import plotly.express as px

GOOD, BAD, GREY = "#1f6f9f", "#c0392b", "#8a9399"
SCALE = "Reds"
LABELS = {"pct_bact": "Bacteriological non-compliance (%)",
          "pct_chim": "Chemical non-compliance (%)",
          "pct_no3": "Nitrate analyses > 50 mg/L (%)",
          "year" : "Year", "dept_name" : "Département", "size" : "Samples per network per year"}


def _style(fig, title):
    fig.update_layout(title=title, template="simple_white", margin=dict(l=10, r=10, t=50, b=10),
                      legend_title_text="", hovermode="x unified" if fig.data and
                      fig.data[0].type == "scatter" else "closest")
    return fig


def line_chart(df, x, ys, title):
    long = df.melt(id_vars=x, value_vars=ys, var_name="metric", value_name="value")
    long["metric"] = long["metric"].map(LABELS)
    fig = px.line(long, x=x, y="value", color="metric", markers=True,
                  color_discrete_sequence=[BAD, GOOD, GREY], labels={"value ": "%", x: LABELS[x]})
    fig.update_xaxes(dtick=1)
    return _style(fig, title)


def bar_chart(df, x, y, title, ref=None, ref_label="France", color=None):
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", labels=LABELS,
                 color_discrete_sequence=[BAD, GOOD, GREY])
    if color is None:
        fig.update_traces(marker_color=BAD)
    if ref is not None:
        fig.add_hline(y=ref, line_dash="dash", line_color=GREY,
                      annotation_text=f"{ref_label}: {ref:.2f}%", annotation_position="top right")
    return _style(fig, title)


def map_chart(df, geo, value, title):
    fig = px.choropleth(df, geojson=geo, locations="dept", featureidkey="properties.code",
                        color=value, color_continuous_scale=SCALE, hover_name="dept_name",
                        hover_data={"dept": False, "n": True}, labels=LABELS | {"n" : "Samples"})
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=550, coloraxis_colorbar_title="%")
    return _style(fig, title)
