import json
import copy

base_notebook = 'prediction_model_new.ipynb'

targets = [
    {'name': 'sms_out', 'col': 'smsout'},
    {'name': 'call_in', 'col': 'callin'},
    {'name': 'call_out', 'col': 'callout'},
    {'name': 'internet', 'col': 'internet'}
]

with open(base_notebook, 'r', encoding='utf-8') as f:
    nb_content = json.load(f)

for target in targets:
    new_nb = copy.deepcopy(nb_content)
    target_name = target['name']
    target_col = target['col']
    
    print(f"Creating prediction_model_{target_name}.ipynb...")
    
    for cell in new_nb['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
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
                    elif "# smsin" in line: # Start of the filling block to replace
                        # We will replace the whole filling block
                        new_source.append(f"        # {target_col}\n")
                        new_source.append(f"        vals = df_pivot.loc[t, '{target_col}'].reindex(range(1, 10001), fill_value=0).values\n")
                        new_source.append(f"        data_tensor[idx, 0, :, :] = vals.reshape(100, 100)\n")
                        skip = True # Skip the original lines until we hit the print or end of loop
                    elif skip and ("print(f\"Tensor shape" in line or "data_tensor[idx, 1" in line):
                         if "print(f\"Tensor shape" in line:
                             skip = False
                             new_source.append(line)
                    elif not skip:
                        new_source.append(line)
                cell['source'] = new_source

            # 4. Ensure Plot Y-limit is set (if not already from base)
            if "plt.plot(train_losses" in source and "plt.ylim(0, 0.015)" not in source:
                 new_source = []
                 for line in cell['source']:
                     new_source.append(line)
                     if "plt.plot(train_losses" in line:
                         new_source.append("    plt.ylim(0, 0.015)\n")
                 cell['source'] = new_source
                 
            # 5. Remove unwanted plots (if not already removed)
            # The base notebook might already have them removed if modify_notebook.py ran, 
            # but let's double check.
            # Actually, the previous modify_notebook.py removed the cells entirely.
            # So if they are gone, we don't see them.
            # If they are present, we remove them.
            
    # Filter out cells that contain the unwanted plots if they still exist
    final_cells = []
    for cell in new_nb['cells']:
        source = ''.join(cell['source'])
        if 'Ground Truth vs Prediction' in source:
            continue
        if 'Mapa de Calor de Error Espacial' in source:
            continue
        final_cells.append(cell)
    new_nb['cells'] = final_cells

    output_filename = f'prediction_model_{target_name}.ipynb'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(new_nb, f, indent=1)
    print(f"Created {output_filename}")

print("All notebooks created.")
