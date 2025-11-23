# TFM - Análisis de Tráfico Celular

Este repositorio contiene el código y los análisis para el Trabajo de Fin de Máster (TFM) sobre dinámicas de tráfico de telecomunicaciones. El proyecto analiza grandes volúmenes de datos de SMS, llamadas e Internet en la ciudad de Milán, explorando patrones temporales, distribución espacial y modelos de predicción basados en Deep Learning.

## 📂 Contenido del Repositorio

*   **`analysis.ipynb`**: Notebook de análisis exploratorio y visualización.
    *   **Carga eficiente** de datos masivos usando `Dask`.
    *   **Análisis temporal**: Selección automática de una semana aleatoria (Lunes-Domingo).
    *   **Análisis espacial 3D**: Visualización de la distribución del tráfico (SMS, Llamadas, Internet) en la cuadrícula urbana.
    *   **Animación Spatio-temporal**: Evolución dinámica del tráfico SMS.
*   **`prediction_model.ipynb`**: Notebook de implementación del modelo de predicción.
    *   **ST-DenseNet**: Red Neuronal Convolucional Densamente Conectada para predicción espacio-temporal.
    *   **Pipeline completo**: Preprocesamiento, construcción de tensores, entrenamiento (PyTorch) y evaluación.
*   **`requirements.txt`**: Lista de dependencias del proyecto.
*   **`RESULTS.md`**: Tablas resumen con los datos más relevantes del análisis.

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/jorgenchu/TFM.git
cd TFM
```

### 2. Requisitos Previos

*   Python 3.8+
*   Recomendado: GPU NVIDIA para el entrenamiento del modelo.

### 3. Instalar Dependencias

Para la mayoría de usuarios:

```bash
pip install -r requirements.txt
```

**Nota para usuarios con GPUs NVIDIA recientes (RTX 30/40/50 series):**
Para aprovechar la aceleración por hardware, se recomienda instalar PyTorch con soporte CUDA específico. 

Si tienes una **RTX 5080** (o arquitectura Blackwell/Hopper reciente), instala la versión Nightly:

```bash
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu124
```

### 4. Configuración Avanzada GPU (RTX 50 Series / Blackwell)

Si tienes una tarjeta gráfica muy reciente (ej. RTX 5080) y Windows, es probable que PyTorch no detecte la GPU nativamente debido a la arquitectura `sm_120`. Para usar la GPU, debes usar **WSL2 (Windows Subsystem for Linux)**:

1.  **Abrir WSL**: Abre una terminal de Ubuntu/WSL.
2.  **Navegar al proyecto**:
    ```bash
    cd /mnt/c/Users/jorge/Desktop/TFM\ DATA
    ```
3.  **Instalar dependencias**:
    ```bash
    sudo apt update
    sudo apt install -y python3-pip python3-venv
    pip3 install -r requirements.txt --break-system-packages
    ```
4.  **Lanzar Jupyter desde WSL**:
    ```bash
    python3 -m notebook
    ```
5.  **Abrir el enlace**: Copia la URL que aparece en la terminal (ej. `http://localhost:8888/?token=...`) en tu navegador de Windows.

**Nota:** Si ejecutas el notebook desde el CMD de Windows, usará la **CPU** (más lento).

## ▶️ Uso

1.  Coloca los archivos de datos (`data1.csv`, `data2.csv`) en las carpetas correspondientes.
2.  Inicia Jupyter Notebook:
    ```bash
    jupyter notebook
    ```
3.  Ejecuta `analysis.ipynb` para ver las estadísticas y visualizaciones.
4.  Ejecuta `prediction_model.ipynb` para entrenar y evaluar el modelo de predicción.

## 🧠 Modelo de Predicción (ST-DenseNet)

El proyecto implementa una arquitectura de **Deep Learning** para predecir el tráfico de SMS:
*   **Entrada**: Tensores 4D que capturan la dependencia de **Proximidad** (últimas horas) y **Periodo** (misma hora de días anteriores).
*   **Arquitectura**: Dos ramas de CNN con bloques densos (Dense Blocks) que aprenden características espacio-temporales, fusionadas mediante una matriz paramétrica.
*   **Objetivo**: Minimizar el Error Cuadrático Medio (MSE) en la predicción del tráfico futuro.

## 🛠️ Tecnologías Utilizadas

*   **Python**: Lenguaje principal.
*   **PyTorch**: Framework de Deep Learning.
*   **Dask**: Procesamiento Big Data.
*   **Pandas & NumPy**: Manipulación de datos.
*   **Matplotlib**: Visualización 2D/3D y animaciones.
