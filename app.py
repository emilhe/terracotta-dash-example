import json
import urllib.request
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_leaflet as dl

from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
from flask import Flask
from config import TC_URL, GFS_KEY, PARAMS
from terracotta_dv.url_utils import singleband_url, point_url

cmaps = ["Viridis", "Spectral", "Greys"]
lbl_map = dict(wspd="Wind speed", temp="Temperature")
unit_map = dict(wspd="m/s", temp="°K")
srng_map = dict(wspd=[0, 10], temp=[250, 300])
# App Stuff.
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
# Create the map itself.
app.layout = html.Div(children=[
    dl.Map(id="map", center=[56, 10], zoom=7, children=[
        dl.TileLayer(),
        dl.TileLayer(id="tc", opacity=0.5),
        dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
    ], style={"width": "100%", "height": "100%"}),
    html.Div(children=[
        html.Div("Parameter"),
        dcc.Dropdown(id="dd_param", options=[dict(value=item, label=lbl_map[item]) for item in PARAMS], value="temp"),
        html.Br(),
        html.Div("Colorbar"),
        dcc.Dropdown(id="dd_cmap", options=[dict(value=item, label=item) for item in cmaps], value="Viridis"),
        html.Br(),
        html.Div("Opacity"),
        dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1),
        html.Div("Value @ click position"),
        html.P(children="-", id="text"),
    ], className="info")
], style={"display": "grid", "width": "100%", "height": "100vh"})


@app.callback(Output("tc", "opacity"), [Input("opacity", "value")])
def update_opacity(opacity):
    return opacity


@app.callback([Output("tc", "url"),
               Output("cbar", "colorscale"), Output("cbar", "min"), Output("cbar", "max"), Output("cbar", "unit")],
              [Input("dd_param", "value"), Input("dd_cmap", "value")])
def update_url(param, cmap):
    if not param or not cmap:
        raise PreventUpdate
    srng = srng_map[param]
    url = singleband_url(TC_URL, [GFS_KEY, param], colormap=cmap.lower(), stretch_range=srng)
    return url, cmap, float(srng[0]), float(srng[1]), unit_map[param]


@app.callback(Output("text", "children"), [Input("map", 'click_lat_lng'), Input("dd_param", "value")])
def update_label(click_lat_lng, param):
    if not click_lat_lng:
        return "-"
    url = point_url(TC_URL, [GFS_KEY, param], click_lat_lng[0], click_lat_lng[1])
    print(url)
    data = json.load(urllib.request.urlopen(url))
    return "{:.3f} {}".format(float(data), unit_map[param])


if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
