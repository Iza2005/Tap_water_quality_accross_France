import json
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PLV_COLS = {"cdreseau", "inseecommuneprinc", "referenceprel", "dateprel",
            "plvconformitebacterio", "plvconformitechimique"}
COM_COLS = {"inseecommune", "nomcommune", "cdreseau", "nomreseau"}
RES_COLS = {"referenceprel", "cdparametresiseeaux", "valtraduite"}
NITRATE_CODE = "NO3"      # SISE-Eaux code for nitrates
NITRATE_LIMIT = 50.0      # regulatory limit, mg/L
SIZE_BINS = [0, 5, 20, 100, np.inf]
SIZE_LABELS = ["1-5", "6-20", "21-100", ">100"]


# Raw reading ---------------------------------------------------------------------
def _read(zf, name, cols, chunksize=None):
    with zf.open(name) as f:
        head = f.read(200_000)
    head = head[: head.rfind(b"\n")]
    try:
        head.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        enc = "latin-1"
    first = head.decode(enc).splitlines()[0]
    sep = max([",", ";", "\t", "|"], key=first.count)
    found = {c.strip().strip('"').lower() for c in first.split(sep)}
    if not cols <= found:
        raise ValueError(f"{name}: missing columns {cols - found}. Found : {sorted(found)}")
    reader = pd.read_csv(zf.open(name), sep=sep, encoding=enc, dtype=str,
                         usecols=lambda c: c.strip().lower() in cols, chunksize=chunksize)
    clean = lambda d: d.rename(columns=lambda c: c.strip().lower())
    return (clean(c) for c in reader) if chunksize else clean(reader)


def _files(zf, key):
    return [n for n in zf.namelist()
            if key in Path(n).name.upper() and n.lower().endswith((".txt", ".csv"))]


def dept_from_insee(code):
    code = code.str.strip().str.zfill(5)
    return code.str[:3].where(code.str.startswith("97"), code.str[:2])


def _conformity(df):
    for col, p in [("plvconformitebacterio", "bact"), ("plvconformitechimique", "chim")]:
        v = df[col].fillna("").str.strip().str.upper()
        df[f"n_{p}"] = v.isin(["C", "N"]).astype(int)   # C = compliant, N = non-compliant
        df[f"nc_{p}"] = v.eq("N").astype(int)
    return df


def _agg(df, keys):
    return df.groupby(keys, as_index=False).agg(
        n=("referenceprel", "nunique"), n_bact=("n_bact", "sum"), nc_bact=("nc_bact", "sum"),
        n_chim=("n_chim", "sum"), nc_chim=("nc_chim", "sum"),
        no3_n=("no3", "count"), no3_mean=("no3", "mean"), no3_max=("no3", "max"),
        no3_over=("no3_over", "sum"))


def build_year(zip_path, year, log):
    with zipfile.ZipFile(zip_path) as zf:
        plv = pd.concat([_read(zf, n, PLV_COLS) for n in _files(zf, "PLV")])
        com = pd.concat([_read(zf, n, COM_COLS) for n in _files(zf, "COM_UDI")])
        no3 = pd.concat(c[c["cdparametresiseeaux"].str.strip().eq(NITRATE_CODE)]
                        for n in _files(zf, "RESULT")
                        for c in _read(zf, n, RES_COLS, chunksize=1_000_000))

    # Samples (PLV)---------------------------------------------
    q = {"plv_raw": len(plv)}
    plv = plv.apply(lambda s: s.str.strip())
    plv = plv.dropna(subset=["referenceprel", "cdreseau", "inseecommuneprinc"])
    plv = plv.drop_duplicates(["referenceprel", "cdreseau"])
    plv = plv[pd.to_datetime(plv["dateprel"], errors="coerce").dt.year.eq(year)]
    plv["dept"] = dept_from_insee(plv["inseecommuneprinc"])
    plv = _conformity(plv)
    q["plv_kept"] = len(plv)

    # Nitrates = numeric conversion with one value per sample ---------------------
    no3["no3"] = pd.to_numeric(no3["valtraduite"].str.replace(",", "."), errors="coerce")
    no3 = no3.dropna(subset=["no3"]).query("no3 >= 0")
    no3 = no3.groupby("referenceprel", as_index=False)["no3"].max()
    q["no3_samples"] = len(no3)
    plv = plv.merge(no3, on="referenceprel", how="left")
    plv["no3_over"] = (plv["no3"] > NITRATE_LIMIT).astype(int)

    # Per network (UDI) and per department -------------------------------------
    udi = _agg(plv, ["cdreseau", "dept"]).assign(year=year)
    dept = _agg(plv.drop_duplicates(["referenceprel", "dept"]), ["dept"]).assign(year=year)
    com = com.apply(lambda s: s.str.strip()).dropna(subset=["inseecommune", "cdreseau"])
    com = com.drop_duplicates(["inseecommune", "cdreseau"]).assign(year=year)
    log[str(year)] = q
    return udi, dept, com


def build_processed(raw_dir, out_dir):
    """raw zips -> data/*.parquet + quality.json (run once, ~minutes)."""
    zips = sorted(Path(raw_dir).glob("dis-*.zip"))
    zips = [z for z in zips if z.stem.split("-")[1].isdigit() and len(z.stem.split("-")) == 2]
    if not zips:
        raise FileNotFoundError(f"No dis-YYYY.zip in {raw_dir}. See README.")
    log = {}
    parts = [build_year(z, int(z.stem.split("-")[1]), log) for z in zips]
    for i, name in enumerate(["udi_year", "dept_year", "com_udi"]):
        pd.concat([p[i] for p in parts]).to_parquet(Path(out_dir) / f"{name}.parquet", index=False)
    (Path(out_dir) / "quality.json").write_text(json.dumps(log, indent=2))


# Analysis tables------------------------------------------------
def add_rates(df):
    df = df.copy()
    pct = lambda a, b: (100 * df[a] / df[b].replace(0, np.nan)).round(2)
    df["pct_bact"] = pct("nc_bact", "n_bact")
    df["pct_chim"] = pct("nc_chim", "n_chim")
    df["pct_no3"] = pct("no3_over", "no3_n")
    return df


def sum_by(df, keys):
    cols = ["n", "n_bact", "nc_bact", "n_chim", "nc_chim", "no3_n", "no3_over"]
    return add_rates(df.groupby(keys, as_index=False)[cols].sum())


def make_tables(raw, geo):
    names = {f["properties"]["code"]: f["properties"]["nom"] for f in geo["features"]}
    dept = add_rates(raw["dept_year"])
    dept["dept_name"] = dept["dept"].map(names).fillna(dept["dept"])
    udi = add_rates(raw["udi_year"])
    udi["size"] = pd.cut(udi["n"], SIZE_BINS, labels=SIZE_LABELS)  # samples/year = population served
    com = raw["com_udi"]
    com = com[com["year"] == com["year"].max()]
    return {
        "dept": dept,
        "national": sum_by(dept, ["year"]),
        "by_size": sum_by(udi, ["year", "size"]),
        "udi": udi,
        "com": com,
        "quality": raw["quality"],
    }
