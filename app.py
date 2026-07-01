import pandas as pd
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# =========================
# LOAD DATA
# =========================

country_summary = pd.read_csv("country_year_summary_2015_2060.csv")
country_rankings = pd.read_csv("global_country_risk_rankings_2026.csv")
forecast = pd.read_csv("global_forecast_2030_2040_2050_2060.csv")
region_risk = pd.read_csv("region_2026_risk_profile.csv")
urban_rural = pd.read_csv("regional_urban_rural_risk_summary_2026.csv")
segments = pd.read_csv("teen_behaviour_segments.csv")

# =========================
# APP SETUP
# =========================

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Roboto+Mono:wght@400;500;600;700&display=swap"
    ]
)

app.title = "Teen Insights Dashboard"
server = app.server

# =========================
# HELPERS
# =========================

def clean_label(text):
    return str(text).replace("_", " ").title()

def safe_mean(df, col):
    return round(df[col].mean(), 2) if col in df.columns else 0

# =========================
# GLOBAL STYLES
# =========================

PAGE_STYLE = {
    "background": "#f8fafc",
    "minHeight": "100vh",
    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "textRendering": "optimizeLegibility",
    "WebkitFontSmoothing": "antialiased",
    "MozOsxFontSmoothing": "grayscale",
    "fontVariantNumeric": "tabular-nums",
    "color": "#0f172a"
}

SIDEBAR_STYLE = {
    "background": "#ffffff",
    "minHeight": "100vh",
    "padding": "24px 18px",
    "boxShadow": "8px 0 30px rgba(15,23,42,0.08)",
    "position": "sticky",
    "top": "0"
}

CARD_STYLE = {
    "background": "#ffffff",
    "border": "1px solid #e5e7eb",
    "borderRadius": "22px",
    "boxShadow": "0 14px 35px rgba(15,23,42,0.08)",
    "padding": "12px"
}

# =========================
# COMPONENTS
# =========================

def nav_link(label, target):
    return html.A(
        label,
        href=f"#{target}",
        style={
            "display": "block",
            "padding": "13px 16px",
            "borderRadius": "14px",
            "marginBottom": "8px",
            "fontWeight": "800",
            "color": "#334155",
            "textDecoration": "none",
            "fontSize": "14px"
        }
    )

def kpi_card(title, value, note, color):
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, style={
                "fontSize": "13px",
                "color": "#64748b",
                "fontWeight": "700",
                "letterSpacing": "0.01em"
            }),
            html.H2(value, style={
                "fontWeight": "900",
                "fontSize": "36px",
                "lineHeight": "1.05",
                "marginTop": "8px",
                "color": "#0f172a",
                "fontVariantNumeric": "tabular-nums"
            }),
            html.Small(note, style={
                "color": color,
                "fontWeight": "700",
                "fontSize": "12px"
            })
        ]),
        style={**CARD_STYLE, "height": "145px"}
    )

def chart_card(title, graph_id):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, style={
                "fontWeight": "800",
                "fontSize": "18px",
                "letterSpacing": "-0.01em",
                "marginBottom": "12px",
                "color": "#111827"
            }),
            dcc.Graph(id=graph_id, config={"displayModeBar": False})
        ]),
        style=CARD_STYLE
    )

# =========================
# KPI DATA
# =========================

total_countries = country_summary["country"].nunique()
total_regions = country_summary["region"].nunique() if "region" in country_summary.columns else region_risk["region"].nunique()
total_records = len(country_summary)
avg_screen_time = safe_mean(country_summary, "avg_screen_time_hours")

kpis = dbc.Row([
    dbc.Col(kpi_card("Total Records", f"{total_records:,}", "Country-year observations", "#2563eb"), md=3),
    dbc.Col(kpi_card("Countries", total_countries, "Global coverage", "#7c3aed"), md=3),
    dbc.Col(kpi_card("Regions", total_regions, "Regional clusters", "#f97316"), md=3),
    dbc.Col(kpi_card("Avg Screen Time", f"{avg_screen_time:.2f} hrs", "Daily average", "#16a34a"), md=3),
])

table_df = country_rankings.copy()
table_df.columns = [clean_label(c) for c in table_df.columns]

# =========================
# LAYOUT
# =========================

app.layout = html.Div([

    dbc.Row([

        dbc.Col([
            html.H2("Teen Insights", style={"fontWeight": "900", "color": "#0f172a"}),
            html.P("Global Analytics", style={"color": "#64748b", "fontWeight": "700"}),

            html.Hr(),

            nav_link("🏠 Dashboard", "dashboard"),
            nav_link("🌍 Country Analysis", "country-analysis"),
            nav_link("📊 Regional Analysis", "regional-analysis"),
            nav_link("🏙 Urban vs Rural", "urban-rural"),
            nav_link("📈 Forecast Analytics", "forecast"),
            nav_link("🧠 Behaviour Segments", "segments"),
            nav_link("📁 Data Explorer", "data"),

            html.Div([
                html.H5("Data-Driven Decisions", style={"fontWeight": "900"}),
                html.P(
                    "Empowering better digital wellbeing for teens worldwide.",
                    style={"fontSize": "13px", "color": "#64748b"}
                ),
                dbc.Button("View Reports", color="primary", style={
                    "borderRadius": "12px",
                    "width": "100%",
                    "fontWeight": "800"
                })
            ], style={
                "background": "#f1f5f9",
                "padding": "18px",
                "borderRadius": "20px",
                "marginTop": "30px"
            })

        ], md=2, style=SIDEBAR_STYLE),

        dbc.Col([

            html.Div(id="dashboard", children=[
                html.H1(
                    "Global Teen Social Media Behaviour Dashboard",
                    style={
                        "fontWeight": "900",
                        "fontSize": "36px",
                        "letterSpacing": "-0.03em",
                        "marginBottom": "4px"
                    }
                ),
                html.P(
                    "Comprehensive insights into teen digital behaviour, wellbeing and future trends.",
                    style={
                        "color": "#64748b",
                        "fontSize": "16px",
                        "fontWeight": "500"
                    }
                )
            ], style={"padding": "28px 20px 10px"}),

            html.Div(kpis, style={"padding": "0 20px 20px"}),

            html.Div([
                dbc.Card(
                    dbc.CardBody([
                        html.Label("Select Country", style={
                            "fontWeight": "900",
                            "fontSize": "13px"
                        }),
                        dcc.Dropdown(
                            id="country",
                            options=[
                                {"label": c, "value": c}
                                for c in sorted(country_summary["country"].unique())
                            ],
                            value="Nigeria" if "Nigeria" in country_summary["country"].unique() else sorted(country_summary["country"].unique())[0],
                            clearable=False,
                            style={"color": "#0f172a", "fontSize": "14px"}
                        )
                    ]),
                    style=CARD_STYLE
                )
            ], style={"padding": "0 20px 20px"}),

            dbc.Row([
                dbc.Col(html.Div(id="country-analysis", children=[
                    chart_card("Trend Analysis", "trend_chart")
                ]), md=8),

                dbc.Col(chart_card("Top 10 High-Risk Countries", "top10_risk_chart"), md=4)
            ], style={"padding": "0 20px 20px"}),

            dbc.Row([
                dbc.Col(html.Div(id="regional-analysis", children=[
                    chart_card("Regional Addiction Comparison", "regional_addiction_chart")
                ]), md=4),

                dbc.Col(html.Div(id="urban-rural", children=[
                    chart_card("Urban vs Rural Risk", "urban_rural_chart")
                ]), md=4),

                dbc.Col(html.Div(id="forecast", children=[
                    chart_card("Forecast Analytics", "forecast_chart")
                ]), md=4)
            ], style={"padding": "0 20px 20px"}),

            html.Div(id="segments", children=[
                chart_card("Teen Behaviour Segments", "segment_chart")
            ], style={"padding": "0 20px 20px"}),

            html.Div(id="data", children=[
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Country Risk Overview", style={"fontWeight": "900"}),
                        dash_table.DataTable(
                            columns=[{"name": col, "id": col} for col in table_df.columns],
                            data=table_df.to_dict("records"),
                            page_size=10,
                            filter_action="native",
                            sort_action="native",
                            style_table={"overflowX": "auto"},
                            style_cell={
                                "backgroundColor": "white",
                                "color": "#0f172a",
                                "border": "1px solid #e5e7eb",
                                "padding": "9px 10px",
                                "fontFamily": "'Roboto Mono', monospace",
                                "fontSize": "12px",
                                "fontWeight": "400",
                                "fontVariantNumeric": "tabular-nums"
                            },
                            style_header={
                                "backgroundColor": "#eff6ff",
                                "color": "#1d4ed8",
                                "fontFamily": "Inter, sans-serif",
                                "fontSize": "12px",
                                "fontWeight": "800",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.04em"
                            }
                        )
                    ]),
                    style=CARD_STYLE
                )
            ], style={"padding": "0 20px 35px"})

        ], md=10)

    ], className="g-0")

], style=PAGE_STYLE)

# =========================
# CALLBACKS
# =========================

@app.callback(
    Output("trend_chart", "figure"),
    Output("top10_risk_chart", "figure"),
    Output("regional_addiction_chart", "figure"),
    Output("urban_rural_chart", "figure"),
    Output("forecast_chart", "figure"),
    Output("segment_chart", "figure"),
    Input("country", "value")
)
def update_charts(selected_country):

    color_seq = ["#2563eb", "#22c55e", "#f97316", "#ec4899", "#8b5cf6", "#06b6d4"]

    # Trend chart
    df_country = country_summary[country_summary["country"] == selected_country]

    trend_fig = px.line(
        df_country,
        x="year",
        y=[
            "avg_screen_time_hours",
            "avg_sleep_hours",
            "avg_addiction_score",
            "avg_mental_health_risk"
        ],
        markers=True,
        color_discrete_sequence=color_seq,
        template="plotly_white"
    )

    trend_fig.for_each_trace(
        lambda t: t.update(
            name=clean_label(t.name),
            line=dict(width=4),
            marker=dict(size=8)
        )
    )

    trend_fig.update_layout(
        height=430,
        title=f"Trend Analysis For {selected_country}",
        title_font=dict(size=18, family="Inter", color="#0f172a"),
        legend_title_text="",
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=30, r=20, t=60, b=30)
    )

    # Top 10 countries
    top10 = country_rankings.sort_values("avg_overall_risk", ascending=False).head(10)

    top10_fig = px.bar(
        top10,
        x="avg_overall_risk",
        y="country",
        orientation="h",
        text="avg_overall_risk",
        color="avg_overall_risk",
        color_continuous_scale=[
            "#2563eb",
            "#06b6d4",
            "#22c55e",
            "#facc15",
            "#f97316",
            "#ec4899"
        ],
        template="plotly_white"
    )

    top10_fig.update_traces(
        textfont=dict(family="Roboto Mono, monospace", size=11)
    )

    top10_fig.update_layout(
        height=430,
        title="Top 10 High-Risk Countries 2026",
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=30)
    )

    top10_fig.update_xaxes(title="Overall Risk")
    top10_fig.update_yaxes(title="Country")

    # Regional comparison
    regional = region_risk.sort_values("avg_addiction_score", ascending=False)

    regional_fig = px.bar(
        regional,
        x="region",
        y="avg_addiction_score",
        color="avg_addiction_score",
        text="avg_addiction_score",
        color_continuous_scale=[
            "#2563eb",
            "#8b5cf6",
            "#ec4899",
            "#f97316"
        ],
        template="plotly_white"
    )

    regional_fig.update_traces(
        textfont=dict(family="Roboto Mono, monospace", size=11)
    )

    regional_fig.update_layout(
        height=420,
        title="Regional Addiction Comparison 2026",
        coloraxis_showscale=False,
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=30, r=20, t=60, b=80)
    )

    regional_fig.update_xaxes(title="Region", tickangle=-35)
    regional_fig.update_yaxes(title="Addiction Score")

    # Urban vs rural
    urban_summary = urban_rural.groupby(
        "urban_rural",
        as_index=False
    )["avg_addiction_score"].mean()

    urban_fig = px.pie(
        urban_summary,
        names="urban_rural",
        values="avg_addiction_score",
        hole=0.58,
        color_discrete_sequence=["#2563eb", "#9333ea", "#14b8a6"],
        template="plotly_white"
    )

    urban_fig.update_traces(
        textfont=dict(family="Roboto Mono, monospace", size=11)
    )

    urban_fig.update_layout(
        height=420,
        title="Urban Vs Rural Addiction Risk",
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Forecast
    selected_forecast = forecast[forecast["country"] == selected_country]

    forecast_cols = [
        c for c in forecast.columns
        if "addiction" in c.lower()
        and any(y in c for y in ["2030", "2040", "2050", "2060"])
    ]

    if len(forecast_cols) == 0:
        forecast_cols = [
            c for c in forecast.columns
            if any(y in c for y in ["2030", "2040", "2050", "2060"])
        ]

    forecast_data = selected_forecast[forecast_cols].T.reset_index()
    forecast_data.columns = ["Forecast Year", "Value"]
    forecast_data["Forecast Year"] = forecast_data["Forecast Year"].apply(clean_label)

    forecast_fig = px.bar(
        forecast_data,
        x="Forecast Year",
        y="Value",
        text="Value",
        color="Value",
        color_continuous_scale=["#60a5fa", "#2563eb", "#1d4ed8"],
        template="plotly_white"
    )

    forecast_fig.update_traces(
        textfont=dict(family="Roboto Mono, monospace", size=11)
    )

    forecast_fig.update_layout(
        height=420,
        title=f"Forecast Analytics For {selected_country}",
        coloraxis_showscale=False,
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=30, r=20, t=60, b=80)
    )

    forecast_fig.update_xaxes(title="")
    forecast_fig.update_yaxes(title="Forecast Value")

    # Behaviour segments
    segment_fig = px.bar(
        segments,
        x="segment",
        y="daily_screen_time_hours",
        color="social_media_hours",
        text="daily_screen_time_hours",
        color_continuous_scale=[
            "#22c55e",
            "#facc15",
            "#f97316",
            "#ef4444"
        ],
        template="plotly_white"
    )

    segment_fig.update_traces(
        textfont=dict(family="Roboto Mono, monospace", size=11)
    )

    segment_fig.update_layout(
        height=420,
        title="Teen Behaviour Segments",
        coloraxis_colorbar_title="Social Media Hours",
        font=dict(family="Inter, Arial, sans-serif", size=12, color="#334155"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=30, r=20, t=60, b=40)
    )

    segment_fig.update_xaxes(title="Segment")
    segment_fig.update_yaxes(title="Daily Screen Time Hours")

    return trend_fig, top10_fig, regional_fig, urban_fig, forecast_fig, segment_fig

# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)
