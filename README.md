# Is tap water equally safe across France ?

This project aims to visualize sanitary control of tap water in France, which is demonstrated with a Streamlit app. By the end, you will understand which department is the most concentrated with failed standards, how your commune is affected, and if you can still continue to drink tap water.

## Dataset
- Résultats du contrôle sanitaire de l'eau distribuée commune par commune, Ministère de la Santé (SISE-Eaux), data.gouv.fr
  https://www.data.gouv.fr/datasets/resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune
- Licence Ouverte / Open Licence 2.0
- Files used : national yearly zips `dis-YYYY.zip` from 2016 to 2026, each with `DIS_PLV` (samples), `DIS_RESULT` (analyses) and `DIS_COM_UDI` (commune/network links).
- Map contours : https://github.com/gregoiredavid/france-geojson (`data/departements.geojson`).

## Story
The targeted audience are the residents and local officials. I want to offer them, and myself, clarity on their daily water consumption. With this data, several questions need to be answered : 

1. How often does tap water fail the standards, and is it improving? 
2. Which departments are most affected ?
3. Are small networks more exposed ?
4. Where do nitrates exceed 50 mg/L?

To brings answers, you will find : context → national KPIs and trend → map and ranking of departments → network size → commune lookup → insights, implications and limitations. Regions are compared with map and ranking, and changes over time.

## Data work (`utils/prep.py`)

1. Read the text files directly from the zips
2. For the samples : strip values, drop rows without sample, network or commune code, remove duplicates, keep samples dated in the file's year, and derive the department from the main commune's INSEE code
3. Share of samples flagged `N` among samples flagged `C` or `N`, for bacteriological and chemical standards
4. For the nitrates, the parameter `NO3` from `DIS_RESULT`, then converted to numbers, one value per sample, is finally compared with the 50 mg/L limit.
5. Aggregation per network (UDI) and per department, network size proxy represent samples per year.
6. For the output, it is to expect small parquet tables in `data/` + `data/quality.json` with rows read and kept per year, which is shown in the app.

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
streamlit run app.py
```
Deployment with Streamlit Community Cloud : push the repo with `data/*.parquet`, `data/quality.json` and `data/departements.geojson`, and without `data/raw/`.

## Limitations

Although the data shows satisfying informations, there are still some points to acknowledge :
- A non-compliant sample is not necessarily a health risk
- Samples taken upstream are reported for every network they feed
- Sampling frequency differs between networks, and network size is a proxy, not the population served.
- Overseas departments are not on the map, since the current year is incomplete

## Video demonstration link :

https://drive.google.com/file/d/1tUpLzwdfLqelnLTMUK2gXj4TNNrJ0SY8/view?usp=sharing
