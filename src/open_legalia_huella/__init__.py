"""open-legalia-huella — huellas y ZIP de legalización de libros (estilo Legalia2).

La huella de cada libro es: Base64(SHA-256(bytes del fichero)).
No depende del año: solo del contenido del fichero.
"""

__version__ = "0.4.0"

from .book_types import OFFICIAL_BOOK_TYPES, display_name_for, resolve_book_type
from .hashing import huella_legalia, huella_legalia_bytes
from .models import BOOK_ZIP_STEMS, OFFICIAL_STEMS, resolve_stem, validate_irus

__all__ = [
    "__version__",
    "huella_legalia",
    "huella_legalia_bytes",
    "BOOK_ZIP_STEMS",
    "OFFICIAL_STEMS",
    "OFFICIAL_BOOK_TYPES",
    "resolve_stem",
    "resolve_book_type",
    "display_name_for",
    "validate_irus",
]
