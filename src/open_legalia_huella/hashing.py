"""Cálculo de la huella digital al estilo Legalia2 / Registro Mercantil.

Fórmula (ZIP real + símbolo en Legalia2 1.5.7: ``ObtenerHuellaFicheroSHA256`` +
``ConvertirABase64`` / ``ToBase64String``):

    huella = Base64( SHA-256( contenido binario del fichero ) )

- No usa sal, fecha, CIF ni año en el hash.
- El binario también expone ``ObtenerHuellaFicheroMD5`` (legado / otros usos);
  el campo de legalización de libros en DATOS.TXT es SHA-256 Base64.
- Si el libro del ejercicio N+1 tiene otro contenido → otra huella.
- Si re-exportas el mismo binario idéntico → la misma huella.
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

# Legalia2: kLongitudHuellaSHA256 — digest SHA-256 = 32 bytes → Base64 ~44 chars con '='
SHA256_B64_LEN = 44


def huella_legalia_bytes(data: bytes) -> str:
    """Devuelve la huella Base64(SHA-256) de un buffer (ruta principal de legalización)."""
    digest = hashlib.sha256(data).digest()
    return base64.b64encode(digest).decode("ascii")


def huella_legalia(path: str | Path) -> str:
    """Devuelve la huella Base64(SHA-256) del fichero en disco."""
    p = Path(path)
    return huella_legalia_bytes(p.read_bytes())


def huella_md5_bytes(data: bytes) -> str:
    """Base64(MD5) — existe en Legalia2 (ObtenerHuellaFicheroMD5); no es el campo NNN06 actual."""
    return base64.b64encode(hashlib.md5(data).digest()).decode("ascii")


def sha256_hex(path: str | Path) -> str:
    """SHA-256 en hex (depuración; Legalia usa Base64)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
