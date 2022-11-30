#!/bin/bash

# run the tiled server

MY_DIR=$(realpath $(dirname $0))
CONDA_ENV=tiled
LOG_FILE="${MY_DIR}/logfile.txt"

export CONDA_BASE=/APSshare/miniconda/x86_64
source "${CONDA_BASE}/etc/profile.d/conda.sh"

# eval "$(micromamba shell hook --shell=)"
conda activate "${CONDA_ENV}"

tiled serve config --public --host 0.0.0.0 "${MY_DIR}/config.yml" 2>&1 | tee "${LOG_FILE}"
