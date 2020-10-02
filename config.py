# Paths.
GEOTIFF_DIR = "data"
DATA_DIR = "data"
DRIVER_PATH = "data/db.sqlite"
# Server config.
TC_PORT = 5000
TC_HOST = "localhost"
TC_URL = f"http://{TC_HOST}:{TC_PORT}"
# Data stuff.
GFS_YEAR, GFS_MONTH, GFS_DAY, GFS_HOUR, GFS_FCST_HOUR = "2020", "01", "01", "000", "0000"
GFS_KEY = f"gfs_4_{GFS_YEAR}{GFS_MONTH}{GFS_DAY}_{GFS_FCST_HOUR}_{GFS_HOUR}"
PARAMS = ["wspd", "temp"]
PARAMS_GFS = ["VGRD:100 m above ground", "UGRD:100 m above ground", "TMP:2 m above ground"]
PARAM_MAPPINGS = dict(
    wspd=lambda ds: (ds['UGRD_100maboveground'][:][0]**2 + ds['VGRD_100maboveground'][:][0]**2)**0.5,
    temp=lambda ds: ds['TMP_2maboveground'][:][0]
)
