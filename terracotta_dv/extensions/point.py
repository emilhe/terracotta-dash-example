import rasterio
from flask import jsonify
from rasterio import warp

from terracotta import get_settings, get_driver
from terracotta.exceptions import InvalidArgumentsError
from terracotta.server.flask_api import convert_exceptions


def register(server):
    @server.route("/point/<path:keys>/<string:lat>/<string:lng>", methods=["GET"])
    @convert_exceptions
    def point(keys: str, lat: str, lng: str):
        keys = keys.split("/")
        settings = get_settings()
        driver = get_driver(settings.DRIVER_PATH, provider=settings.DRIVER_PROVIDER)
        with driver.connect():
            dataset = get_unique_dataset(driver, keys)
            result = get_point_data(float(lat), float(lng), dataset[1])
        return jsonify(result)


def get_unique_dataset(driver, keys):
    datasets = driver.get_datasets(dict(zip(driver.key_names, keys)))  # keys MUST arrive in correct order
    if len(datasets) == 0:
        raise InvalidArgumentsError("not matches found for specified keys ({})".format(",".join(keys)))
    if len(datasets) > 1:
        matching_keys = [str(item) for item in datasets.keys()]
        raise InvalidArgumentsError("specified keys ({}) must resolve a single dataset, but multiple matches were "
                                    "found ({})".format(",".join(keys), ",".join(matching_keys)))
    return list(datasets.items())[0]


def get_point_data(lat, lng, path):
    with rasterio.open(path) as src_dst:
        # Concert to source CRS.
        x, y = warp.transform("epsg:4326", src_dst.crs, [lng], [lat])
        # Check bounds.
        x_inside = min(src_dst.bounds.left, src_dst.bounds.right) < x[0] < \
                   max(src_dst.bounds.left, src_dst.bounds.right)
        y_inside = min(src_dst.bounds.bottom, src_dst.bounds.top) < y[0] < \
                   max(src_dst.bounds.bottom, src_dst.bounds.top)
        if not (x_inside and y_inside):
            raise InvalidArgumentsError('requested lat lon outside bounds')
        # Sample value.
        return list(src_dst.sample([(x[0], y[0])]))[0].tolist()[0]
