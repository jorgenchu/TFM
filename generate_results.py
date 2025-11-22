import dask.dataframe as dd
import pandas as pd
import os

def generate_markdown_table(df, title):
    md = f"## {title}\n\n"
    md += df.to_markdown()
    md += "\n\n"
    return md

def main():
    print("Generating RESULTS.md...")
    
    files = ['data1.csv/data1.csv', 'data2.csv/data2.csv']
    services = ['smsin', 'smsout', 'callin', 'callout', 'internet']
    
    valid_files = [f for f in files if os.path.exists(f)]
    if not valid_files:
        print("No data files found.")
        return

    # Load Data
    ddf = dd.read_csv(valid_files, assume_missing=True)
    
    # 1. Spatial Analysis (Top GridIDs)
    print("Calculating Spatial Distribution...")
    spatial_task = ddf.groupby('GridID')[services].sum()
    spatial_df = spatial_task.compute()
    
    spatial_df['sms_total'] = spatial_df['smsin'] + spatial_df['smsout']
    spatial_df['call_total'] = spatial_df['callin'] + spatial_df['callout']
    
    # Top 10 Internet
    top_internet = spatial_df.nlargest(10, 'internet')[['internet']]
    
    # Top 10 SMS
    top_sms = spatial_df.nlargest(10, 'sms_total')[['sms_total']]
    
    # Top 10 Calls
    top_calls = spatial_df.nlargest(10, 'call_total')[['call_total']]
    
    # Write to Markdown
    with open('RESULTS.md', 'w') as f:
        f.write("# Resultados del Análisis\n\n")
        f.write("Este archivo contiene las tablas resumen generadas a partir del análisis de datos.\n\n")
        
        f.write(generate_markdown_table(top_internet, "Top 10 Celdas (GridID) - Tráfico Internet"))
        f.write(generate_markdown_table(top_sms, "Top 10 Celdas (GridID) - Tráfico SMS (Total)"))
        f.write(generate_markdown_table(top_calls, "Top 10 Celdas (GridID) - Tráfico Llamadas (Total)"))
        
    print("RESULTS.md generated successfully.")

if __name__ == "__main__":
    main()
