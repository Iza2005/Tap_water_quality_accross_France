import streamlit as st
from utils.viz import LABELS, bar_chart, map_chart

MIN_SAMPLES = 100  # departments with fewer samples are left out of rankings, it could alter the results


def render(t, geo, year, metric, depts):
    d = t["dept"][t["dept"]["year"] == year]
    ref = t["national"].set_index("year").loc[year, metric]

    st.header("Where are the problems ?")
    st.plotly_chart(map_chart(d, geo, metric, f"{LABELS[metric]} by department, {year}"),
                    width="stretch")

    ranked = d[d["n"] >= MIN_SAMPLES].sort_values(metric, ascending=False)
    shown = ranked[ranked["dept_name"].isin(depts)] if depts else ranked.head(10)
    title = "Selected departements" if depts else "10 most affected departments"
    st.plotly_chart(bar_chart(shown, "dept_name", metric, f"{title} vs national average, {year}", ref=ref),
                    width="stretch")
    st.caption(f"Departements with fewer than {MIN_SAMPLES} samples in {year} are excluded from the ranking.")

    st.header("Are small networks more exposed ?")
    s = t["by_size"][t["by_size"]["year"] == year]
    s = s.melt(id_vars="size", value_vars=["pct_bact", "pct_chim"], var_name="type", value_name="pct")
    s["type"] = s["type"].map(LABELS)
    fig = bar_chart(s, "size", "pct", f"Non-compliance by network size, {year}", color="type")
    fig.update_yaxes(title="%")
    st.plotly_chart(fig, width="stretch")
    st.caption("Network size is approximated by samples per year, which grows with the population served.")

    st.header("You can check how is tap water in your own commune !")
    com = t["com"]
    options = (com["nomcommune"] + " (" + com["inseecommune"] + ")").drop_duplicates().sort_values()
    choice = st.selectbox("Commune", options, index=None, placeholder="Type a commune name")
    if choice:
        insee = choice[-6:-1]
        nets = com[com["inseecommune"] == insee][["cdreseau", "nomreseau"]]
        u = t["udi"][t["udi"]["year"] == year].merge(nets, on="cdreseau")
        if u.empty:
            st.warning(f"No sample recorded in {year} for the networks serving this commune.")
        else:
            st.dataframe(u[["nomreseau", "n", "pct_bact", "pct_chim", "no3_mean", "no3_max"]].rename(
                columns={"nomreseau": "Network", "n": "Samples", "pct_bact": LABELS["pct_bact"],
                         "pct_chim": LABELS["pct_chim"], "no3_mean": "Mean nitrates (mg/L)",
                         "no3_max": "Max nitrates (mg/L)"}).round(2),
                width="stretch", hide_index=True)
