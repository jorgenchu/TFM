import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime

# Setup
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (15, 8)

# Paths
files = ['data1.csv/data1.csv', 'data2.csv/data2.csv']
services = ['smsin', 'smsout', 'callin', 'callout', 'internet']
valid_files = [f for f in files if os.path.exists(f)]

if not valid_files:
    print(f"Error: Data files not found. Searched for: {files}")
    print(f"Current Directory: {os.getcwd()}")
    exit(1)

print(f"Loading data from {valid_files}...")
ddf = dd.read_csv(valid_files, assume_missing=True)

# --- 1. PRE-PROCESSING (Global) ---
print("Aggregating temporal data (Global)...")
ddf_time = ddf[['TimeInterval'] + services]
agg_task = ddf_time.groupby('TimeInterval')[services].sum()
with ProgressBar():
    final_df = agg_task.compute()

final_df = final_df.reset_index()
final_df['Timestamp'] = pd.to_datetime(final_df['TimeInterval'], unit='ms')
final_df.set_index('Timestamp', inplace=True)
final_df = final_df.sort_index()

# Add Total Column
final_df['Total'] = final_df[services].sum(axis=1)

# --- 2. HISTORIC TOP ZONES ---
print("\n--- Analysing Historic Top Zones ---")
ddf['total_load'] = ddf['internet'] + ddf['smsin'] + ddf['smsout'] + ddf['callin'] + ddf['callout']
global_zone_task = ddf.groupby('GridID')['total_load'].sum()
with ProgressBar():
    global_zone_df = global_zone_task.compute()

top_20_zones = global_zone_df.nlargest(20)

plt.figure(figsize=(14, 7))
top_20_zones.plot(kind='bar', color='teal', alpha=0.8)
plt.title('Top 20 Zonas con Mayor Tráfico Histórico (Acumulado)')
plt.ylabel('Volumen de Tráfico Total')
plt.xlabel('GridID')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('imagenes/top_zones_historic.png')
print("Saved: imagenes/top_zones_historic.png")

# --- 3. DAILY PEAKS & THRESHOLD ---
print("\n--- Analysing Daily Peaks ---")
daily_agg = final_df.resample('D')['Total'].sum()

mean_val = daily_agg.mean()
std_val = daily_agg.std()
threshold = mean_val + 2 * std_val
top_5_days = daily_agg.nlargest(5)

print(f"Daily Threshold (Mean + 2*Std): {threshold:,.2f}")
print("Top 5 Days:")
print(top_5_days)

plt.figure(figsize=(15, 6))
plt.plot(daily_agg.index, daily_agg, label='Tráfico Total Diario', color='steelblue')
plt.axhline(threshold, color='red', linestyle='--', linewidth=2, label=f'Umbral ({threshold:,.0f})')
plt.scatter(top_5_days.index, top_5_days, color='red', s=100, zorder=5, label='Picos Maximos')
plt.title('Evolución Diaria del Tráfico: Detección de Picos')
plt.legend()
plt.tight_layout()
plt.savefig('imagenes/daily_peaks_threshold.png')
print("Saved: imagenes/daily_peaks_threshold.png")

# --- 4. RELATIONAL: ZONES IN TOP DAYS ---
print("\n--- Analysing Zones in Top Days ---")
top_dates_str = top_5_days.index.strftime('%Y-%m-%d').tolist()

# Create DateStr column in Dask (efficiently)
ddf['DateStr'] = dd.to_datetime(ddf['TimeInterval'], unit='ms').dt.strftime('%Y-%m-%d')
ddf_peaks = ddf[ddf['DateStr'].isin(top_dates_str)]

# Group by Date, GridID
peak_zones_task = ddf_peaks.groupby(['DateStr', 'GridID'])['total_load'].sum()
with ProgressBar():
    peak_zones_df = peak_zones_task.compute().reset_index()

# Prepare Stacked Bar Plot
plot_data = []
for date_str in top_dates_str:
    day_data = peak_zones_df[peak_zones_df['DateStr'] == date_str]
    if day_data.empty: continue
    
    day_sorted = day_data.sort_values('total_load', ascending=False)
    top_curr = day_sorted.head(5)
    others = day_sorted.iloc[5:]['total_load'].sum()
    
    row = {'Date': date_str, 'Others': others}
    for _, z in top_curr.iterrows():
        row[f"Zone {int(z['GridID'])}"] = z['total_load']
    plot_data.append(row)

if plot_data:
    df_plot = pd.DataFrame(plot_data).set_index('Date')
    df_plot.plot(kind='bar', stacked=True, figsize=(12, 7), colormap='tab20')
    plt.title('Top 5 Zonas Contribuyentes en Días Pico')
    plt.ylabel('Volumen Total')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('imagenes/top_days_zones.png')
    print("Saved: imagenes/top_days_zones.png")

# --- 5. HOURLY ANALYSIS & ZONES ---
print("\n--- Analysing Hourly Profile and Zones ---")
final_df['Hour'] = final_df.index.hour
hourly_avg = final_df.groupby('Hour')['Total'].mean()

top_hours = hourly_avg.nlargest(5).index.tolist()
print(f"Top 5 Hours (Avg): {top_hours}")

plt.figure(figsize=(10, 5))
hourly_avg.plot(kind='bar', color='orange', alpha=0.7)
plt.title('Perfil Horario Promedio (0-23h)')
plt.ylabel('Tráfico Promedio')
plt.xlabel('Hora del Día')
plt.savefig('imagenes/hourly_profile.png')
print("Saved: imagenes/hourly_profile.png")

# Zones in Top 3 Hours
print(f"Analysing Zones for Top 3 Hours: {top_hours[:3]}...")
ddf['Hour'] = dd.to_datetime(ddf['TimeInterval'], unit='ms').dt.hour
ddf_hours = ddf[ddf['Hour'].isin(top_hours[:3])]

hour_zones_task = ddf_hours.groupby(['Hour', 'GridID'])['total_load'].sum()
with ProgressBar():
    hour_zones_df = hour_zones_task.compute().reset_index()

plot_data_h = []
sorted_top_hours = sorted(top_hours[:3]) # Order by hour
for h in sorted_top_hours:
    h_data = hour_zones_df[hour_zones_df['Hour'] == h]
    if h_data.empty: continue
    
    h_sorted = h_data.sort_values('total_load', ascending=False)
    top_curr = h_sorted.head(5)
    others = h_sorted.iloc[5:]['total_load'].sum()
    
    row = {'Hour': f"{h}:00", 'Others': others}
    for _, z in top_curr.iterrows():
        row[f"Zone {int(z['GridID'])}"] = z['total_load']
    plot_data_h.append(row)

if plot_data_h:
    df_plot_h = pd.DataFrame(plot_data_h).set_index('Hour')
    df_plot_h.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='viridis')
    plt.title(f'Top Zonas en las Horas Pico')
    plt.ylabel('Volumen Acumulado (Muestra)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('imagenes/top_hours_zones.png')
    print("Saved: imagenes/top_hours_zones.png")

# --- 6. REPORT GENERATION ---
report_content = f"""# Reporte de Análisis de Tráfico: Zonas, Días y Horas
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Top Zonas Históricas
Las zonas (GridID) que más tráfico han acumulado en todo el histórico.
![Top Zones](imagenes/top_zones_historic.png)

## 2. Picos de Tráfico Diario
Evolución del tráfico diario total con umbral (Mean + 2*Std).
- **Umbral calculado**: {threshold:,.0f}
- **Días Pico**: {', '.join(top_dates_str)}
![Daily Peaks](imagenes/daily_peaks_threshold.png)

## 3. Desglose de Zonas en Días Pico
¿Qué zonas contribuyeron más al tráfico en los días de mayor demanda?
![Top Days Zones](imagenes/top_days_zones.png)

## 4. Perfil Horario
Tráfico promedio por hora del día.
![Hourly Profile](imagenes/hourly_profile.png)

## 5. Top Zonas en Horas Pico
Zonas más activas durante las horas de mayor tráfico ({', '.join(map(str, top_hours[:3]))}:00).
![Top Hours Zones](imagenes/top_hours_zones.png)
"""

with open('analysis_report_advanced.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

print("\nSuccess! Report generated: analysis_report_advanced.md")
