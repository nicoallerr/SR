import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify():
    BASE_DIR = Path(__file__).resolve().parent.parent
    SUBMISSION_FILE = BASE_DIR / "submissions" / "iteracion_0_baseline.csv"
    
    logging.info(f"Verificando formato de: {SUBMISSION_FILE.name}")
    
    try:
        # 1. Leer saltando las líneas de team_info
        with open(SUBMISSION_FILE, 'r') as f:
            lines = [l for l in f.readlines() if l.strip() and not l.startswith('team_info')]
        
        errors = 0
        pids_vistos = set()
        
        for i, line in enumerate(lines):
            parts = line.strip().split(',')
            pid = parts[0]
            tracks = parts[1:]
            
            # Regla: 500 tracks
            if len(tracks) != 500:
                logging.error(f"Línea {i}: El PID {pid} tiene {len(tracks)} tracks (deben ser 500)")
                errors += 1
            
            # Regla: No duplicados
            if len(set(tracks)) != len(tracks):
                logging.error(f"Línea {i}: El PID {pid} tiene tracks duplicados")
                errors += 1
                
            # Regla: PID único en el archivo
            if pid in pids_vistos:
                logging.error(f"Línea {i}: El PID {pid} está duplicado en el CSV")
                errors += 1
            pids_vistos.add(pid)
            
            # Regla: Formato URI
            if not all(t.strip().startswith('spotify:track:') for t in tracks):
                logging.error(f"Línea {i}: El PID {pid} contiene tracks con formato incorrecto")
                errors += 1

        if errors == 0:
            logging.info("Verificación exitosa. El archivo cumple con todas las reglas del README.")
        else:
            logging.warning(f"Se encontraron {errors} errores en el formato.")

    except FileNotFoundError:
        logging.error("No se encontró el archivo de submission.")

if __name__ == "__main__":
    verify()