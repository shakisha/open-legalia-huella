"""Cálculo de la huella digital al estilo Legalia2 / Registro Mercantil.

Fórmula (verificada empíricamente con ZIP real Legalia 1.5.7, 2026-07-24/25):

    huella = Base64( SHA-256( contenido binario del fichero ) )

- No usa sal, fecha, CIF ni año en el hash.
- Si el libro del ejercicio N+1 tiene otro contenido → otra huella.
- Si re-exportas el mismo binario idéntico → la misma huella.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path


def huella_legalia_bytes(data: bytes) -> str:
    """Devuelve la huella Base64(SHA-256) de un buffer."""
    digest = hashlib.sha256(data).digest()
    return base64.b64encode(digest).decode("ascii")


def huella_legalia(path: str | Path) -> str:
    """Devuelve la huella Base64(SHA-256) del fichero en disco."""
    p = Path(path)
    return huella_legalia_bytes(p.read_bytes())


def sha256_hex(path: str | Path) -> str:
    """SHA-256 en hex (depuración; Legalia usa Base64)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
