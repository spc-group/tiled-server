# tiled

APS local tiled data server template: databroker catalog

- [tiled](#tiled)
  - [Overview](#overview)
  - [Startup](#startup)
    - [Features](#features)
  - [Additional content served](#additional-content-served)
  - [Links](#links)
  - [Install](#install)
  - [Files](#files)
    - [bluesky.yml](#blueskyyml)

## Overview

Run the *tiled* data server for the local beam line on workstation
`SERVER`.  Since this server provides open access, it is only
accessible within the APS subnet.

## Startup

To start this tiled server (after configuring as described in the
[Install](#install} section), navigate to this directory and run:

```bash
in-screen.sh
```

Then, use any web browser (within the APS firewall) to visit
URL: `http://SERVER:8000`.

The web interface is a simple UI demonstrating many features of
the tiled server and also providing access to online documentation.
Visit the documentation to learn how to build your own interface
to tiled.

### Features

- serve data from Bluesky databroker catalogs
- (optional) serve data from user experiment file directory

## Additional content served

- [x] Identify NeXus/HDF5 files with arbitrary names.
- [x] Identify SPEC data files with arbitrary names and read them.
- [x] Read `.jpg` (and other image format) files.
- [x] Read the [synApps MDA format](https://github.com/epics-modules/sscan/blob/master/documentation/saveData_fileFormat.txt) ([Python support](https://github.com/EPICS-synApps/utils/blob/master/mdaPythonUtils/INSTALL.md))
- [x] Write a custom data file identifier.
- [x] Write a custom data file loader.
- [ ] Authentication
- [x] Learn how to ignore files such as `.xml` (without startup comments).

## Links

- <https://github.com/bluesky/tiled/issues/175>
- <https://blueskyproject.io/tiled/how-to/read-custom-formats.html#case-2-no-file-extension>

## Install

1. Setup and activate a custom micromamba (conda)
   environment as directed
   in [`environment.yml`](./environment.yml). (Do not expect that file needs editing as of 2022-11-23.)

   Note: This step defines a `CONDA_PREFIX` environment variable in the bash shell.  Used below.
2. Copy the template file `config.yml.template` to `config.yml`.
3. Edit tiled's configuration file: [`config.yml`](./config.yml)
   1. `path` is the name seen by the tiled clients.
   2. `tree` should not be changed
   3. for databroker catalogs, `uri` is the address
      of the mongodb catalog for this `path`
   4. for file directories, `directory` is the path to
      the directory.  Either absolute or relative to the
      directory of this README.md file.
3. Edit bash starter shell script file [`start-tiled.sh`](./start-tiled.sh)
   1. Override definition of `MY_DIR` at your choice.
   2. Choose one definition of `CONDA_ENV`.
4. Edit web interface to display additional columns:
   1. In the `$CONDA_PREFIX` directory, edit file
      `share/tiled/ui/config/bluesky.yml` so it has the
      content indicated by the [`bluesky.yml`](#blueskyyml)
      below.
   2. Edit file `share/tiled/ui/configuration_manifest.yml`
      and add a line at the bottom to include the
      `bluesky.yml` file:

      ```yml
        - config/bluesky.yml
      ```

## Files

### bluesky.yml

```yml
specs:
  - spec: CatalogOfBlueskyRuns
    columns:
      - header: Bluesky Plan
        select_metadata: start.plan_name
        field: plan_name
      - header: Scan ID
        select_metadata: start.scan_id
        field: scan_id
      - header: Time
        select_metadata: start.time
        field: start_time
    default_columns:
      - plan_name
      - scan_id
      - start_time
```
