import json
import zipfile
import logging
import csv
import numpy as np
from pathlib import Path
from typing import List, Dict, Set

# Configuración de logging profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def r_precision(prediction: List[str], ground_truth: Set[str]) -> float:
    """
    Calcula la precisión basada en el número de ítems relevantes (N).
    R-Precision es la proporción de canciones relevantes en las primeras N recomendaciones,
    donde N es el tamaño del ground truth.
    """
    if not ground_truth:
        return 0.0
    n = len(ground_truth)
    # Solo miramos las primeras N predicciones
    relevant_found = [t for t in prediction[:n] if t in ground_truth]
    return len(relevant_found) / n

def dcg(prediction: List[str], ground_truth: Set[str]) -> float:
    """Calcula el Discounted Cumulative Gain."""
    score = 0.0
    for i, track in enumerate(prediction):
        if track in ground_truth:
            # Fórmula: 1 / log2(pos + 1). Usamos i+2 porque i empieza en 0
            score += 1.0 / np.log2(i + 2)
    return score

def ndcg(prediction: List[str], ground_truth: Set[str]) -> float:
    """Calcula el Normalized DCG (Métrica principal de Spotify)."""
    actual_dcg = dcg(prediction, ground_truth)
    # DCG ideal: los aciertos estarían en las mejores posiciones posibles
    # Creamos un set ficticio de aciertos para calcular el máximo posible
    ideal_prediction = ["relevant"] * len(ground_truth)
    ideal_dcg = dcg(ideal_prediction, set(ideal_prediction))
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0

def song_clicks(prediction: List[str], ground_truth: Set[str]) -> float:
    """
    Métrica de 'Clicks': cuántos bloques de 10 canciones hay que saltar 
    hasta encontrar la primera relevante.
    """
    for i, track in enumerate(prediction):
        if track in ground_truth:
            return i // 10
    return 51.0 # Valor por defecto si no hay aciertos en el top 500

def evaluate():
    BASE_DIR = Path(__file__).resolve().parent.parent
    SUBMISSION_PATH = BASE_DIR / "submissions" / "iteracion_0_baseline.csv"
    TEST_ZIP_PATH = BASE_DIR / "data" / "raw" / "spotify_test_playlists.zip"

    # 1. Extraer Ground Truth (lo que el usuario REALMENTE añadió y estaba oculto)
    logging.info("Extrayendo ground truth desde 'test_eval_playlists.json'...")
    ground_truths: Dict[str, Set[str]] = {}
    
    try:
        with zipfile.ZipFile(TEST_ZIP_PATH, "r") as zipf:
            # IMPORTANTE: Cargamos el archivo de evaluación, no el de input
            with zipf.open("test_eval_playlists.json") as f:
                data = json.loads(f.read())
                for pl in data.get("playlists", []):
                    # Estas son las pistas que el modelo DEBÍA adivinar
                    ground_truths[str(pl["pid"])] = {t["track_uri"] for t in pl.get("tracks", [])}
    except KeyError:
        logging.error("No se encontró 'test_eval_playlists.json' dentro del ZIP.")
        return

    # 2. Procesar el archivo de resultados (Submission)
    logging.info(f"Evaluando métricas para: {SUBMISSION_PATH.name}")
    metrics = {"r_prec": [], "ndcg": [], "clicks": []}
    
    try:
        with open(SUBMISSION_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                # Saltar cabeceras, team_info y líneas vacías
                if not row or row[0].startswith("team_info") or row[0] == "" or row[0] == "team_info":
                    continue
                
                pid = row[0]
                preds = row[1:] # Las 500 canciones recomendadas
                
                if pid in ground_truths:
                    gt = ground_truths[pid]
                    metrics["r_prec"].append(r_precision(preds, gt))
                    metrics["ndcg"].append(ndcg(preds, gt))
                    metrics["clicks"].append(song_clicks(preds, gt))
    except FileNotFoundError:
        logging.error("No se encontró el archivo de submission. Genera el baseline primero.")
        return

    # 3. Mostrar resultados finales promedio
    if metrics["ndcg"]:
        logging.info(f"--- RESULTADOS FINALES (Sobre {len(metrics['ndcg'])} playlists) ---")
        print(f"R-Precision: {np.mean(metrics['r_prec']):.6f}")
        print(f"NDCG:        {np.mean(metrics['ndcg']):.6f}")
        print(f"Clicks:      {np.mean(metrics['clicks']):.6f}")
    else:
        logging.warning("No se pudieron emparejar las predicciones con el ground truth.")

if __name__ == "__main__":
    evaluate()