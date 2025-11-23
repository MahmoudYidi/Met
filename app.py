from dash import Dash, html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Use a clean & neutral Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# --- Initial default values ---
initial_metrics = {
    "scanned": 1200,
    "anomalies": 32,
    "fps": 18.5,
    "epochs": [1, 2, 3, 4, 5],
    "precision": [0.70, 0.75, 0.80, 0.82, 0.85],
    "recall":    [0.60, 0.65, 0.72, 0.75, 0.78],
    "f1":        [0.64, 0.69, 0.75, 0.78, 0.81]
}


# ============================================================
# MODERN ASH/GRAY GLASS UI STYLES
# ============================================================
BACKGROUND_STYLE = {
    "background": "#e4e4e4",  # Ash Gray
    "minHeight": "100vh",
    "paddingBottom": "40px"
}

CARD_STYLE = {
    "borderRadius": "18px",
    "background": "rgba(255,255,255,0.55)",
    "backdropFilter": "blur(6px)",
    "boxShadow": "0 6px 20px rgba(0,0,0,0.25)",
    "border": "1px solid rgba(255,255,255,0.6)",
}

TITLE_STYLE = {
    "fontWeight": "600",
    "textAlign": "center",
    "padding": "12px 0",
    "color": "#333",
}

TILE_NUMBER_STYLE = {
    "fontSize": "42px",
    "fontWeight": "700",
    "color": "#2a2a2a",
}



# ============================================================
# LAYOUT
# ============================================================
app.layout = dbc.Container([

    dcc.Interval(id="update-interval", interval=3000),
    dcc.Store(id="metrics-store", data=initial_metrics),

    # ------------------- LOGO + TITLE -------------------
    html.Div([
        html.Img(src="assets/logo.png", style={
            "height": "85px",
            "marginBottom": "10px",
        }),

        html.H1("Analytics Dashboard", style={
            "textAlign": "center",
            "fontWeight": "700",
            "fontSize": "42px",
            "color": "#222",
            "marginBottom": "25px"
        })
    ], style={"textAlign": "center"}),

    # =================== METRIC TILES ===================
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6("Scanned", className="text-center text-muted"),
                    html.Div(id="scanned-tile", style=TILE_NUMBER_STYLE)
                ])
            ], style=CARD_STYLE),
            md=4
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6("Anomalies", className="text-center text-muted"),
                    html.Div(id="anomalies-tile", style=TILE_NUMBER_STYLE)
                ])
            ], style=CARD_STYLE),
            md=4
        ),

        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H6("FPS", className="text-center text-muted"),
                    html.Div(id="fps-tile", style=TILE_NUMBER_STYLE)
                ])
            ], style=CARD_STYLE),
            md=4
        ),
    ], className="my-4"),

    # =================== PERFORMANCE CHART ===================
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4("Precision / Recall / F1", style=TITLE_STYLE),
                    dcc.Graph(id="performance-chart", style={"height": "420px"})
                ])
            ], style=CARD_STYLE),
            md=12
        )
    ], className="my-3")

], fluid=True, style=BACKGROUND_STYLE)



# ============================================================
# CALLBACK
# ============================================================
@app.callback(
    [
        Output("scanned-tile", "children"),
        Output("anomalies-tile", "children"),
        Output("fps-tile", "children"),
        Output("performance-chart", "figure"),
    ],
    [Input("update-interval", "n_intervals"),
     Input("metrics-store", "data")]
)
def update_dashboard(n, data):
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

    fig.update_layout(
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", y=-0.2),
        plot_bgcolor="rgba(255,255,255,0.5)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333")
    )

    return scanned, anomalies, fps, fig



# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)
