# Is tap water equally safe across France?

Streamlit data-storytelling app on the sanitary control of tap water in France.

## Dataset
- **Résultats du contrôle sanitaire de l'eau distribuée commune par commune** — Ministère de la Santé (SISE-Eaux), data.gouv.fr
  https://www.data.gouv.fr/datasets/resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune
- Licence Ouverte / Open Licence 2.0
- Files used: national yearly zips `dis-YYYY.zip` (2021–2025), each with `DIS_PLV` (samples), `DIS_RESULT` (analyses) and `DIS_COM_UDI` (commune ↔ network links).
- Map contours only: https://github.com/gregoiredavid/france-geojson (`data/departements.geojson`).

## Story
- **Audience:** residents and local officials.
- **Questions:** How often does tap water fail the standards, and is it improving? Which départements are most affected? Are small networks more exposed? Where do nitrates exceed 50 mg/L?
- **Arc:** hook and context → national KPIs and trend → map and ranking of départements → network size → commune lookup → insights, implications, limitations.
- **Patterns:** compare regions (map + ranking) and change over time.

## Data work (`utils/prep.py`)
1. Read the text files directly from the zips (encoding and separator detected, required columns checked).
2. Samples: strip values, drop rows without sample/network/commune code, remove duplicates, keep samples dated in the file's year, derive the département from the main commune's INSEE code.
3. Compliance: share of samples flagged `N` among samples flagged `C` or `N`, for bacteriological and chemical standards.
4. Nitrates: parameter `NO3` from `DIS_RESULT`, converted to numbers, one value per sample, compared with the 50 mg/L limit.
5. Aggregation per network (UDI) and per département (each sample counted once per département); network size proxy = samples per year.
6. Output: small parquet tables in `data/` + `data/quality.json` (rows read/kept per year, shown in the app).

## Structure
```
app.py                 page config, cached loading, sidebar filters, sections
sections/              intro, overview, deep_dives, conclusions
utils/io.py            load_data(), fetch_and_cache(), licence text
utils/prep.py          cleaning, aggregation, rates, analysis tables
utils/viz.py           chart functions with a consistent style
data/                  processed parquet, geojson, raw/ (not shipped)
```

## Run
```bash
pip install -r requirements.txt
# 1. download dis-2021.zip … dis-2025.zip from the dataset page into data/raw/
# 2. first run builds data/*.parquet (a few minutes), next runs load the parquet only
streamlit run app.py
```
Deployment (Streamlit Community Cloud): push the repo **with** `data/*.parquet`, `data/quality.json` and `data/departements.geojson`, **without** `data/raw/`.

## Limitations
- A non-compliant sample is not necessarily a health risk (it can trigger a re-test or a restriction).
- Samples taken upstream are reported for every network they feed.
- Sampling frequency differs between networks; network size is a proxy, not the population served.
- Overseas départements are not on the map; the current year is incomplete and excluded.

## Demo video
<link to add>
