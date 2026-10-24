import streamlit as st
from utils.prep import sum_by
from utils.viz import line_chart


def render(t, year, depts):
    d = t["dept"] if not depts else t["dept"][t["dept"]["dept_name"].isin(depts)]
    nat = sum_by(d, ["year"]).set_index("year")
    cur = nat.loc[year]
    prev = nat.loc[year - 1] if year - 1 in nat.index else None
    delta = lambda c: None if prev is None else f"{cur[c] - prev[c]:+.2f} pts vs {year - 1}"

    st.header(f"Overview : {', '.join(depts) if depts else 'France'}, {year}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Samples", f"{int(cur['n']):,}".replace(",", " "))
    c2.metric("Bacteriological non-compliance", f"{cur['pct_bact']:.2f}%", delta("pct_bact"), delta_color="inverse")
    c3.metric("Chemical non-compliance", f"{cur['pct_chim']:.2f}%", delta("pct_chim"), delta_color="inverse")
    c4.metric("Nitrates > 50 mg/L", f"{cur['pct_no3']:.2f}%", delta("pct_no3"), delta_color="inverse")

    st.plotly_chart(line_chart(nat.reset_index(), "year", ["pct_bact", "pct_chim", "pct_no3"],
                               "Non-compliance over time"), width="stretch")
    first, last = nat.index.min(), nat.index.max()
    st.caption(f"From {first} to {last}, bacteriological non-compliance went from "
               f"{nat.loc[first, 'pct_bact']:.2f}% to {nat.loc[last, 'pct_bact']:.2f}% and chemical "
               f"non-compliance from {nat.loc[first, 'pct_chim']:.2f}% to {nat.loc[last, 'pct_chim']:.2f}%.")
