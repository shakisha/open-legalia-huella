"""open-legalia-huella — huellas y ZIP de legalización de libros (estilo Legalia2).

La huella de cada libro es: Base64(SHA-256(bytes del fichero)).
No depende del año: solo del contenido del fichero.
"""

__version__ = "0.3.0"

from .hashing import huella_legalia, huella_legalia_bytes
from .models import BOOK_ZIP_STEMS, OFFICIAL_STEMS, resolve_stem

__all__ = [
    "__version__",
    "huella_legalia",
    "huella_legalia_bytes",
    "BOOK_ZIP_STEMS",
    "OFFICIAL_STEMS",
    "resolve_stem",
]
