from dash import Dash, html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask, jsonify, request
import os
import requests

# ----------------------------
# Flask server for endpoints
# ----------------------------
server = Flask(__name__)
app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.FLATLY])

# ----------------------------
# Initial metrics
# ----------------------------
metrics_data = {
    "scanned": 1200,
    "anomalies": 32,
    "fps": 18.5,
    "epochs": [1, 2, 3, 4, 5],
    "precision": [0.70, 0.75, 0.80, 0.82, 0.85],
    "recall":    [0.60, 0.65, 0.72, 0.75, 0.78],
    "f1":        [0.64, 0.69, 0.75, 0.78, 0.81]
}

# =======================
# Styles
# =======================
BACKGROUND_STYLE = {"background": "#e4e4e4", "minHeight": "100vh", "paddingBottom": "40px"}
CARD_STYLE = {"borderRadius": "18px", "background": "rgba(255,255,255,0.55)",
              "backdropFilter": "blur(6px)", "boxShadow": "0 6px 20px rgba(0,0,0,0.25)",
              "border": "1px solid rgba(255,255,255,0.6)"}
TITLE_STYLE = {"fontWeight": "600", "textAlign": "center", "padding": "12px 0", "color": "#333"}
TILE_NUMBER_STYLE = {"fontSize": "42px", "fontWeight": "700", "color": "#2a2a2a"}

# =======================
# Layout
# =======================
app.layout = dbc.Container([
    dcc.Interval(id="update-interval", interval=3000),
    dcc.Store(id="metrics-store", data=metrics_data),

    html.Div([
        html.Img(src="/assets/logo.png", style={"height": "85px", "marginBottom": "10px"}),
        html.H1("Analytics Dashboard", style={"textAlign": "center", "fontWeight": "700",
                                             "fontSize": "42px", "color": "#222", "marginBottom": "25px"})
    ], style={"textAlign": "center"}),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Scanned", className="text-center text-muted"),
                                       html.Div(id="scanned-tile", style=TILE_NUMBER_STYLE)]),
                         style=CARD_STYLE), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Anomalies", className="text-center text-muted"),
                                       html.Div(id="anomalies-tile", style=TILE_NUMBER_STYLE)]),
                         style=CARD_STYLE), md=4),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("FPS", className="text-center text-muted"),
                                       html.Div(id="fps-tile", style=TILE_NUMBER_STYLE)]),
                         style=CARD_STYLE), md=4),
    ], className="my-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H4("Precision / Recall / F1", style=TITLE_STYLE),
                                       dcc.Graph(id="performance-chart", style={"height": "420px"})])),
                md=12, style=CARD_STYLE)
    ], className="my-3")

], fluid=True, style=BACKGROUND_STYLE)

# =======================
# Dash callback
# =======================
@app.callback(
    [
        Output("scanned-tile", "children"),
        Output("anomalies-tile", "children"),
        Output("fps-tile", "children"),
        Output("performance-chart", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n):
    try:
        # Fetch latest metrics from backend
        resp = requests.get("https://met-rbic.onrender.com/metrics", timeout=2)
        data = resp.json()
    except Exception as e:
        print("Error fetching metrics:", e)
        # fallback to last known metrics
        data = metrics_data

    scanned = data["scanned"]
    anomalies = data["anomalies"]
    fps = data["fps"]

    epochs = data["epochs"]
    precision = data["precision"]
    recall = data["recall"]
    f1 = data["f1"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=epochs, y=precision, mode="lines+markers", name="Precision"))
    fig.add_trace(go.Scatter(x=epochs, y=recall, mode="lines+markers", name="Recall"))
    fig.add_trace(go.Scatter(x=epochs, y=f1, mode="lines+markers", name="F1 Score"))

    fig.update_layout(template="plotly_white", height=400,
                      margin=dict(l=40, r=40, t=40, b=40),
                      legend=dict(orientation="h", y=-0.2),
                      plot_bgcolor="rgba(255,255,255,0.5)",
                      paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#333"))

    return scanned, anomalies, fps, fig

# =======================
# Backend endpoints
# =======================
@server.route("/metrics", methods=["GET"])
def metrics_get():
    """Frontend fetches metrics."""
    return jsonify(metrics_data)

@server.route("/metrics", methods=["POST"])
def metrics_post():
    """External devices push metrics."""
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=True)
