import pandas as pd
from datetime import datetime

def parse_date(date_str):
    if not date_str or date_str.strip() == "":
        return None
    date_str = date_str.split(" ")[0]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%b %d", "%d %b %Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    return None

def clean_currency(val):
    if not val or val.strip() == "":
        return 0.0
    val = str(val).replace(",", "").replace("Rs", "").replace(" ", "")
    try:
        return float(val)
    except:
        return 0.0

def clean_deals(df):
    df = df.copy()
    # Try to find a column that looks like a value column
    value_col = None
    for col in df.columns:
        if "value" in col.lower() or "amount" in col.lower():
            value_col = col
            break
    if value_col:
        df[value_col] = df[value_col].apply(clean_currency)
    # Handle date columns
    for col in df.columns:
        if "date" in col.lower():
            df[col] = df[col].apply(parse_date)
    return df

def clean_work_orders(df):
    df = df.copy()
    for col in ["Probable Start Date", "Probable End Date", "Collection Date"]:
        if col in df.columns:
            df[col] = df[col].apply(parse_date)
    for col in ["Amount Excl GST", "Billed Value Excl GST"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_currency)
    return df