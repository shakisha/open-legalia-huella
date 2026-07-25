"""Catálogo oficial de tipos de libro Legalia2 1.5.7 (TiposLibro embebido).

Cada entrada es el trío canónico:
  Codigo + Descripcion (texto NNN01 en DATOS.TXT) + NombreFichero (STEM del ZIP)

Flags de validación de fechas tal como en el XML interno de Legalia2.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BookType:
    codigo: int
    """Código numérico Legalia (1–20)."""
    descripcion: str
    """Texto exacto del campo DATOS NNN01."""
    stem: str
    """Prefijo de fichero en el ZIP (NombreFichero)."""
    comprobar_solapamiento: bool = True
    comprobar_fecha_apertura: bool = True


# Orden y textos literales del XML <TiposLibro> de Legalia2 1.5.7
OFFICIAL_BOOK_TYPES: tuple[BookType, ...] = (
    BookType(1, "Diario", "DIARIO", True, True),
    BookType(2, "Inventario y cuentas anuales", "INV_CUEN", True, True),
    BookType(3, "Balances comprobación (sumas y saldos)", "BAL_SUMS", True, True),
    BookType(4, "Inventario", "INVENTAR", True, True),
    BookType(5, "Balances", "BALANCES", True, True),
    BookType(6, "Memoria", "MEMORIA", True, True),
    BookType(7, "Mayor", "MAYOR", True, True),
    BookType(8, "Libro de pérdidas y ganancias", "PER_GAN", True, True),
    BookType(9, "IVA", "IVA", True, True),
    BookType(10, "Facturas emitidas", "FAC_EMIT", True, True),
    BookType(11, "Facturas recibidas", "FAC_RECI", True, True),
    BookType(12, "Detalle del diario", "DET_DIA", True, True),
    BookType(13, "Registro de acciones nominativas", "ACCIONES", True, False),
    BookType(14, "Registro de socios", "SOCIOS", True, False),
    BookType(15, "Otros", "OTROS", False, True),
    BookType(16, "Libro de actas", "ACTASCON", True, False),
    BookType(17, "Libro de detalle de actas", "ACTASDET", True, False),
    BookType(
        18,
        "Libro-registro de contratos del socio único con la sociedad unipersonal",
        "SOCUNICO",
        True,
        False,
    ),
    BookType(19, "Libro de actas del consejo", "ACTALCON", True, False),
    BookType(20, "Libro de detalle de actas del consejo", "ACTACODE", True, False),
)

STEM_TO_TYPE: dict[str, BookType] = {bt.stem: bt for bt in OFFICIAL_BOOK_TYPES}
OFFICIAL_STEMS: frozenset[str] = frozenset(STEM_TO_TYPE)

# Alias de config (minúsculas) → STEM
ALIASES: dict[str, str] = {
    "diario": "DIARIO",
    "inventario": "INV_CUEN",
    "inventario_cuentas": "INV_CUEN",
    "inventar": "INVENTAR",
    "mayor": "MAYOR",
    "socios": "SOCIOS",
    "actas": "ACTASCON",
    "actas_con": "ACTASCON",
    "actas_det": "ACTASDET",
    "acta_code": "ACTACODE",
    "acta_lcon": "ACTALCON",
    "contratos": "SOCUNICO",
    "socio_unico": "SOCUNICO",
    "balances": "BALANCES",
    "bal_sums": "BAL_SUMS",
    "sumas_saldos": "BAL_SUMS",
    "det_dia": "DET_DIA",
    "detalle_diario": "DET_DIA",
    "fac_emit": "FAC_EMIT",
    "facturas_emitidas": "FAC_EMIT",
    "fac_reci": "FAC_RECI",
    "facturas_recibidas": "FAC_RECI",
    "iva": "IVA",
    "memoria": "MEMORIA",
    "per_gan": "PER_GAN",
    "pyg": "PER_GAN",
    "acciones": "ACCIONES",
    "otros": "OTROS",
}


def resolve_book_type(tipo: str) -> BookType:
    """Resuelve clave amigable o STEM → BookType oficial."""
    t = (tipo or "").strip()
    if not t:
        raise ValueError("tipo de libro vacío")
    if t in ALIASES:
        stem = ALIASES[t]
    elif t.upper() in STEM_TO_TYPE:
        stem = t.upper()
    else:
        raise ValueError(
            f"Tipo de libro desconocido: {tipo!r}. "
            f"Stems oficiales: {', '.join(sorted(OFFICIAL_STEMS))}"
        )
    return STEM_TO_TYPE[stem]


def display_name_for(tipo: str) -> str:
    """Texto exacto NNN01 (Descripcion Legalia)."""
    return resolve_book_type(tipo).descripcion
