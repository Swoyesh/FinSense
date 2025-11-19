import pandas as pd
import numpy as np

def cleaner_function(df):
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["date_time", "amount", "category"])
    
    if 'type' in df.columns:
        df = df[df['type'] == 'expense'].copy()
    
    df["date_time"] = pd.to_datetime(df["date_time"])
    df.set_index("date_time", inplace=True)
    df.sort_index(inplace=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['amount'])
    
    return df


def reshaping(df):
    monthly = df.groupby([pd.Grouper(freq="M"), "category"])["amount"].sum().unstack(fill_value=0)
    
    for cat in monthly.columns:
        if monthly[cat].sum() == 0:
            monthly.drop(cat, axis=1, inplace=True)
    
    monthly['Total'] = monthly.sum(axis=1)
    
    for col in monthly.columns:
        if col != 'Total':
            monthly[f"{col} %"] = (monthly[col] / monthly['Total'] * 100).fillna(0)
    
    monthly['Total %'] = 100.0
    
    return monthly