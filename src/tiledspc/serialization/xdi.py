import datetime as dt
import logging
import io
import asyncio
from collections.abc import Mapping

import pandas as pd
from tiled.utils import ensure_awaitable
from tiled.catalog.adapter import CatalogNodeAdapter


__all__ = ["serialize_xdi"]


log = logging.getLogger(__name__)


def headers(metadata: Mapping[str, Mapping], data_keys: Mapping[str, Mapping], d_spacing: str):
    """Generate individual header lines for the XDI file."""
    # Version information
    versions = ["XDI/1.0"]
    start_doc = metadata.get("start", {})
    version_md = start_doc.get("versions", {})
    versions += [f"{name}/{ver}" for name, ver in version_md.items()]
    # fd.write(f"# {' '.join(versions)}\n")
    yield f"# {' '.join(versions)}"
    # Column Names
    for num, (key, info) in enumerate(data_keys.items()):
        yield f"# Column.{num+1}: {key} {info.get('units', '')}"
    # X-ray edge information
    edge_str = start_doc.get("edge", None)
    try:
        elem, edge = edge_str.split("_")
    except (AttributeError, ValueError):
        msg = f"Could not parse X-ray edge metadata: {edge_str}"
        log.debug(msg)
    else:
        yield f"# Element.symbol: {elem}"
        yield f"# Element.edge: {edge}"
    yield f"# Mono.d_spacing: {d_spacing}"
    # Facility information
    start_time = dt.datetime.fromtimestamp(start_doc['time'], dt.timezone.utc)
    start_time = start_time.astimezone()
    yield f"# Scan.start_time: {start_time.strftime('%Y-%m-%d %H:%M:%S%z')}"
    md_mappings = [
        # metadata key, XDI key
        ("facility_id", "Facility.name"),
        ("beamline_id", "Beamline.name"),
        ("uid", "uid"),
    ]
    md_mappings = [key for key in md_mappings if key[0] in start_doc]
    for md_key, xdi_key in md_mappings:
        yield f"# {xdi_key}: {start_doc[md_key]}"
    # Header end token
    yield "# -------------"


def data_keys(metadata: Mapping[str, Mapping | str | float | int]):
    """Prepare valid hinted data keys for a stream.

    *metadata* should be the metadata dictionary for a specific stream.

    """
    dkeys = metadata['data_keys']
    hints = metadata["hints"]
    hints = [hint for dev_hints in hints.values() for hint in dev_hints['fields']]
    dkeys = {key: desc for key, desc in dkeys.items() if key in hints}
    return dkeys


async def load_datasets(node: CatalogNodeAdapter) -> tuple[CatalogNodeAdapter, CatalogNodeAdapter, CatalogNodeAdapter]:
    """Decide which datasets to plot.

    Returns
    =======
    stream_node
      The node for the ("primary" by default) data stream.
    internal_node
      The node for the internal data frame.
    config_node
      The node for the internal config data frame.
    """
    items = {key: node for key, node in await node.items_range(0, None)}
    stream_node = items['primary']
    stream_items = {key: node for key, node in await stream_node.items_range(0, None)}
    internal_items = {key: node for key, node in await stream_items['internal'].items_range(0, None)}
    config_items = {key: node for key, node in await stream_items['config'].items_range(0, None)}
    return stream_node, internal_items['events'], config_items['energy']



async def serialize_xdi(node, metadata, filter_for_access):
    """Write a bluesky run in XDI format.

    Assumes that *node* is a BlueskyRun.

    Follows the XDI spectroscopy definition."

    """
    stream_node, data_node, config_node = await load_datasets(node)
    data_keys_ = data_keys(stream_node.metadata())
    # Get extra data
    data, energy_config = await asyncio.gather(
        data_node.read(),
        config_node.read(),
    )
    d_spacing = energy_config['energy-monochromator-d_spacing'].values[0]
    # Write headers
    xdi_text = ""
    hdrs = headers(metadata, data_keys=data_keys_, d_spacing=f"{d_spacing}")
    xdi_text += "\n".join(hdrs) + "\n"
    # Write data
    xdi_text += f"# {'\t'.join(data_keys_.keys())}\n"
    buffer = io.StringIO()
    data.to_csv(buffer, sep="\t", header=False, columns=data_keys_.keys(), index=False)
    buffer.seek(0)
    xdi_text += buffer.read()
    return xdi_text.encode("utf-8")
