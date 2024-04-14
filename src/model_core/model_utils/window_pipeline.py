import pandas as pd
import numpy as np
import yfinance as yf
from typing import Optional

from utils.logger import make_log
from window_generator import WindowGenerator


def data_init(ticker: str) -> Optional[pd.DataFrame]:
    #df = pd.read_csv(filepath)
    df = yf.download(ticker)
    if df.empty():
        make_log("WINDOW_PIPELINE", 40, "data_pipeline.log", f"Couldn't download data for {ticker}")
        raise TypeError
    columns_to_drop = df.columns[df.iloc[0] == 0.0]
    if columns_to_drop:
        df.drop(columns_to_drop, axis=1, inplace=True)
    return df


def feature_engineering(df) -> pd.DataFrame:
    date_time = pd.to_datetime(df.pop("Date"), utc=True)
    df["day_of_week"] = date_time.dt.dayofweek
    df["month_of_year"] = date_time.dt.month

    df["day_sin"] = np.sin(df["day_of_week"] * (2 * np.pi / 7))
    df["day_cos"] = np.cos(df["day_of_week"] * (2 * np.pi / 7))
    df["month_sin"] = np.sin((df["month_of_year"] - 1) * (2 * np.pi / 12))
    df["month_cos"] = np.cos((df["month_of_year"] - 1) * (2 * np.pi / 12))

    return df


def data_split(df):
    n = len(df)
    train_df = df[0 : int(n * 0.7)]
    val_df = df[int(n * 0.7) : int(n * 0.9)]
    test_df = df[int(n * 0.9) :]

    return train_df, val_df, test_df


def data_normalization(train_df, val_df, test_df):
    train_mean = train_df.mean()
    train_std = train_df.std()

    train_df = (train_df - train_mean) / train_std
    val_df = (val_df - train_mean) / train_std
    test_df = (test_df - train_mean) / train_std

    return train_df, val_df, test_df


def data_processing(ticker: str) -> Optional[WindowGenerator]:
    df = data_init(ticker)
    engineered_df = feature_engineering(df)
    train_df, val_df, test_df = data_split(engineered_df)
    train_df, val_df, test_df = data_normalization(train_df, val_df, test_df)

    return WindowGenerator(
        input_width=30,
        label_width=1,
        shift=1,
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        label_columns=["Close"],
    )
