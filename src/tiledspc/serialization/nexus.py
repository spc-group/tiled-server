import json
import datetime as dt
import io
import logging
from typing import Mapping, IO

import numpy as np
import h5py
from tiled.catalog.adapter import CatalogContainerAdapter
from tiled.utils import (
    ensure_awaitable,
)
from nexusformat.nexus import nxopen, NXFile
from nexusformat.nexus.tree import NXentry, NXinstrument, NXnote, NXdata, NXfield, NXroot

log = logging.getLogger(__name__)


async def asdict(node):
    """Convert a catalog node to a dictionary."""
    return {key: val for key, val in await node.items_range(0, None)}


class NexusIO(NXFile):
    def __init__(self, bytesio: IO[bytes], mode: str='r', **kwargs):
        self.h5 = h5py
        self.name = ""
        self._file = None
        self._filename = "/dev/null"
        self._filedir = "/tmp"
        self._lock = None
        self._lockdir = None
        self._path = '/'
        self._root = None
        self._with_count = 0
        self.recursive = True

        self._file = self.h5.File(bytesio, mode, **kwargs)

        if mode == 'r':
            self._mode = 'r'
        else:
            self._mode = 'rw'

    def acquire_lock(self, timeout=None):
        pass

    def release_lock(self, timeout=None):
        pass

    def open(self, **kw):
        pass


async def write_run(nxfile: NexusIO, node: CatalogContainerAdapter, metadata: Mapping[str, Mapping | float | str | int]) -> NXroot:
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
    name = metadata['start']['uid']
    root = nxfile.readfile()
    root.attrs['default'] = name
    nxentry = NXentry()
    root[name] = nxentry
    # Create bluesky groups
    nxentry["instrument"] = NXinstrument()
    nxentry['instrument/bluesky'] = NXnote()
    bluesky_group = nxentry['instrument/bluesky']
    bluesky_group["streams"] = NXnote()
    # Write stream data
    await write_metadata(metadata, nxentry=nxentry)
    for stream_name, stream_node in await node.items_range(0, None):
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
        (Mapping, json.dumps),
    ]
    new_types = [new for old, new in type_conversions if isinstance(value, old)]
    new_type = [*new_types, lambda x: x][0]
    return new_type(value)


async def write_metadata(metadata: dict[str], nxentry: NXentry):
    """Write run-level metadata to the Nexus file."""
    md_group = NXnote()
    nxentry['instrument/bluesky/metadata'] = md_group
    flattened = {f"{doc_name}.{key}": value for doc_name, doc in metadata.items() for key, value in doc.items()}
    for key, value in flattened.items():
        value = to_hdf_type(value)
        md_group[key] = NXfield(value)


async def write_stream(name: str, node, nxentry: NXentry, metadata: Mapping[str, dict] = {}):
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
    stream_group = NXnote()
    nxentry[f"instrument/bluesky/streams/{name}"] = stream_group
    # Make sure we have access to these data
    containers = await asdict(node)
    internal = await asdict(containers['internal'])
    events = await internal['events'].read()
    external = await asdict(containers['external'])
    # Add individual data columns
    for col_name, desc in metadata['data_keys'].items():
        nxdata = NXdata()
        stream_group[col_name] = nxdata
        if "external" in desc:
            # Load and save external dataset from disk
            data = await external[col_name].read()
            nxdata['value'] = NXfield(data)
        else:
            # Save interal dataset
            nxdata["value"] = NXfield(events[col_name].values)
            nxdata['value'].attrs['units'] = desc['units']
            times = events[f"ts_{col_name}"].values
            nxdata["EPOCH"] = NXfield(times)
            nxdata["time"] = times - np.min(times)
            nxdata['time'].attrs['units'] = 's'
            nxdata.attrs['signal'] = "value"
            nxdata.attrs['axes'] = "time"
    return stream_group


async def serialize_nexus(node, metadata, filter_for_access):
    """Encode everything below this node as HDF5.

    Assumes that *node* is a BlueskyRun.

    Follows the NeXuS XAS spectroscopy definition."

    """
    buff = io.BytesIO()
    root_node = node
    # MSG = "Metadata contains types or structure that does not fit into HDF5."
    
    with NexusIO(buff, mode='w') as nxfile:
        # Write data entry to the nexus file
        tree = await write_run(
            nxfile=nxfile,
            node=node,
            metadata=metadata
        )
        nxfile.writefile(tree)
        nxfile.close()
    return buff.getbuffer()
