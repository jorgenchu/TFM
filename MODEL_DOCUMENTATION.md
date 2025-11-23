# Documentación del Modelo de Predicción de Tráfico (ST-DenseNet)

Este documento detalla la arquitectura, formulación matemática y metodología utilizada en el modelo de predicción de tráfico celular (SMS) para la ciudad de Milán. El modelo se basa en una arquitectura **ST-DenseNet** (Spatio-Temporal Densely Connected Convolutional Network).

## 1. Definición del Problema

El objetivo es predecir el volumen de tráfico de SMS (entrante y saliente) para cada celda de una cuadrícula de $100 \times 100$ en la ciudad de Milán para el siguiente intervalo de tiempo, basándose en datos históricos.

Sea $X_t \in \mathbb{R}^{2 \times 100 \times 100}$ el tensor de tráfico en el tiempo $t$, donde el canal 0 representa `smsin` y el canal 1 representa `smsout`. El objetivo es aprender una función $f$ tal que:

$$ \hat{X}_{t} = f(X_{t-1}, X_{t-2}, \dots, X_{t-n}) $$

## 2. Preprocesamiento de Datos

### 2.1. Agregación Espacio-Temporal
Los datos crudos se agregan espacialmente en una rejilla de $H \times W$ ($100 \times 100$) y temporalmente en intervalos de 1 hora.

### 2.2. Normalización Min-Max
Para facilitar la convergencia del entrenamiento, los datos se normalizan al rango $[0, 1]$ utilizando la transformación Min-Max:

$$ x'_{i} = \frac{x_i - \min(X)}{\max(X) - \min(X)} $$

Donde $x_i$ es el valor de tráfico en una celda y tiempo específico, y $X$ es el conjunto total de datos de entrenamiento.

### 2.3. Construcción de Entradas (Dependencias Temporales)
El modelo captura dos tipos de dependencias temporales:

1.  **Cercanía (Closeness - $X_c$)**: Captura la tendencia reciente. Se toman los últimos $l_c$ intervalos de tiempo.
    $$ X_c = [X_{t-l_c}, X_{t-(l_c-1)}, \dots, X_{t-1}] $$
    
2.  **Periodo (Period - $X_d$)**: Captura la periodicidad diaria (mismo hora del día en días anteriores). Se toman $l_p$ días.
    $$ X_d = [X_{t-l_p \cdot 24}, X_{t-(l_p-1) \cdot 24}, \dots, X_{t-24}] $$

## 3. Arquitectura del Modelo (ST-DenseNet)

El modelo utiliza dos ramas de redes convolucionales idénticas (una para $X_c$ y otra para $X_d$) que luego se fusionan. La característica principal es el uso de **Bloques Densos**.

### 3.1. Unidad Densa (Dense Unit)
En una red densa, la salida de cada capa se conecta a todas las capas siguientes. Para una capa $l$, la entrada es la concatenación de las salidas de todas las capas anteriores:

$$ x_l = H_l([x_0, x_1, \dots, x_{l-1}]) $$

Donde $H_l(\cdot)$ es una función compuesta por tres operaciones consecutivas:
1.  Batch Normalization ($BN$)
2.  Rectified Linear Unit ($ReLU$)
3.  Convolución $3 \times 3$ ($Conv$)

$$ H_l(x) = Conv(ReLU(BN(x))) $$

### 3.2. Ramas de Procesamiento
Cada rama (Cercanía y Periodo) procesa su entrada a través de:
1.  **Convolución Inicial**: Transforma la entrada al espacio de características.
2.  **Bloque Denso**: Secuencia de $L$ Unidades Densas.
3.  **Convolución Final**: Reduce la profundidad de los canales de vuelta a $N_{flow}$ (2 canales: SMS in/out).

Sea $f_c$ la transformación de la rama de cercanía y $f_d$ la de la rama de periodo:
$$ Y_c = f_c(X_c) $$
$$ Y_d = f_d(X_d) $$

### 3.3. Fusión Paramétrica Basada en Matrices
Las salidas de ambas ramas se combinan utilizando una fusión ponderada por matrices de pesos aprendibles ($W_c$ y $W_d$). A diferencia de una suma simple, esto permite dar diferente importancia a la cercanía o al periodo para cada ubicación espacial (cada celda de la rejilla).

$$ Y_{fusion} = W_c \circ Y_c + W_d \circ Y_d $$

Donde:
*   $\circ$ denota el producto de Hadamard (multiplicación elemento a elemento).
*   $W_c, W_d \in \mathbb{R}^{2 \times 100 \times 100}$ son parámetros aprendibles.

Finalmente, se aplica una función de activación **Sigmoid** para asegurar que la salida esté en el rango $[0, 1]$ (consistente con la normalización Min-Max).

$$ \hat{X}_t = \sigma(Y_{fusion}) = \frac{1}{1 + e^{-Y_{fusion}}} $$

## 4. Entrenamiento

### 4.1. Función de Pérdida (Loss Function)
Se utiliza el Error Cuadrático Medio (MSE) entre la predicción y el valor real:

$$ L(\theta) = \frac{1}{N} \sum_{i=1}^{N} || \hat{X}_t^{(i)} - X_t^{(i)} ||^2 $$

Donde $\theta$ son todos los parámetros aprendibles del modelo.

### 4.2. Optimizador
*   **Algoritmo**: Adam (Adaptive Moment Estimation).
*   **Learning Rate**: Se utiliza un esquema de decaimiento (MultiStepLR) que reduce la tasa de aprendizaje en épocas específicas (50 y 75) para refinar la convergencia.

## 5. Interpretación de Resultados

### 5.1. Métrica de Evaluación: RMSE
Para evaluar el rendimiento, primero se **desnormalizan** las predicciones para volver a la escala original de tráfico (número de SMS).

$$ \hat{X}_{orig} = \hat{X}_{norm} \cdot (Max - Min) + Min $$

Luego se calcula la Raíz del Error Cuadrático Medio (RMSE):

$$ RMSE = \sqrt{\frac{1}{M} \sum (\hat{x}_{orig} - x_{orig})^2} $$

**Interpretación:**
*   El RMSE indica el error promedio en la predicción del número de SMS por celda y por hora.
*   **Ejemplo**: Un RMSE de 5.0 significa que, en promedio, el modelo se equivoca por 5 SMS (arriba o abajo) en cada celda.
*   Cuanto menor sea el RMSE, mejor es el modelo.

### 5.2. Visualización
*   **Mapas de Calor (Heatmaps)**: Se comparan visualmente el "Ground Truth" (Realidad) vs "Prediction" (Predicción).
    *   Si los mapas de calor se ven similares en distribución de colores (zonas calientes en los mismos lugares), el modelo ha aprendido correctamente la distribución espacial.
*   **Curva de Loss**: Muestra cómo disminuye el error durante el entrenamiento. Debe descender y estabilizarse. Si sube, indica inestabilidad o learning rate muy alto.
