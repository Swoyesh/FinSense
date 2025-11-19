import pandas as pd
import numpy as np
from io import BytesIO

def clean_transactions(df):
    df = df[df[['Dr.', 'Cr.', 'Balance (NPR)']].notna().any(axis=1)]
    df = df[~df["Description"].str.contains("Total|Summary", case=False, na=False)]
    df = df.replace({pd.NaT: None, np.nan: None, 'nan': None})
    return df

def read_excel_dynamic(file_bytes: bytes):
    preview_df = pd.read_excel(BytesIO(file_bytes), header=None, nrows=15)

    header_row = None
    for i, row in preview_df.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        if any(keyword in row_str for keyword in ["description", "date", "dr.", "cr.", "balance"]):
            header_row = i
            break

    if header_row is None:
        header_row = 0

    df = pd.read_excel(BytesIO(file_bytes), header=header_row)

    return df