import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pygam import LinearGAM, s, f

def fit_lme(df: pd.DataFrame, pollutant: str):
    """
    LME with random intercept by Day.
    Fixed: AT_z, RH_z, Site, Period, Site:AT_z, Site:RH_z.
    """
    d = df.dropna(subset=[pollutant, 'AT_z', 'RH_z', 'Period']).copy()
    d['Site'] = d['site'].astype('category')
    d['Period'] = d['Period'].astype('category')
    formula = f"{pollutant} ~ AT_z + RH_z + C(Site) + C(Period) + C(Site):AT_z + C(Site):RH_z"
    model = smf.mixedlm(formula, d, groups=d['Day'])
    res = model.fit(method='lbfgs', disp=False)
    return res

def fit_gam(df: pd.DataFrame, pollutant: str):
    """
    GAM with smooths for AT, RH and categorical Site/Period as factors.
    """
    d = df.dropna(subset=[pollutant, 'AT', 'RH', 'Period']).copy()
    y = d[pollutant].values
    site_codes   = d['site'].astype('category').cat.codes.values
    period_codes = d['Period'].astype('category').cat.codes.values
    X = np.column_stack([d['AT'].values, d['RH'].values, site_codes, period_codes])
    gam = LinearGAM(s(0) + s(1) + f(2) + f(3)).fit(X, y)
    return gam

def fit_quantile(df: pd.DataFrame, pollutant: str, q=0.75):
    """
    τ-quantile regression (default τ=0.75).
    """
    d = df.dropna(subset=[pollutant, 'AT', 'RH', 'Period']).copy()
    d['Site'] = d['site'].astype('category')
    d['Period'] = d['Period'].astype('category')
    model = smf.quantreg(f"{pollutant} ~ AT + RH + C(Period) + C(Site)", d)
    res = model.fit(q=q)
    return res
