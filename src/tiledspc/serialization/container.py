import io
import logging
from typing import Mapping

import h5py
from tiled.utils import (
    SerializationError,
    ensure_awaitable,
    modules_available,
    safe_json_dump,
)


log = logging.getLogger(__name__)


class NexusFile(h5py.File):
    def __init__(self, *args, filter_for_access, **kwargs):
        self.filter_for_access = filter_for_access
        super().__init__(*args, **kwargs)

    def write_run(self, name, node, metadata: Mapping = {}):
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
        self.attrs["NX_class"] = "NXroot"
        self.attrs["default"] = name
        # Create NXentry
        entry = self.create_group(f"{name}")
        entry.attrs["NX_class"] = "NXentry"
        # Write individual streams
        stream_names = metadata["summary"]["stream_names"]
        for stream_name in stream_names:
            self.write_stream(
                name=stream_name,
                node=node[stream_name],
                parent=entry,
                metadata=metadata,
            )
        default_stream = "primary" if "primary" in stream_names else stream_names[0]
        entry.attrs["default"] = default_stream
        # Write attributes
        return entry

    def write_stream(self, name, node, parent, metadata: Mapping = {}):
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
        # Add individual data columns
        data = node["data"]
        for key, child in data.items():
            arr = self.filter_for_access(child).read()
            try:
                ds = data_group.create_dataset(key, data=arr)
            except TypeError as exc:
                log.exception(exc)
                log.error(f"Could not create dataset for {type(child)} '{key}'.")
                continue
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
        fp.write_run(name=metadata["summary"]["uid"], node=node, metadata=metadata)
        # try:
        #     file.attrs.update(metadata)
        # except TypeError:
        #     raise SerializationError(MSG)
        # async for key_path, array_adapter in walk(node, filter_for_access):
        #     group = file
        #     node = root_node
        #     for key in key_path[:-1]:
        #         if hasattr(node, "lookup_adapter"):
        #             node = await node.lookup_adapter([key])
        #         else:
        #             node = node[key]
        #         if key in group:
        #             group = group[key]
        #         else:
        #             group = group.create_group(key)
        #             try:
        #                 group.attrs.update(node.metadata())
        #             except TypeError:
        #                 raise SerializationError(MSG)
        #     data = await ensure_awaitable(array_adapter.read)
        #     dataset = group.create_dataset(key_path[-1], data=data)
        #     for k, v in array_adapter.metadata().items():
        #         dataset.attrs.create(k, v)
    return buffer.getbuffer()
