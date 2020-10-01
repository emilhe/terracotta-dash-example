import os
import tempfile
import numpy as np
import rasterio

from pyproj import Transformer
from rasterio import MemoryFile
from rasterio.transform import Affine
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from scipy.interpolate import NearestNDInterpolator
from scipy.interpolate.interpnd import LinearNDInterpolator


def raster_to_cog(raster, transform, dst_path, block_size=None, nodata=None):
    block_size = 256 if block_size is None else block_size
    nrows, ncols = np.shape(raster)
    # Source profile.
    src_profile = dict(
        driver='GTiff',
        height=nrows,
        width=ncols,
        count=1,
        dtype=raster.dtype,  # if data_type is None else data_type,
        crs='EPSG:3857',
        transform=transform,
        nodata=np.nan if nodata is None else nodata,
    )
    # Write data.
    with MemoryFile() as memfile:
        with memfile.open(**src_profile) as mem:
            # Write raster to mem file.
            mem.write(raster, 1)
            # Copy to disk.
            dst_profile = cog_profiles.get("raw")
            dst_profile["blockxsize"] = block_size
            dst_profile["blockysize"] = block_size
            cog_translate(
                mem,
                dst_path,
                dst_profile,
                in_memory=True,
                quiet=True,
                web_optimized=True
            )


def setup_grid(xmin, ymin, xmax, ymax, resolution):
    # First, setup the non-optimized grid.
    x = np.arange(xmin, xmax - resolution, resolution)
    y = np.arange(ymin, ymax - resolution, resolution)
    mx, my = np.meshgrid(x, y)
    # Then, write it to a tmp file.
    temp_path = os.path.join(tempfile.gettempdir(), "grid.tiff")
    raster = mx.astype(np.float32)
    transform = Affine.translation(xmin, ymin) * Affine.scale(resolution, resolution)
    raster_to_cog(raster, transform, temp_path)
    # Read it again.
    with rasterio.open(temp_path, 'r') as r:
        new_transform = r.transform
        new_bounds = r.bounds
    # Prepare the grid.
    x = np.arange(new_bounds[0], new_bounds[2], new_transform.a)
    y = np.arange(new_bounds[3], new_bounds[1], new_transform.e)
    mx, my = np.meshgrid(x, y)

    return mx, my, new_bounds, new_transform


def latlon_to_xy(lat, lon, drop_non_finite=True, rasters=None):
    lonlat_to_mercator = Transformer.from_crs('epsg:4326', 'epsg:3857', always_xy=True)
    mlon, mlat = np.meshgrid(lon, lat)
    lonlat_vec = np.column_stack((mlon.flatten(), mlat.flatten()))
    xy_vec = np.array(list(lonlat_to_mercator.itransform(lonlat_vec)))
    # Drop nan values.
    if drop_non_finite:
        flr = np.logical_and(np.isfinite(xy_vec[:, 0]), np.isfinite(xy_vec[:, 1]))
        xy_vec = xy_vec[flr]
        if rasters:
            new_rasters = []
            for i, raster in enumerate(rasters):
                new_rasters.append(raster.flatten()[flr])
            return xy_vec, new_rasters
    return xy_vec


def interpolate_onto_grid(xy_vec, rasters, mx, my):
    # Do the interpolation.
    lndi, nndi = None, None
    new_rasters = []
    for raster in rasters:
        if lndi is None:
            lndi = LinearNDInterpolator(xy_vec, raster)
            nndi = NearestNDInterpolator(xy_vec, raster)
        else:
            lndi = LinearNDInterpolator(lndi.tri, raster)
            nndi.values = raster
        new_raster = lndi(mx, my)
        new_raster[np.isnan(new_raster)] = nndi(mx[np.isnan(new_raster)], my[np.isnan(new_raster)])
        new_rasters.append(new_raster)
    return new_rasters

