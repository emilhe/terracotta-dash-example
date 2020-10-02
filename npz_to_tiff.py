import os
import numpy as np

from terracotta_toolbelt import latlon_to_xy, setup_grid, interpolate_onto_grid, raster_to_cog
from config import DATA_DIR, GFS_KEY, PARAMS

"""
This script converts numpy arrays of (lat, lon, values) into cloud optimized geotiff files.
"""

os.makedirs(DATA_DIR, exist_ok=True)
src = os.path.join(DATA_DIR, GFS_KEY)
# Read numpy array.
data = np.load(f"{src}.npz")
lat, lon, rasters = data["lat"], data["lon"], [data[param] for param in PARAMS]
# Interpolate onto a regular grid in EPSG:3857.
xy_vec, rasters = latlon_to_xy(lat, lon, rasters=rasters)
dxdy = 25000
xmin, ymin, xmax, ymax = -20037500, -20037500, 20037500, 20037500  # approx world bounds
mx, my, bounds, transform = setup_grid(xmin, ymin, xmax, ymax, dxdy)
rasters = interpolate_onto_grid(xy_vec, rasters, mx, my)
# Convert to cog.
for i, raster in enumerate(rasters):
    raster_to_cog(raster, transform, f"{src}.{PARAMS[i]}.tiff")
