# src/stats.py
import os
from itertools import combinations
import numpy as np
import pandas as pd
import pingouin as pg
from statsmodels.stats.multitest import multipletests

from .data import load_prepare
from .config import CLIMATE, POLLUTANTS

# ---------- Correlations ----------

def corr_climate_pollutants(df: pd.DataFrame,
                            climate_cols=None,
                            pollutant_cols=None,
                            method="spearman",
                            partial=None,
                            by=None) -> pd.DataFrame:
    """
    Compute correlations between climate (X) and pollutants (Y).
    - method: 'spearman' (robust default) or 'pearson'
    - partial: list of covariates to control for (e.g., ['site', 'Period'])
    - by: optional column name to group by (e.g., 'site') and compute per-group
    Returns long-format DataFrame: [group, x, y, r, pval, ci95%, n]
    """
    climate_cols = [c for c in (climate_cols or CLIMATE) if c in df]
    pollutant_cols = [p for p in (pollutant_cols or POLLUTANTS) if p in df]

    groups = [None]
    if by and by in df:
        groups = df[by].dropna().unique().tolist()

    rows = []
    for g in groups:
        d = df if g is None else df[df[by] == g]
        for x in climate_cols:
            for y in pollutant_cols:
                sub = d[[x, y] + (partial or [])].dropna()
                if len(sub) < 3:
                    continue
                if partial:
                    res = pg.partial_corr(data=sub, x=x, y=y, covar=partial, method=method)
                    r = res.loc[0, "r"]; p = res.loc[0, "p-val"]; ci = res.loc[0, "CI95%"]
                else:
                    res = pg.corr(sub[x], sub[y], method=method)
                    r = res["r"].values[0]; p = res["p-val"].values[0]; ci = res["CI95%"].values[0]
                rows.append({
                    by if g is not None else "group": (g if g is not None else "ALL"),
                    "x": x, "y": y, "r": r, "pval": p, "ci95": ci, "n": len(sub)
                })
    out = pd.DataFrame(rows)
    return out.rename(columns={"group": by or "group"})

# ---------- Mann–Whitney U (pairwise) + Kruskal ----------

def _bootstrap_ci_median_diff(a, b, n_boot=2000, alpha=0.05, seed=42):
    rng = np.random.default_rng(seed)
    a = np.asarray(a); b = np.asarray(b)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = np.median(rng.choice(a, size=len(a), replace=True)) - np.median(rng.choice(b, size=len(b), replace=True))
    lo, hi = np.quantile(diffs, [alpha/2, 1 - alpha/2])
    return lo, hi

def mwu_pairwise(df: pd.DataFrame, y: str, group: str, padjust="fdr_bh"):
    """
    Pairwise Mann–Whitney U across all levels of `group`.
    Returns tidy DataFrame with U, p-unc, p-adj, RBC (rank-biserial), CLES, medians, and bootstrapped median-diff CI.
    """
    levels = [lvl for lvl in df[group].dropna().unique()]
    pairs = list(combinations(levels, 2))
    rows = []
    for a, b in pairs:
        xa = df.loc[df[group] == a, y].dropna()
        xb = df.loc[df[group] == b, y].dropna()
        if len(xa) == 0 or len(xb) == 0:
            continue
        res = pg.mwu(xa, xb, alternative="two-sided")  # returns U-val, p-val, RBC, CLES
        U = float(res.loc[0, "U-val"]); p = float(res.loc[0, "p-val"])
        rbc = float(res.loc[0, "RBC"]); cles = float(res.loc[0, "CLES"])
        med_a, med_b = float(np.median(xa)), float(np.median(xb))
        ci_lo, ci_hi = _bootstrap_ci_median_diff(xa, xb)
        rows.append({
            "group_a": a, "group_b": b, "y": y, "U": U, "p_unc": p,
            "RBC": rbc, "CLES": cles,
            "median_a": med_a, "median_b": med_b,
            "median_diff": med_a - med_b,
            "median_diff_CI95%": f"[{ci_lo:.3g}, {ci_hi:.3g}]",
            "n_a": int(len(xa)), "n_b": int(len(xb))
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out["p_adj"] = multipletests(out["p_unc"], method=padjust)[1]
    return out

def kruskal_omnibus(df: pd.DataFrame, y: str, group: str):
    """
    Kruskal–Wallis omnibus test across all levels of `group`.
    """
    return pg.kruskal(dv=y, between=group, data=df.dropna(subset=[y, group]))

# ---------- Convenience runner ----------

def run_all(in_csv: str, out_dir: str):
    """
    Load, prepare, then:
    - Correlations: overall and by-site (Spearman)
    - Mann–Whitney U: pairwise by Period and by Site, for each pollutant present
    - Kruskal omnibus: by Period and by Site
    Saves CSVs under out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)
    df = load_prepare(in_csv)

    # Correlations: ALL + by site
    corr_all = corr_climate_pollutants(df, method="spearman", partial=None, by=None)
    corr_by_site = corr_climate_pollutants(df, method="spearman", partial=None, by="site")
    corr_all.to_csv(os.path.join(out_dir, "corr_climate_pollutants_ALL.csv"), index=False)
    corr_by_site.to_csv(os.path.join(out_dir, "corr_climate_pollutants_by_site.csv"), index=False)

    # MWU & Kruskal per pollutant
    present_pollutants = [p for p in POLLUTANTS if p in df]
    mwu_period_all = []; mwu_site_all = []; kruskal_rows = []
    for y in present_pollutants:
        # Period comparisons (e.g., morning/afternoon/evening)
        if "Period" in df:
            mwu_period_all.append(mwu_pairwise(df, y=y, group="Period"))
            kper = kruskal_omnibus(df, y=y, group="Period"); kper["y"] = y; kper["group"] = "Period"
            kruskal_rows.append(kper)
        # Site comparisons
        if "site" in df:
            mwu_site_all.append(mwu_pairwise(df, y=y, group="site"))
            ks = kruskal_omnibus(df, y=y, group="site"); ks["y"] = y; ks["group"] = "site"
            kruskal_rows.append(ks)

    if mwu_period_all:
        pd.concat(mwu_period_all, ignore_index=True).to_csv(os.path.join(out_dir, "mwu_pairwise_byPeriod_allPollutants.csv"), index=False)
    if mwu_site_all:
        pd.concat(mwu_site_all, ignore_index=True).to_csv(os.path.join(out_dir, "mwu_pairwise_bySite_allPollutants.csv"), index=False)
    if kruskal_rows:
        pd.concat(kruskal_rows, ignore_index=True).to_csv(os.path.join(out_dir, "kruskal_omnibus.csv"), index=False)

    print(f"Saved results to: {out_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m src.stats <in.csv> <out_dir>")
        sys.exit(1)
    run_all(sys.argv[1], sys.argv[2])
