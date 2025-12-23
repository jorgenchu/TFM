import json
import os

filepath = r"C:\Users\jorge\Desktop\TFM DATA\Predicciones\ConvLSTM.ipynb"

if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if saving code already exists to avoid duplicates
    source_code = [cell.get('source', []) for cell in data['cells']]
    flat_source = [line for field in source_code for line in field]
    if any("torch.save" in line for line in flat_source):
        print("Model saving code already exists.")
    else:
        new_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "\n",
                "# --- GUARDADO DEL MODELO ---\n",
                "model_save_path = 'convlstm_model.pth'\n",
                "torch.save(model.state_dict(), model_save_path)\n",
                "print(f\"Modelo guardado exitosamente en: {model_save_path}\")"
            ]
        }
        
        data['cells'].append(new_cell)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1)
        print("Added model saving cell to ConvLSTM.ipynb")
else:
    print(f"File not found: {filepath}")
