import os

def replace_in_file(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes for {filepath}")

base_path = r"C:\Users\jorge\Desktop\TFM DATA\Predicciones"

# 1. ConvLSTM.ipynb
# Replaces incorrect model name ST-GAT with Time-Aware ConvLSTM
# Fixes Learning Rate visual mismatch (code 0.01 vs 0.001 usage)
# Removes confusing SMS references
convlstm_replacements = {
    "Optimized Architecture: Time-Aware ST-GAT": "Time-Aware ConvLSTM",
    "Time-Aware ST-GAT": "Time-Aware ConvLSTM",
    "NB_FLOW = 1      # Canales (Internet In, Internet Out)": "NB_FLOW = 1      # Canales (Total Internet Traffic)",
    "LEARNING_RATE = 0.01": "LEARNING_RATE = 0.001",
    "ST-GNN": "ConvLSTM",
    "# Seleccionar columnas de interés (SMS)": "# Seleccionar columnas de interés (Internet Traffic)",
    "volumen de tráfico de SMS": "volumen de tráfico de Internet",
    "representa `smsin` y el canal 1 representa `smsout`": "representa `internet`"
}
replace_in_file(os.path.join(base_path, "ConvLSTM.ipynb"), convlstm_replacements)

# 2. CNN_Internet.ipynb
# Replaces ST-DenseNet with Standard ST-CNN
# Replaces Densely Connected with Sequential/Standard
# SMS -> Internet Traffic
cnn_replacements = {
    "ST-DenseNet": "Standard ST-CNN",
    "Densely Connected": "Standard",
    "NB_FLOW = 1      # Canales (SMS In, SMS Out)": "NB_FLOW = 1      # Canales (Total Internet Traffic)",
    "# Seleccionar columnas de interés (SMS)": "# Seleccionar columnas de interés (Internet Traffic)",
    "volumen de tráfico de SMS": "volumen de tráfico de Internet",
    "representa `smsin` y el canal 1 representa `smsout`": "representa `internet`",
    "(SMS)": "(Internet Traffic)"
}
replace_in_file(os.path.join(base_path, "CNN_Internet.ipynb"), cnn_replacements)

# 3. CNN_Dense_Internet.ipynb
# Updates SMS -> Internet Traffic
dense_replacements = {
    "NB_FLOW = 1      # Canales (SMS In, SMS Out)": "NB_FLOW = 1      # Canales (Total Internet Traffic)",
    "# Seleccionar columnas de interés (SMS)": "# Seleccionar columnas de interés (Internet Traffic)",
    "volumen de tráfico de SMS": "volumen de tráfico de Internet",
    "representa `smsin` y el canal 1 representa `smsout`": "representa `internet`",
    "(SMS)": "(Internet Traffic)"
}
replace_in_file(os.path.join(base_path, "CNN_Dense_Internet.ipynb"), dense_replacements)
