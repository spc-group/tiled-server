#!/bin/bash

# run the tiled server in a screen session
# SESSION_NAME=tiled_server
SESSION_NAME=tiled_server_issue2
N_LINES=5000

screen \
    -dm \
    -S "${SESSION_NAME}" \
    -h "${N_LINES}" \
    ./start-tiled.sh
