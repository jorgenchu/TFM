import json

notebook_path = 'prediction_model_new.ipynb'
target_col = 'smsin'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []
for cell in nb['cells']:
    source = ''.join(cell['source'])
    
    if cell['cell_type'] == 'code':
        # 1. Modify NB_FLOW
        if 'NB_FLOW = 2' in source:
            cell['source'] = [line.replace('NB_FLOW = 2', 'NB_FLOW = 1') for line in cell['source']]
        
        # 2. Modify cols selection
        if "cols = ['Hour', 'GridID', 'smsin', 'smsout']" in source:
            new_source = []
            for line in cell['source']:
                if "cols = ['Hour', 'GridID', 'smsin', 'smsout']" in line:
                    new_source.append(f"cols = ['Hour', 'GridID', '{target_col}']\n")
                elif "agg_task = ddf.groupby(['Hour', 'GridID'])[['smsin', 'smsout']].sum()" in line:
                    new_source.append(f"agg_task = ddf.groupby(['Hour', 'GridID'])[['{target_col}']].sum()\n")
                else:
                    new_source.append(line)
                    
            cell['source'] = new_source
            
        # 3. Modify Tensor Construction
        if "data_tensor = np.zeros((len(time_range), 2, 100, 100)" in source:
            new_source = []
            skip = False
            for line in cell['source']:
                if "data_tensor = np.zeros((len(time_range), 2, 100, 100)" in line:
                    new_source.append(f"    data_tensor = np.zeros((len(time_range), 1, 100, 100), dtype=np.float32)\n")
                elif "df_pivot = df_agg.pivot_table" in line:
                    new_source.append(f"    df_pivot = df_agg.pivot_table(index='Hour', columns='GridID', values=['{target_col}'], fill_value=0)\n")
                elif "# smsin" in line: # Start of the filling block
                    new_source.append(f"        # {target_col}\n")
                    new_source.append(f"        vals = df_pivot.loc[t, '{target_col}'].reindex(range(1, 10001), fill_value=0).values\n")
                    new_source.append(f"        data_tensor[idx, 0, :, :] = vals.reshape(100, 100)\n")
                    skip = True 
                elif skip and ("print(f\"Tensor shape" in line or "data_tensor[idx, 1" in line):
                        if "print(f\"Tensor shape" in line:
                            skip = False
                            new_source.append(line)
                elif not skip:
                    new_source.append(line)
            cell['source'] = new_source

    elif cell['cell_type'] == 'markdown':
        # Update Section 5
        if '## 5. Interpretación de Resultados' in source:
            cell['source'] = [
                "## 5. Interpretación de Resultados\n",
                "\n",
                "### 5.1. Métricas de Evaluación\n",
                "Para evaluar el rendimiento, primero se **desnormalizan** las predicciones para volver a la escala original de tráfico (número de SMS).\n",
                "\n",
                "$$ \\hat{X}_{orig} = \\hat{X}_{norm} \\cdot (Max - Min) + Min $$\n",
                "\n",
                "Se calculan las siguientes métricas:\n",
                "\n",
                "1.  **RMSE (Root Mean Squared Error)**: Error cuadrático medio. Penaliza más los errores grandes.\n",
                "    $$ RMSE = \\sqrt{\\frac{1}{M} \\sum (\\hat{x}_{orig} - x_{orig})^2} $$\n",
                "\n",
                "2.  **MAE (Mean Absolute Error)**: Error absoluto medio. Es más robusto a outliers y fácil de interpretar (error promedio en SMS).\n",
                "    $$ MAE = \\frac{1}{M} \\sum |\\hat{x}_{orig} - x_{orig}| $$\n",
                "\n",
                "3.  **R2 Score**: Coeficiente de determinación. Indica qué tan bien las predicciones se ajustan a los datos reales (1.0 es perfecto).\n",
                "\n",
                "### 5.2. Visualización\n",
                "*   **Serie Temporal**: Comparación visual de la predicción y la realidad a lo largo del tiempo para una celda específica.\n"
            ]

    new_cells.append(cell)

nb['cells'] = new_cells

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook converted to SMS IN and text updated.")
