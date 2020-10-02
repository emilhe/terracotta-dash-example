The repository hold a small example of a Python stack that enables visualization of geospatial raster data. It consists of three main elements,

1) Pre processing scripts that converts wrib2 files / numpy arrays into [cloud optimized geotiff](https://www.cogeo.org/) (COG)
2) A script that launches a [Terracotta](https://github.com/DHI-GRAS/terracotta) tile server to serve the geotiff files
3) A demo application written in [Dash](https://plotly.com/dash/) that visualizes the data using the [dash-leaflet](https://github.com/thedirtyfew/dash-leaflet) library

In addition to visualizing the data on the map, the example also demonstrates how to sample data from the underlying raster. Special care has been taken to ensure a 1:1 correspondence between the values shown on the map, and the sampled valued. 

### Running the demo 

Create a virtual environment and install python requirements,

    python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

Next, we need some example data. In this example, we'll use weather data from [GFS](https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs), but any geospatial raster data would do. A small script is included that fetches data for the 1st of January 2020 and converts them to numpy arrays,

    python3 gfs_to_npz.py

Before the data can be loaded by the tile server, it must be converted into COG. Simply run,

    python3 npz_to_tiff.py
    
The tiles are served to the map component via a tile server. In this example, [Terracotta](https://github.com/DHI-GRAS/terracotta) is used. To start it, run

    python3 tc_server.py

With the tile server running, the demo application can now be started,

    python3 app.py

If you open and browser and go `http://localhost:8050`, the map visualization should appear.

### Can i visualize my own data? 

It should be more-or-less straight forward to visualize custom data, you just need to setup a pipeline to convert them into COG. The `npz_to_tiff.py`, which takes simple numpy arrays as input, should be a good starting point.

### What about production?

Both [Terracotta](https://github.com/DHI-GRAS/terracotta) and [Dash](https://plotly.com/dash/) are based on [Flask](https://flask.palletsprojects.com/en/1.1.x/). In production, a proper web server (such a [gunicorn](https://gunicorn.org/)) should be used.

### How did you achieve WYSIWYG pixel drilling?

To ensure a 1:1 correspondence between the values shown on the map, and the sampled valued, a few step are necessary.

* The data must be interpolated onto a grid that is regular in the coordinates system in which the data is viewed. In most web based maps (including this example), `epsg:3857` is used. This task is performed by the `interpolate_onto_grid` function.

* The pixels of the data grid must be aligned with map tiles. This is ensured by passing `web_optimized=True` to the `cog_translate` function. 

* The tile server cannot perform any post processing (e.g. interpolation) of the data. With Terracotta, this is achieved via the settings `RESAMPLING_METHOD="nearest"` and `REPROJECTION_METHOD="nearest"`.
