
import pandas as pd
import dask.dataframe as dd
import os

files = [os.path.join(r"c:\Users\jorge\Desktop\TFM DATA", f) for f in ['data1.csv/data1.csv', 'data2.csv/data2.csv']]

try:
    print("Reading dates...")
    df = dd.read_csv(files, usecols=['TimeInterval'])
    
    # Compute min and max
    min_ts = df['TimeInterval'].min().compute()
    max_ts = df['TimeInterval'].max().compute()
    
    start_date = pd.to_datetime(min_ts, unit='ms')
    end_date = pd.to_datetime(max_ts, unit='ms')
    
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")

except Exception as e:
    print(f"Error: {e}")
