import zipfile
import json
import csv
import logging
import time
import numpy as np
from pathlib import Path
from scipy.sparse import load_npz
from typing import List, Set

# Configuración de Logging profesional
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Datos del grupo (Requisitos de la práctica)
TEAM_NAME = "Jacobo_Cousillas_Xaime_Paz_Nicolas_Aller"
TEAM_EMAIL = "jacobo.cousillas@udc.es_xaime.paz.ollero@udc.es_nicolas.aller@udc.es,"
RECOMMENDATIONS_COUNT = 500 

def generate_baseline():
    """
    Genera el archivo de recomendaciones basado en popularidad global.
    Solo procesa el archivo de entrada (test_input_playlists.json).
    """
    start_time = time.time()
    
    # 1. Configuración de rutas
    BASE_DIR = Path(__file__).resolve().parent.parent
    PROCESSED_DIR = BASE_DIR / "data" / "processed"
    TEST_ZIP_PATH = BASE_DIR / "data" / "raw" / "spotify_test_playlists.zip"
    OUTPUT_CSV_PATH = BASE_DIR / "submissions" / "iteracion_0_baseline.csv"
    METADATA_PATH = BASE_DIR / "submissions" / "iteracion_0_info.json"

    # 2. Carga de la infraestructura de datos
    logging.info("Cargando matriz de entrenamiento y mapeos...")
    try:
        # Cargamos la matriz CSR generada por data_loader.py
        matrix = load_npz(PROCESSED_DIR / "user_item_matrix.npz")
        
        # Cargamos el diccionario para traducir índices a URIs de Spotify
        with open(PROCESSED_DIR / "track_to_idx.json", "r", encoding="utf-8") as f:
            track_to_idx = json.load(f)
        
        # Invertimos el diccionario: {índice: uri}
        idx_to_track = {v: k for k, v in track_to_idx.items()}
        
    except FileNotFoundError as e:
        logging.error(f"Error: No se encontró el archivo necesario en data/processed/. {e}")
        return

    # 3. Cálculo de Popularidad Global
    logging.info("Calculando ranking de popularidad desde la matriz...")
    # Sumamos las columnas (canciones) de la matriz CSR
    popularity_counts = np.array(matrix.sum(axis=0)).flatten()
    
    # Obtenemos los índices ordenados de mayor a menor frecuencia
    sorted_indices = np.argsort(-popularity_counts)
    
    # Tomamos las 2000 canciones más populares como margen de seguridad
    global_top_uris = [idx_to_track[idx] for idx in sorted_indices[:2000]]

    # 4. Generación del Submission (Solo para test_input_playlists.json)
    logging.info(f"Procesando 'test_input_playlists.json' para generar recomendaciones...")
    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    total_playlists = 0

    with open(OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Cabecera obligatoria según el README del reto
        writer.writerow(['team_info', TEAM_NAME, TEAM_EMAIL])
        writer.writerow([]) # Línea vacía permitida/recomendada

        with zipfile.ZipFile(TEST_ZIP_PATH, "r") as zipf:
            # Abrimos específicamente el archivo de entrada del reto
            with zipf.open("test_input_playlists.json") as f:
                data = json.loads(f.read())
                
                for playlist in data.get("playlists", []):
                    total_playlists += 1
                    pid = playlist["pid"]
                    
                    # Identificamos las canciones que ya tiene la playlist (semilla)
                    seeds: Set[str] = {t["track_uri"] for t in playlist.get("tracks", [])}
                    
                    # Generamos el Top 500 excluyendo las semillas
                    recommendations = []
                    for uri in global_top_uris:
                        if uri not in seeds:
                            recommendations.append(uri)
                        
                        if len(recommendations) == RECOMMENDATIONS_COUNT:
                            break
                    
                    # Escribimos la fila según el formato: pid, uri_1, uri_2, ...
                    writer.writerow([pid] + recommendations)

    # 5. Guardado de Metadatos de ejecución
    execution_time = time.time() - start_time
    logging.info(f"Guardando metadatos en {METADATA_PATH.name}...")
    
    submission_metadata = {
        "equipo": TEAM_NAME,
        "metodo": "Popularity Baseline (Iteración 0)",
        "estadisticas": {
            "playlists_procesadas": total_playlists,
            "recomendaciones_por_playlist": RECOMMENDATIONS_COUNT,
            "tiempo_ejecucion_segundos": round(execution_time, 2)
        },
        "archivos_utilizados": {
            "entrenamiento": "user_item_matrix.npz",
            "test_input": "test_input_playlists.json"
        }
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(submission_metadata, f, indent=4, ensure_ascii=False)

    logging.info(f"Se han procesado {total_playlists} playlists en {execution_time:.2f}s.")
    logging.info(f"Archivo de salida: {OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    generate_baseline()