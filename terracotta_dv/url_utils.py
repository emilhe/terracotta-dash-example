def singleband_url(api_url, keys, **kwargs):
    base_url = f"{api_url}/singleband/{'/'.join(keys)}/{{z}}/{{x}}/{{y}}.png"
    if not kwargs:
        return base_url
    kwstr = "&".join([f"{key}={kwargs[key]}" for key in kwargs])
    return f"{base_url}?{kwstr}"


def point_url(api_url, keys, lat, lon):
    lat_lon_str = "{:.4f}/{:.4f}".format(lat, lon)
    return f"{api_url}/point/{'/'.join(keys)}/{lat_lon_str}"
