import json
from pathlib import Path
import pandas as pd
import requests
from utils.prep import build_processed

DATA = Path(__file__).resolve().parents[1] / "data"
DATASET_URL = ("https://www.data.gouv.fr/datasets/"
               "resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune")
GEO_URL = ("https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
           "master/departements-version-simplifiee.geojson")
LICENSE_TEXT = ("Source : Ministère de la Santé – SISE-Eaux, “Résultats du contrôle sanitaire de "
                "l'eau distribuée commune par commune”, data.gouv.fr – Licence Ouverte 2.0.")
TABLES = ["udi_year", "dept_year", "com_udi"]


def load_data():
    if not all((DATA / f"{t}.parquet").exists() for t in TABLES):
        build_processed(DATA / "raw", DATA)
    raw = {t: pd.read_parquet(DATA / f"{t}.parquet") for t in TABLES}
    raw["quality"] = json.loads((DATA / "quality.json").read_text())
    return raw


def fetch_and_cache(url=GEO_URL, path=DATA / "departements.geojson"):
    if not path.exists():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        path.write_text(r.text, encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))
