# NOTES with new tiled a105

```bash
   tiled catalog init catalog.db
   tiled catalog register catalog.db   --verbose   --ext '.nx5=application/x-hdf5'   --ext '.nexus.hdf5=application/x-hdf5' ./dev_data/hdf5
   tiled serve catalog catalog.db -r ./dev_data/hdf5/ --host 0.0.0.0  --public
```


```bash
    tiled catalog init catalog.db
    PYTHONPATH=. \
        tiled catalog register \
        catalog.db \
        --verbose \
        --ext '.nx5=application/x-hdf5' \
        --ext '.nexus.hdf5=application/x-hdf5' \
        --mimetype-hook 'custom:detect_mimetype' \
        --adapter 'text/spec_data=spec_data:read_spec_data' \
        ./dev_data
    tiled serve catalog catalog.db -r ./dev_data/ --host 0.0.0.0  --public
```
