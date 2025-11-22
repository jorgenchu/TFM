import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.animation import FuncAnimation, PillowWriter
import seaborn as sns

# Configuración de visualización
plt.style.use('ggplot')
sns.set_palette("husl")

print("Cargando datos...")
files = ['data1.csv/data1.csv', 'data2.csv/data2.csv']
valid_files = [f for f in files if os.path.exists(f)]

if not valid_files:
    raise FileNotFoundError("No se encontraron los archivos de datos.")

# Leer datos con Dask
ddf = dd.read_csv(valid_files, assume_missing=True)

# Agregar columna de timestamp
ddf['Timestamp'] = dd.to_datetime(ddf['TimeInterval'], unit='ms')

# Seleccionar una semana aleatoria
print("Procesando datos temporales...")
with ProgressBar():
    df_sample = ddf.compute()

df_sample = df_sample.sort_values('Timestamp')
df_sample['DayOfWeek'] = df_sample['Timestamp'].dt.dayofweek
df_sample['Hour'] = df_sample['Timestamp'].dt.hour

# Filtrar una semana completa (lunes a domingo)
min_date = df_sample['Timestamp'].min()
max_date = df_sample['Timestamp'].max()

# Encontrar el primer lunes
days_to_monday = (7 - min_date.dayofweek) % 7
first_monday = min_date + pd.Timedelta(days=days_to_monday)
first_monday = first_monday.normalize()

# Calcular semanas disponibles
total_days = (max_date - first_monday).days
total_weeks = total_days // 7

if total_weeks < 1:
    print("Advertencia: Menos de una semana completa. Usando datos disponibles.")
    start_date = first_monday
else:
    # Seleccionar semana aleatoria
    import random
    random_week = random.randint(0, total_weeks - 1)
    start_date = first_monday + pd.Timedelta(weeks=random_week)

end_date = start_date + pd.Timedelta(days=7)

# Filtrar datos de la semana
week_df = df_sample[(df_sample['Timestamp'] >= start_date) & 
                     (df_sample['Timestamp'] < end_date)].copy()

print(f"Semana seleccionada: {start_date.date()} a {end_date.date()}")
print(f"Total de registros: {len(week_df)}")

# ============================================
# GRÁFICA 1: Distribución Espacial - INTERNET
# ============================================
print("\nCreando gráfica de distribución espacial - Internet...")

# Agregar datos por GridID para internet
spatial_internet = week_df.groupby('GridID')['internet'].sum().reset_index()
spatial_internet = spatial_internet.sort_values('internet', ascending=False)

# Crear gráfica
fig, ax = plt.subplots(figsize=(16, 10))

# Top 50 celdas con más tráfico de internet
top_cells = spatial_internet.head(50)

bars = ax.bar(range(len(top_cells)), top_cells['internet'], 
               color=plt.cm.viridis(np.linspace(0, 1, len(top_cells))))

ax.set_xlabel('Grid ID (Top 50 celdas)', fontsize=14, fontweight='bold')
ax.set_ylabel('Tráfico de Internet (MB)', fontsize=14, fontweight='bold')
ax.set_title(f'Distribución Espacial del Tráfico de Internet\\nSemana: {start_date.date()} - {end_date.date()}', 
             fontsize=16, fontweight='bold', pad=20)

# Añadir etiquetas de GridID
ax.set_xticks(range(len(top_cells)))
ax.set_xticklabels(top_cells['GridID'].astype(str), rotation=90, fontsize=8)

# Añadir valores en las barras
for i, (idx, row) in enumerate(top_cells.iterrows()):
    height = row['internet']
    ax.text(i, height, f'{height/1e6:.1f}M', 
            ha='center', va='bottom', fontsize=8, rotation=0)

# Grid
ax.grid(True, alpha=0.3, axis='y')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('distribucion_espacial_internet.png', dpi=300, bbox_inches='tight')
print("✓ Gráfica guardada: distribucion_espacial_internet.png")
plt.close()

# =====================================================
# GRÁFICA 2: Distribución Espacial - LLAMADAS IN/OUT
# =====================================================
print("\nCreando gráfica de distribución espacial - Llamadas...")

# Agregar datos por GridID para llamadas
week_df['total_calls'] = week_df['callin'] + week_df['callout']
spatial_calls = week_df.groupby('GridID').agg({
    'callin': 'sum',
    'callout': 'sum',
    'total_calls': 'sum'
}).reset_index()

spatial_calls = spatial_calls.sort_values('total_calls', ascending=False)

# Crear gráfica con barras apiladas
fig, ax = plt.subplots(figsize=(16, 10))

# Top 50 celdas
top_calls = spatial_calls.head(50)

x = np.arange(len(top_calls))
width = 0.8

# Barras apiladas
bars1 = ax.bar(x, top_calls['callin'], width, label='Llamadas Entrantes',
               color='#3498db', alpha=0.8)
bars2 = ax.bar(x, top_calls['callout'], width, bottom=top_calls['callin'],
               label='Llamadas Salientes', color='#e74c3c', alpha=0.8)

ax.set_xlabel('Grid ID (Top 50 celdas)', fontsize=14, fontweight='bold')
ax.set_ylabel('Número de Llamadas', fontsize=14, fontweight='bold')
ax.set_title(f'Distribución Espacial de Llamadas (In/Out)\\nSemana: {start_date.date()} - {end_date.date()}', 
             fontsize=16, fontweight='bold', pad=20)

# Etiquetas
ax.set_xticks(x)
ax.set_xticklabels(top_calls['GridID'].astype(str), rotation=90, fontsize=8)

# Leyenda
ax.legend(loc='upper right', fontsize=12)

# Grid
ax.grid(True, alpha=0.3, axis='y')
ax.set_axisbelow(True)

# Añadir valores totales
for i, (idx, row) in enumerate(top_calls.iterrows()):
    total = row['total_calls']
    ax.text(i, total, f'{total/1000:.1f}K', 
            ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('distribucion_espacial_llamadas.png', dpi=300, bbox_inches='tight')
print("✓ Gráfica guardada: distribucion_espacial_llamadas.png")
plt.close()

# =====================================================
# ANIMACIÓN GIF: Evolución durante la semana
# =====================================================
print("\nCreando animación GIF de evolución semanal...")

# Preparar datos por día y hora
week_df['Day'] = week_df['Timestamp'].dt.day_name()
week_df['DayNum'] = week_df['Timestamp'].dt.dayofweek

# Agregar por día, hora y GridID
hourly_spatial = week_df.groupby(['DayNum', 'Day', 'Hour', 'GridID']).agg({
    'internet': 'sum',
    'total_calls': 'sum',
    'smsin': 'sum',
    'smsout': 'sum'
}).reset_index()

# Crear figura para animación
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Evolución del Tráfico durante la Semana', fontsize=18, fontweight='bold')

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def update_frame(frame):
    """Actualizar frame de la animación"""
    day_num = frame // 24
    hour = frame % 24
    
    if day_num >= 7:
        return
    
    day_name = days_order[day_num]
    
    # Filtrar datos para este momento
    current_data = hourly_spatial[
        (hourly_spatial['DayNum'] == day_num) & 
        (hourly_spatial['Hour'] == hour)
    ]
    
    # Limpiar axes
    for ax in axes.flat:
        ax.clear()
    
    # Top 20 celdas para cada métrica
    top_n = 20
    
    # 1. Internet
    top_internet = current_data.nlargest(top_n, 'internet')
    if len(top_internet) > 0:
        axes[0, 0].barh(range(len(top_internet)), top_internet['internet'],
                        color=plt.cm.Blues(np.linspace(0.4, 1, len(top_internet))))
        axes[0, 0].set_yticks(range(len(top_internet)))
        axes[0, 0].set_yticklabels(top_internet['GridID'].astype(str), fontsize=8)
        axes[0, 0].set_xlabel('Tráfico (MB)', fontsize=10)
        axes[0, 0].set_title('Top 20 Celdas - Internet', fontsize=12, fontweight='bold')
        axes[0, 0].invert_yaxis()
    
    # 2. Llamadas
    top_calls = current_data.nlargest(top_n, 'total_calls')
    if len(top_calls) > 0:
        axes[0, 1].barh(range(len(top_calls)), top_calls['total_calls'],
                        color=plt.cm.Reds(np.linspace(0.4, 1, len(top_calls))))
        axes[0, 1].set_yticks(range(len(top_calls)))
        axes[0, 1].set_yticklabels(top_calls['GridID'].astype(str), fontsize=8)
        axes[0, 1].set_xlabel('Número de Llamadas', fontsize=10)
        axes[0, 1].set_title('Top 20 Celdas - Llamadas', fontsize=12, fontweight='bold')
        axes[0, 1].invert_yaxis()
    
    # 3. SMS In
    top_smsin = current_data.nlargest(top_n, 'smsin')
    if len(top_smsin) > 0:
        axes[1, 0].barh(range(len(top_smsin)), top_smsin['smsin'],
                        color=plt.cm.Greens(np.linspace(0.4, 1, len(top_smsin))))
        axes[1, 0].set_yticks(range(len(top_smsin)))
        axes[1, 0].set_yticklabels(top_smsin['GridID'].astype(str), fontsize=8)
        axes[1, 0].set_xlabel('SMS Entrantes', fontsize=10)
        axes[1, 0].set_title('Top 20 Celdas - SMS In', fontsize=12, fontweight='bold')
        axes[1, 0].invert_yaxis()
    
    # 4. SMS Out
    top_smsout = current_data.nlargest(top_n, 'smsout')
    if len(top_smsout) > 0:
        axes[1, 1].barh(range(len(top_smsout)), top_smsout['smsout'],
                        color=plt.cm.Purples(np.linspace(0.4, 1, len(top_smsout))))
        axes[1, 1].set_yticks(range(len(top_smsout)))
        axes[1, 1].set_yticklabels(top_smsout['GridID'].astype(str), fontsize=8)
        axes[1, 1].set_xlabel('SMS Salientes', fontsize=10)
        axes[1, 1].set_title('Top 20 Celdas - SMS Out', fontsize=12, fontweight='bold')
        axes[1, 1].invert_yaxis()
    
    # Añadir timestamp
    fig.text(0.5, 0.95, f'{day_name} - Hora: {hour:02d}:00', 
             ha='center', fontsize=14, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0, 1, 0.94])

# Crear animación (7 días × 24 horas = 168 frames)
# Para hacer el GIF más manejable, tomamos cada 2 horas
frames = list(range(0, 7 * 24, 2))  # 84 frames (cada 2 horas)

print(f"Generando {len(frames)} frames...")
anim = FuncAnimation(fig, update_frame, frames=frames, interval=200, repeat=True)

# Guardar como GIF
writer = PillowWriter(fps=5)  # 5 frames por segundo
anim.save('evolucion_semanal.gif', writer=writer, dpi=100)
print("✓ Animación guardada: evolucion_semanal.gif")
plt.close()

print("\n" + "="*60)
print("PROCESO COMPLETADO")
print("="*60)
print("\nArchivos generados:")
print("  1. distribucion_espacial_internet.png")
print("  2. distribucion_espacial_llamadas.png")
print("  3. evolucion_semanal.gif")
print("\n" + "="*60)
