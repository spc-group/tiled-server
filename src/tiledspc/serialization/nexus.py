import datetime as dt
import io
import json
import logging
from typing import IO, Mapping

import h5py
import numpy as np
from nexusformat.nexus import NeXusError, NXFile
from nexusformat.nexus.tree import (
    NXdata,
    NXentry,
    NXfield,
    NXinstrument,
    NXlinkfield,
    NXnote,
    NXroot,
)
from tiled.catalog.adapter import CatalogContainerAdapter
from tiled.utils import SerializationError

log = logging.getLogger(__name__)


async def asdict(node):
    """Convert a catalog node to a dictionary."""
    return {key: val for key, val in await node.items_range(0, None)}


class NexusIO(NXFile):
    def __init__(self, bytesio: IO[bytes], mode: str = "r", **kwargs):
        self.h5 = h5py
        self.name = ""
        self._file = None
        self._filename = "/dev/null"
        self._filedir = "/tmp"
        self._lock = None
        self._lockdir = None
        self._path = "/"
        self._root = None
        self._with_count = 0
        self.recursive = True

        self._file = self.h5.File(bytesio, mode, **kwargs)

        if mode == "r":
            self._mode = "r"
        else:
            self._mode = "rw"

    def acquire_lock(self, timeout=None):
        pass

    def release_lock(self, timeout=None):
        pass

    def open(self, **kw):
        pass


async def write_run(
    nxfile: NexusIO,
    node: CatalogContainerAdapter,
    metadata: Mapping[str, Mapping | float | str | int],
) -> NXroot:
    """Write a run to the HDF file as a nexus-compatiable entry.

    *node* should be the container for this run. E.g.

    .. code-block:: python

        uid = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
        write_stream(name=uid, node=client[uid])

    Returns
    =======
    root
      The HDF5 :NXentry group used to hold this run's data.

    """
    name = metadata["start"]["uid"]
    root = nxfile.readfile()
    root.attrs["default"] = name
    nxentry = NXentry()
    root[name] = nxentry
    # Create bluesky groups
    nxentry["data"] = NXdata(date=None)
    nxentry["instrument"] = NXinstrument()
    nxentry["instrument/bluesky"] = NXnote(date=None)
    bluesky_group = nxentry["instrument/bluesky"]
    bluesky_group["streams"] = NXnote(date=None)
    # Write stream data
    await write_metadata(metadata, nxentry=nxentry)
    streams = (await asdict(node))["streams"]
    for stream_name, stream_node in await streams.items_range(0, None):
        await write_stream(
            name=stream_name,
            node=stream_node,
            nxentry=nxentry,
            metadata=stream_node.metadata(),
        )
    # Write attributes
    return root


def to_hdf_type(value):
    """Some objects cannot be stored as HDF5 types.

    For example, a datetime should be converted to a string.

    Complex structures, like dictionaries, are converted to JSON.

    """
    type_conversions = [
        # (old => new)
        (dt.datetime, str),
        (dict, json.dumps),
        (list, json.dumps),
    ]
    new_types = [new for old, new in type_conversions if isinstance(value, old)]
    new_type = [*new_types, lambda x: x][0]
    return new_type(value)


async def write_metadata(metadata: dict[str], nxentry: NXentry):
    """Write run-level metadata to the Nexus file."""
    bluesky_group = nxentry["instrument/bluesky"]
    md_group = NXnote(date=None)
    bluesky_group["metadata"] = md_group
    flattened = {
        f"{doc_name}.{key}": value
        for doc_name, doc in metadata.items()
        for key, value in doc.items()
    }
    for key, value in flattened.items():
        value = to_hdf_type(value)
        md_group[key] = NXfield(value)
    # Create additional convenient links
    if "start.sample_name" in md_group.keys():
        nxentry["sample_name"] = NXlinkfield(md_group["start.sample_name"])
    if "start.scan_name" in md_group.keys():
        nxentry["scan_name"] = NXlinkfield(md_group["start.scan_name"])
    if "start.plan_name" in md_group.keys():
        nxentry["plan_name"] = NXlinkfield(md_group["start.plan_name"])
        bluesky_group["plan_name"] = NXlinkfield(md_group["start.plan_name"])
    if "start.uid" in md_group.keys():
        bluesky_group["uid"] = NXlinkfield(md_group["start.uid"])
        nxentry["entry_identifier"] = NXlinkfield(md_group["start.uid"])
    for phase in ["start", "stop"]:
        if f"{phase}.time" in flattened.keys():
            timestamp = dt.datetime.fromtimestamp(flattened[f"{phase}.time"])
            nxentry[f"{phase}_time"] = NXfield(timestamp.astimezone().isoformat())
    if "start.time" in flattened.keys() and "stop.time" in flattened.keys():
        nxentry["duration"] = NXfield(flattened["stop.time"] - flattened["start.time"])


async def write_stream(
    name: str, node, nxentry: NXentry, metadata: Mapping[str, dict] = {}
):
    """Write a stream to the HDF file as a nexus-compatiable entry.

    *node* should be the container for this stream. E.g.

    .. code-block:: python

        write_stream(name="primary", node=run["primary"])

    Parameters
    ==========
    name
      The name for the new HDF5 NXdata group.
    node
      The tiled container for this stream.
    parent
      The HDF5 group/file to add this stream's group to.
    metadata
      Descriptions of the individual datasets to create and hint.

    Returns
    =======
    grp
      The HDF5 group used to hold this stream's data.

    """
    stream_group = NXnote(date=None)
    nxentry[f"instrument/bluesky/streams/{name}"] = stream_group
    # Make sure we have access to these data
    stream = await asdict(node)
    try:
        internal = await stream["internal"].read()
    except KeyError:
        # We don't have an internal dataset for some reason
        internal = None
    for col_name, desc in metadata["data_keys"].items():
        nxdata = NXdata()
        stream_group[col_name] = nxdata
        if "external" in desc:
            # Load and save external dataset from disk
            data = await stream[col_name].read()
            nxdata["value"] = NXfield(data)
        else:
            # Save internal dataset
            try:
                nxdata["value"] = NXfield(internal[col_name].values)
            except KeyError:
                raise SerializationError(
                    f"Could not find internal dataset '{col_name}'"
                )
            if "units" in desc.keys():
                nxdata["value"].attrs["units"] = desc["units"]
            nxdata.attrs["signal"] = "value"
            try:
                times = internal[f"ts_{col_name}"].values
            except KeyError:
                log.error(
                    f"Could not find timestamps for internal dataset '{col_name}'"
                )
            else:
                nxdata["EPOCH"] = NXfield(times)
                nxdata["time"] = times - np.min(times)
                nxdata["time"].attrs["units"] = "s"
                nxdata.attrs["axes"] = "time"
    # Add links to the main NXdata group
    if name == "baseline":
        # We don't want to see baseline fields in the data NXdata group
        stream_hints = {}
    else:
        stream_hints = metadata.get("hints", {})
    root_nxdata = nxentry["data"]
    for device, hints in stream_hints.items():
        for field in hints.get("fields", []):
            # Make sure the field name is not already used in another stream
            link_name = field if field not in root_nxdata.keys() else f"field_{name}"
            # Write the link
            try:
                root_nxdata[link_name] = NXlinkfield(stream_group[field]["value"])
            except NeXusError:
                raise SerializationError(
                    f"Could not link hinted '{name}' field: '{field}'"
                )
    return stream_group


async def serialize_nexus(node, metadata, filter_for_access):
    """Encode everything below this node as HDF5.

    Assumes that *node* is a BlueskyRun.

    Follows the NeXuS XAS spectroscopy definition."

    """
    buff = io.BytesIO()
    root_node = node
    # MSG = "Metadata contains types or structure that does not fit into HDF5."

    with NexusIO(buff, mode="w") as nxfile:
        # Write data entry to the nexus file
        tree = await write_run(nxfile=nxfile, node=node, metadata=metadata)
        nxfile.writefile(tree)
        nxfile.close()
    return buff.getbuffer()
