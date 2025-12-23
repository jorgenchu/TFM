
import requests
import pandas as pd
import os

# Milan Coordinates
LAT = 45.4642
LON = 9.1900
START_DATE = "2013-10-31"
END_DATE = "2014-01-01"

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LAT,
    "longitude": LON,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": "precipitation,rain,weathercode",
    "timezone": "Europe/Berlin" # Milan timezone
}

output_file = r"c:\Users\jorge\Desktop\TFM DATA\analisis\clima_milano.csv"

try:
    print("Requesting weather data...")
    response = requests.get(URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    hourly = data['hourly']
    df = pd.DataFrame({
        'time': pd.to_datetime(hourly['time']),
        'precipitation': hourly['precipitation'],
        'rain': hourly['rain'],
        'weathercode': hourly['weathercode']
    })
    
    df.to_csv(output_file, index=False)
    print(f"Success: Weather data saved to {output_file}")
    print(df.head())

except Exception as e:
    print(f"Error: {e}")
