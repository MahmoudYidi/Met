from dash import Dash, html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask, jsonify, request
import os
import requests
from dash_iconify import DashIconify  

# ----------------------------
# Flask server for endpoints
# ----------------------------
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.FLATLY])

# ----------------------------
# Initial metrics
# ----------------------------
metrics_data = {
    "scanned": 1,
    "anomalies": 1,
    "total_normal": 1,
    "fps": 1,
    "percent_anomalous": 1,
    "threshold": 1
}

# =======================
# Styles
# =======================
BACKGROUND_STYLE = {"background": "#e4e4e4", "minHeight": "100vh", "paddingBottom": "40px"}
CARD_STYLE = {"borderRadius": "18px", "background": "rgba(255,255,255,0.55)",
              "backdropFilter": "blur(6px)", "boxShadow": "0 6px 20px rgba(0,0,0,0.25)",
              "border": "1px solid rgba(255,255,255,0.6)"}
TITLE_STYLE = {"fontWeight": "600", "textAlign": "center", "padding": "12px 0", "color": "#333"}
TILE_NUMBER_STYLE = {"fontSize": "42px", "fontWeight": "700"}
ICON_STYLE = {"fontSize": "28px", "marginRight": "8px"}

# =======================
# Layout
# =======================
app.layout = dbc.Container([
    dcc.Interval(id="update-interval", interval=1000),

    # Logo + Title
    html.Div([
        html.Img(src="/assets/logo.png", style={"height": "85px", "marginBottom": "10px"}),
        html.H1("Anomaly Dashboard Demo", style={"textAlign": "center",
                                                  "fontWeight": "700",
                                                  "fontSize": "42px",
                                                  "color": "#222",
                                                  "marginBottom": "25px"})
    ], style={"textAlign": "center"}),

    # Metric Tiles - Row 1
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:eye", style=ICON_STYLE),
                html.Span("Scanned", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="scanned-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "#2a2a2a"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:alert-circle-outline", style=ICON_STYLE),
                html.Span("Anomalies", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="anomalies-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "red"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:check-circle-outline", style=ICON_STYLE),
                html.Span("Normal", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="normal-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "green"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),
    ], className="my-2"),

    # Metric Tiles - Row 2
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:speedometer", style=ICON_STYLE),
                html.Span("FPS", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="fps-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "#2a2a2a"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:percent", style=ICON_STYLE),
                html.Span("Anomaly %", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="percent-anomalous-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "red"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.Div([
                DashIconify(icon="mdi:vector-triangle", style=ICON_STYLE),
                html.Span("Threshold", className="text-muted")
            ], className="d-flex justify-content-center align-items-center mb-2"),
            html.Div(id="threshold-tile", className="tile-number", style={**TILE_NUMBER_STYLE, "color": "#2a2a2a"})
        ]), style=CARD_STYLE), md=4, xs=12, className="mb-3"),
    ], className="my-2"),

    # Pie Chart
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H4("Normal vs Anomalous", style=TITLE_STYLE),
            dcc.Graph(id="pie-chart", style={"width": "100%", "height": "100%"})
        ])), md=12, xs=12, style=CARD_STYLE, className="mb-3")
    ], className="my-2"),

], fluid=True, style=BACKGROUND_STYLE)

# =======================
# Dash callback
# =======================
@app.callback(
    [
        Output("scanned-tile", "children"),
        Output("anomalies-tile", "children"),
        Output("normal-tile", "children"),
        Output("fps-tile", "children"),
        Output("percent-anomalous-tile", "children"),
        Output("threshold-tile", "children"),
        Output("pie-chart", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n):
    try:
        resp = requests.get("https://met-rbic.onrender.com/metrics", timeout=2)
        data = resp.json()
    except Exception as e:
        print("Error fetching metrics:", e)
        data = metrics_data

    scanned = data.get("scanned", 1)
    anomalies = data.get("anomalies", 0)
    normal = data.get("total_normal", scanned - anomalies)
    fps = data.get("fps", 0)
    percent_anomalous = data.get("percent_anomalous", round(anomalies / scanned * 100, 2))
    threshold = data.get("threshold", 0.5)

    fig = go.Figure(go.Pie(labels=["Normal", "Anomalous"],
                           values=[normal, anomalies],
                           marker=dict(colors=["green", "red"]),
                           hole=0.4))
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                      height=400,
                      paper_bgcolor="rgba(0,0,0,0)")

    return scanned, anomalies, normal, fps, percent_anomalous, threshold, fig

# =======================
# Backend endpoints
# =======================
@server.route("/metrics", methods=["GET"])
def metrics_get():
    return jsonify(metrics_data)

@server.route("/metrics", methods=["POST"])
def metrics_post():
    global metrics_data
    incoming = request.get_json(force=True)
    for key, value in incoming.items():
        if key in metrics_data:
            metrics_data[key] = value
    return jsonify({"status": "updated", "metrics": metrics_data})

# =======================
# Run
# =======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
