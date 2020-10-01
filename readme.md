## Running the demo 

Create a virtual environment and install python requirements,

    python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

### Data pre processing

First, we need some example data. In this example, we'll use weather data from [GFS](https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs), but any geospatial raster data can be used. To download some data and convert them to numpy arrays,

    python3 gfs_to_npz.py

Before the data can be loaded by the tile server, it must be converted into [cloud optimized geotiff](https://www.cogeo.org/),

    python3 npz_to_tiff.py

### Tile server

The tiles are served to the map component via a tile server. In this example, [Terracotta](https://github.com/DHI-GRAS/terracotta) is used,

    python3 tc_server.py

### Demo application

With the tile server running, the demo application can now be started,

    python3 app.py

        




