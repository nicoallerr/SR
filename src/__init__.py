"""
Spotify Million Playlist Challenge - Iteration 0
Sistema de recomendación basado en popularidad.
"""

from .data_loader import build_dataset
from .baseline import generate_baseline
from .evaluation import evaluate
from .verify_submission import verify

__version__ = "0.1.0"

__all__ = [
    'build_dataset',
    'generate_baseline',
    'evaluate',
    'verify',
]