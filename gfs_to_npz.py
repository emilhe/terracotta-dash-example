import os
import numpy as np
from netCDF4 import Dataset

"""
This script converts GFS weather data from the grib2 format (in which they are published) into numpy arrays,

https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs

The particular data files used in this example can be found here,

https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-003-1.0-degree/forecast/202009/20200901/gfs_3_20200901_0000_000.grb2
https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-003-1.0-degree/forecast/202009/20200901/gfs_3_20200901_0000_000.grb2.inv

"""

src = "data/gfs_3_20200901_0000_000"
# Convert wgrid2 to nc.
params = ["VGRD:100 m above ground", "UGRD:100 m above ground", "TMP:2 m above ground"]
cmd = f"wgrib2 {src}.grb2 -s | egrep '(:{':|:'.join(params)}:)'|wgrib2 -i {src}.grb2 -netcdf {src}.nc"
os.system(cmd)
# Convert nc to numpy arrays.
rootgrp = Dataset(f"{src}.nc", "r")
lon = rootgrp['longitude'][:]
lat = rootgrp['latitude'][:]
ugrd = rootgrp['UGRD_100maboveground'][:][0]
vgrd = rootgrp['VGRD_100maboveground'][:][0]
wspd = (ugrd**2 + vgrd**2)**0.5
temp = rootgrp['TMP_2maboveground'][:][0]
np.savez(f"{src}.npz", lat=lat, lon=lon, wspd=wspd, temp=temp)
