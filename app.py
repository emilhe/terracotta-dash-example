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
from terracotta_toolbelt import singleband_url, point_url

cmaps = ["Viridis", "Spectral", "Greys"]
lbl_map = dict(wspd="Wind speed", temp="Temperature")
unit_map = dict(wspd="m/s", temp="°K")
srng_map = dict(wspd=[0, 10], temp=[250, 300])
param0 = "temp"
cmap0 = "Viridis"
srng0 = srng_map[param0]
# App Stuff.
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.layout = html.Div(children=[
    # Create the map itself.
    dl.Map(id="map", center=[56, 10], zoom=7, children=[
        dl.TileLayer(),
        dl.TileLayer(id="tc", opacity=0.5),
        dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
    ], style={"width": "100%", "height": "100%"}),
    # Create controller.
    html.Div(children=[
        html.Div("Parameter"),
        dcc.Dropdown(id="dd_param", options=[dict(value=p, label=lbl_map[p]) for p in PARAMS], value=param0),
        html.Br(),
        html.Div("Colorbar"),
        dcc.Dropdown(id="dd_cmap", options=[dict(value=c, label=c) for c in cmaps], value=cmap0),
        html.Br(),
        html.Div("Opacity"),
        dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
        html.Br(),
        html.Div("Stretch range"),
        dcc.RangeSlider(id="srng", min=srng0[0], max=srng0[1], value=srng0,
                        marks={v: "{:.1f}".format(v) for v in srng0}),
        html.Br(),
        html.Div("Value @ click position"),
        html.P(children="-", id="label"),
    ], className="info")
], style={"display": "grid", "width": "100%", "height": "100vh"})


@app.callback(Output("tc", "opacity"), [Input("opacity", "value")])
def update_opacity(opacity):
    return opacity


@app.callback([Output("srng", "min"), Output("srng", "max"), Output("srng", "value"), Output("srng", "marks")],
              [Input("dd_param", "value")])
def update_stretch_range(param):
    if not param:
        return PreventUpdate
    srng = srng_map[param]
    return srng[0], srng[1], srng, {v: "{:.1f}".format(v) for v in srng}


@app.callback([Output("tc", "url"),
               Output("cbar", "colorscale"), Output("cbar", "min"), Output("cbar", "max"), Output("cbar", "unit")],
              [Input("dd_param", "value"), Input("dd_cmap", "value"), Input("srng", "value")])
def update_url(param, cmap, srng):
    if not param or not cmap:
        raise PreventUpdate
    srng = [float(item) for item in srng]
    url = singleband_url(TC_URL, GFS_KEY, param, colormap=cmap.lower(), stretch_range=srng)
    return url, cmap, float(srng[0]), float(srng[1]), unit_map[param]


@app.callback(Output("label", "children"), [Input("map", 'click_lat_lng'), Input("dd_param", "value")])
def update_label(click_lat_lng, param):
    if not click_lat_lng:
        return "-"
    url = point_url(TC_URL, GFS_KEY, param, lat=click_lat_lng[0], lon=click_lat_lng[1])
    data = json.load(urllib.request.urlopen(url))
    return "{:.3f} {}".format(float(data), unit_map[param])


if __name__ == '__main__':
    app.run_server(port=8050)
