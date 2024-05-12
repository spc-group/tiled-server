#!/bin/bash

# run the tiled server

MY_DIR=$(realpath $(dirname $0))
HOST=0.0.0.0
PORT=8001

# export CONDA_BASE=/APSshare/miniconda/x86_64
# source "${CONDA_BASE}/etc/profile.d/conda.sh"

# eval "$(micromamba shell hook --shell=)"
# micromamba activate "${CONDA_ENV}"

tiled serve config \
    --port ${PORT} \
    --host ${HOST} \
    --public \
    "${MY_DIR}/config.yml"
