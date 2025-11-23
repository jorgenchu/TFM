#!/bin/bash

# 1. Definir nombre y ruta del entorno (en HOME de Linux para evitar errores de permisos)
ENV_NAME="env_tfm"
ENV_PATH="$HOME/$ENV_NAME"

echo "--- Configurando entorno en Linux: $ENV_PATH ---"

# 2. Crear entorno virtual si no existe
if [ ! -d "$ENV_PATH" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv "$ENV_PATH"
else
    echo "El entorno ya existe."
fi

# 3. Activar entorno
source "$ENV_PATH/bin/activate"

# 4. Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
# Instalar requirements del proyecto actual
pip install -r requirements.txt

# 5. Instalar kernel de Jupyter
echo "Registrando kernel para Jupyter..."
pip install ipykernel
python -m ipykernel install --user --name="$ENV_NAME" --display-name "Python (WSL TFM)"

echo ""
echo "--- ¡LISTO! ---"
echo "Ahora sigue estos pasos:"
echo "1. Reinicia Jupyter Notebook (Ctrl+C y vuelve a lanzarlo)."
echo "2. Abre tu notebook 'prediction_model.ipynb'."
echo "3. En el menú de arriba, ve a 'Kernel' -> 'Change Kernel' -> 'Python (WSL TFM)'."
echo "4. Ejecuta las celdas."
