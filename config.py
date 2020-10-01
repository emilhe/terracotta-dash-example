# Paths.
GEOTIFF_DIR = "data"
DATA_DIR = "data"
DRIVER_PATH = "data/db.sqlite"
# Server config.
TC_PORT = 5000
TC_HOST = "localhost"
TC_URL = f"http://{TC_HOST}:{TC_PORT}"
# Data stuff.
GFS_KEY = "gfs_3_20200901_0000_000"
PARAMS = ["wspd", "temp"]
PARAMS_GFS = ["VGRD:100 m above ground", "UGRD:100 m above ground", "TMP:2 m above ground"]
PARAM_MAPPINGS = dict(
    wspd=lambda ds: (ds['UGRD_100maboveground'][:][0]**2 + ds['VGRD_100maboveground'][:][0]**2)**0.5,
    temp=lambda ds: ds['TMP_2maboveground'][:][0]
)
