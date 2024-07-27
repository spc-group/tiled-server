#!/usr/bin/env sh

# Set these to be the lists of data directories to be indexed
data_dirs=(
    "/net/s25data/export/25-ID-C"
    "/net/s25data/export/25-ID-D"
    "/net/s20data/export/sector20/BMData"
    "/net/s20data/export/sector20/IDData"
    "/net/s9data/export/9bm/BMData"
)
# Set these to be the lists of sqlite catalogs generated with ``tiled catalog init``
catalogs=(
    "/local/tiled_server/catalog_25idc.db"
    "/local/tiled_server/catalog_25idd.db"
    "/local/tiled_server/catalog_20bm.db"
    "/local/tiled_server/catalog_20id.db"
    "/local/tiled_server/catalog_9bm.db"
)


# Update our environment to find python modules
THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
NEW_PYTHONPATH=${THIS_DIR}:${PYTHONPATH}


function register_catalog {
    # Runs a tiled job to register all the files in a directory
    # $1 is the catalog
    local catalog=$1
    # $2 is the data directory
    local data_dir=$2
    # Execute the tiled command
    PYTHONPATH=${NEW_PYTHONPATH} \
	      tiled catalog register \
	      ${catalog} \
	      --verbose \
	      --watch \
	      --ext '.avif=image/avif' \
	      --ext '.dat=text/x-spec_data' \
	      --ext '.docx=application/octet-stream' \
	      --ext '.DS_Store=text/plain' \
	      --ext '.h5=application/x-hdf5' \
	      --ext '.hdf=application/x-hdf5' \
	      --ext '.mda=application/x-mda' \
	      --ext '.nexus.hdf5=application/x-hdf5' \
	      --ext '.nx5=application/x-hdf5' \
	      --ext '.pptx=application/octet-stream' \
	      --ext '.pyc=application/octet-stream' \
	      --ext '.webp=image/webp' \
	      --keep-ext \
	      --mimetype-hook 'custom:detect_mimetype' \
	      --adapter 'application/json=ignore_data:read_ignore' \
	      --adapter 'application/octet-stream=ignore_data:read_ignore' \
	      --adapter 'application/x-mda=synApps_mda:read_mda' \
	      --adapter 'application/xop+xml=ignore_data:read_ignore' \
	      --adapter 'application/zip=ignore_data:read_ignore' \
	      --adapter 'image/avif=ignore_data:read_ignore' \
	      --adapter 'image/bmp=image_data:read_image' \
	      --adapter 'image/gif=image_data:read_image' \
	      --adapter 'image/jpeg=image_data:read_image' \
	      --adapter 'image/png=image_data:read_image' \
	      --adapter 'image/svg+xml=ignore_data:read_ignore' \
	      --adapter 'image/tiff=image_data:read_image' \
	      --adapter 'image/vnd.microsoft.icon=image_data:read_image' \
	      --adapter 'image/webp=image_data:read_image' \
	      --adapter 'image/x-ms-bmp=image_data:read_image' \
	      --adapter 'text/markdown=ignore_data:read_ignore' \
	      --adapter 'text/plain=ignore_data:read_ignore' \
	      --adapter 'text/x-python=ignore_data:read_ignore' \
	      --adapter 'text/x-spec_data=spec_data:read_spec_data' \
	      --adapter 'text/xml=ignore_data:read_ignore' \
	      ${data_dir}
}


for idx in "${!data_dirs[@]}"; do
# Run each catalog registration client in the background
echo "Starting registration for catalog ${catalogs[idx]} in ${data_dirs[idx]}"
register_catalog ${catalogs[idx]} ${data_dirs[idx]} &
done

# Wait for all the catalog registration clients to finish
wait
