# Práctica Sistemas de Recomendación - Iteración 0 (Baseline de Popularidad)

Este directorio contiene el código y los resultados de la **Iteración 0**, desarrollado para la asignatura de Sistemas de Recomendación.

## Miembros del Equipo

- **Jacobo Cousillas Taboada** (`jacobo.cousillas@udc.es`)
- **Xaime Paz Ollero** (`xaime.paz.ollero@udc.es`)
- **Nicolas Aller Ponte** (`nicolas.aller@udc.es`)

---

## Descripción de la Implementación

El objetivo de esta fase inicial es construir un sistema de recomendación base (**baseline**) que utilice la popularidad global de las canciones.

La estrategia implementada es la siguiente:

1. **Extracción de la Matriz Interacciones**: A partir del dataset de entrenamiento (`spotify_train_dataset.zip`), se contabiliza la cantidad total de apariciones de cada canción en todas las playlists, usando una representación dispersa (CSR Matrix) para optimizar el rendimiento en tiempo y memoria.
2. **Cálculo de Popularidad**: Se obtiene un ranking ordenando las canciones por su frecuencia de aparición de mayor a menor.
3. **Generación de Recomendaciones**: Para cada playlist en el conjunto de prueba (`test_input_playlists.json`), se sugieren las canciones más populares del paso anterior, filtrando y descartando aquellas que ya están presentes (semillas) en la propia playlist. Para cada playlist se generan exactamente 500 recomendaciones únicas.

---

## Estructura del Código

Todo nuestro flujo de ejecución está estructurado modularmente en paquetes de **Python (`.py`)** (no se requieren Jupyter Notebooks):

- `src/data_loader.py`: Procesa el archivo ZIP de entrenamiento. Parse la información en formato JSON para crear y guardar internamente una matriz elemento-usuario (`user_item_matrix.npz`) así como los diccionarios de índices.
- `src/baseline.py`: Es el script principal de predicción. Carga la matriz generada, calcula el top de canciones a nivel global y procesa el fichero `test_input_playlists.json` para generar el archivo de envíos en el directorio `submissions/`.
- `src/evaluation.py`: Script que lee la solución (Ground Truth) de `test_eval_playlists.json` y compara nuestras recomendaciones para devolver los valores oficiales de _R-Precision_, _NDCG_ y _Clicks_.
- `src/verify_submission.py`: Utilidad adicional implementada para verificar que las recomendaciones cumplen estrictamente el formato exacto requerido (500 canciones, cero duplicados, etc.).

---

## Instrucciones de Ejecución

Para ejecutar este proyecto de principio a fin, asegúrese de tener configurado un entorno virtual de Python (>= 3.8). Se incluyen a través de `pyproject.toml` las dependencias estrictamente necesarias estándar (`numpy`, `scipy`). Puede instalar las dependencias con `pip` o `uv`:

```bash
uv sync   # O alternativamente: pip install .
source .venv/bin/activate
```

**Preparación de los Datos**:
Los datasets oficiales deben estar guardados en la carpeta `data/raw/` sin descomprimir:

- `data/raw/spotify_train_dataset.zip`
- `data/raw/spotify_test_playlists.zip`

### Flujo de ejecución secuencial:

**1. Preparar la estructura de datos (Entrenamiento):**

```bash
python src/data_loader.py
```

_Genera una carpeta en `data/processed/` con datos optimizados._

**2. Calcular el Baseline y Generar Recomendaciones (Predicción):**

```bash
python src/baseline.py
```

_Genera el archivo final en `submissions/iteracion_0_baseline.csv` (éste es el fichero válido que hemos extraído para subir al panel de la asignatura)._

**3. Testear el resultado contra Ground-Truth (Validación):**

```bash
python src/evaluation.py
```

---

## 📊 Resultados de la Evaluación (Métricas)

Tras procesar la totalidad de las 10,000 playlists objetivo en local y contrastarlas con `test_eval_playlists.json` usando nuestro script `evaluation.py`, se han obtenido las siguientes métricas para la Iteración 0:

- **R-Precision**: **0.025670**
- **NDCG (Normalized Discounted Cumulative Gain)**: **0.090437**
- **Recommended Songs Clicks**: **17.309400**

Estos resultados actúan de base (baseline) y muestran el comportamiento esperado para un modelo estático y general de popularidad, cumpliendo todos los requisitos obligatorios de volumen, estructura y forma exigidos de la Iteración 0.
