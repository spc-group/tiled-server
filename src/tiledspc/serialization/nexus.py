import io
import logging
from typing import Mapping

import h5py
from tiled.catalog.adapter import CatalogContainerAdapter
from tiled.utils import (
    ensure_awaitable,
)

log = logging.getLogger(__name__)


async def asdict(node):
    """Convert a catalog node to a dictionary."""
    return {key: val for key, val in await node.items_range(0, None)}


class NexusFile(h5py.File):
    def __init__(self, *args, filter_for_access, **kwargs):
        self.filter_for_access = filter_for_access
        super().__init__(*args, **kwargs)

    async def write_baseline(self, *args, **kwargs):
        return

    async def write_run(self, node: CatalogContainerAdapter, metadata: Mapping[str, Mapping | float | str | int]):
        """Write a run to the HDF file as a nexus-compatiable entry.

        *node* should be the container for this run. E.g.

        .. code-block:: python

            uid = "7d1daf1d-60c7-4aa7-a668-d1cd97e5335f"
            write_stream(name=uid, node=client[uid])

        Returns
        =======
        grp
          The HDF5 :NXentry group used to hold this run's data.

        """
        name = metadata['start']['uid']
        self.attrs["NX_class"] = "NXroot"
        self.attrs["default"] = name
        # Create NXentry
        entry = self.create_group(f"{name}")
        entry.attrs["NX_class"] = "NXentry"
        # Write individual streams
        stream_names = []
        for stream_name, stream_node in await node.items_range(0, None):
            if stream_name == "baseline":
                await self.write_baseline(
                    stream_node
                )
            else:
                stream_names.append(stream_name)
                await self.write_stream(
                    name=stream_name,
                    node=stream_node,
                    parent=entry,
                    metadata=metadata,
                )
        default_stream = "primary" if "primary" in stream_names else stream_names[0]
        entry.attrs["default"] = default_stream
        # Write attributes
        return entry

    async def write_stream(self, name, node, parent, metadata: Mapping = {}):
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
        metatata
          The Bluesky metadata for this run.

        Returns
        =======
        grp
          The HDF5 group used to hold this stream's data.

        """
        data_group = parent.create_group(name)
        data_group.attrs["NX_class"] = "NXdata"
        # Make sure we have access to these data
        from pprint import pprint
        containers = await asdict(node)
        internal = await asdict(containers['internal'])
        events = await internal['events'].read()
        # Add individual data columns
        for col_name, series in events.items():
            arr = series.values
            # Create the data set for the new data column
            ds = data_group.create_dataset(col_name, data=arr)
            ds.attrs["NX_class"] = "NXdata"
        return data_group


async def serialize_nexus(node, metadata, filter_for_access):
    """Encode everything below this node as HDF5.

    Assumes that *node* is a BlueskyRun.

    Follows the NeXuS XAS spectroscopy definition."

    """
    buffer = io.BytesIO()
    root_node = node
    # MSG = "Metadata contains types or structure that does not fit into HDF5."
    with NexusFile(buffer, mode="w", filter_for_access=filter_for_access) as fp:
        # Write data entry to the nexus file
        await fp.write_run(
            node=node, metadata=metadata
        )
    return buffer.getbuffer()
