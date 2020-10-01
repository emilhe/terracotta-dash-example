import os
import urllib.request
import numpy as np

from netCDF4 import Dataset
from config import DATA_DIR, GFS_KEY, PARAM_MAPPINGS, PARAMS_GFS

"""
This script download GFS weather data and converts them from grib2 (in which they are published) into numpy arrays.
"""

src = os.path.join(DATA_DIR, GFS_KEY)

# Download data.
base_url = "https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-003-1.0-degree/forecast/"
urllib.request.urlretrieve(f"{base_url}/202009/20200901/{GFS_KEY}.grb2.inv", f"{src}.grb2.inv")
urllib.request.urlretrieve(f"{base_url}/202009/20200901/{GFS_KEY}.grb2", f"{src}.grb2")
# Convert wgrid2 to nc.
cmd = f"wgrib2 {src}.grb2 -s | egrep '(:{':|:'.join(PARAMS_GFS)}:)'|wgrib2 -i {src}.grb2 -netcdf {src}.nc"
os.system(cmd)
# Convert nc to numpy arrays.
ds = Dataset(f"{src}.nc", "r")
lon = ds['longitude'][:]
lat = ds['latitude'][:]
params = {param: PARAM_MAPPINGS[param](ds) for param in PARAM_MAPPINGS}
np.savez(f"{src}.npz", lat=lat, lon=lon, **params)
