import pandas as pd
import numpy as np
from .config import PERIOD_BOUNDS, TZ

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    ren = {
        'pm2_5':'PM25','pm25':'PM25','PM2.5':'PM25',
        'pm10':'PM10','PM_10':'PM10',
        'co':'CO','CO_ppm':'CO','co_ppm':'CO',
        'so2':'SO2','SO2_ppm':'SO2',
        'voc':'VOCs','VOC':'VOCs'
    }
    return df.rename(columns={k:v for k,v in ren.items() if k in df.columns})

def _ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if df['timestamp'].dt.tz is None:
        df['timestamp'] = df['timestamp'].dt.tz_localize(TZ, nonexistent='shift_forward', ambiguous='NaT')
    return df

def add_day_and_period(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Day'] = df['timestamp'].dt.date
    hour = df['timestamp'].dt.hour
    def _label(h):
        for name, start, end in PERIOD_BOUNDS:
            if start <= h < end:
                return name
        return np.nan
    df['Period'] = hour.map(_label)
    return df

def zscore_climate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ['AT','RH']:
        if col in df:
            mu, sd = df[col].mean(skipna=True), df[col].std(ddof=0, skipna=True)
            if sd and not np.isnan(sd) and sd>0:
                df[f'{col}_z'] = (df[col] - mu) / sd
            else:
                df[f'{col}_z'] = np.nan
    return df

def load_prepare(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _standardize_columns(df)
    df = _ensure_datetime(df)
    df = add_day_and_period(df)
    df = zscore_climate(df)
    # keep operational window 06–18
    df = df[df['timestamp'].dt.hour.between(6,17)]
    df = df[df['Period'].notna()]
    return df
