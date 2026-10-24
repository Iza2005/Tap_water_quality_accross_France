import streamlit as st
from sections import conclusions, deep_dives, intro, overview
from utils.io import DATASET_URL, LICENSE_TEXT, fetch_and_cache, load_data
from utils.prep import make_tables
from utils.viz import LABELS

st.set_page_config(page_title="Is tap water equally safe across France ?", layout="wide")


@st.cache_data(show_spinner="Loading data, please wait…")
def get_data():
    geo = fetch_and_cache()
    return make_tables(load_data(), geo), geo


tables, geo = get_data()
years = sorted(tables["national"]["year"].unique())

st.title("Is tap water equally safe across France ?")
st.caption(f"{LICENSE_TEXT} [Dataset]({DATASET_URL})")

with st.sidebar:
    st.header("Filters")
    year = st.selectbox("Year", years, index=len(years) - 1)
    metric = st.selectbox("Metric", ["pct_bact", "pct_chim", "pct_no3"], format_func=LABELS.get)
    depts = st.multiselect("Départements (empty = all France)",
                           sorted(tables["dept"]["dept_name"].unique()))

intro.render(tables["quality"])
overview.render(tables, year, depts)
deep_dives.render(tables, geo, year, metric, depts)
conclusions.render(tables, year, metric)
