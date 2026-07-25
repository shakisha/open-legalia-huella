"""Modelos de datos del expediente de legalización."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .book_types import (
    ALIASES,
    OFFICIAL_BOOK_TYPES,
    OFFICIAL_STEMS,
    STEM_TO_TYPE,
    display_name_for,
    resolve_book_type,
)

# Reexport para API estable
BOOK_ZIP_STEMS: dict[str, str] = {**ALIASES, **{s: s for s in OFFICIAL_STEMS}}
BOOK_DISPLAY_NAMES: dict[str, str] = {
    **{a: STEM_TO_TYPE[st].descripcion for a, st in ALIASES.items()},
    **{bt.stem: bt.descripcion for bt in OFFICIAL_BOOK_TYPES},
}

# Límites del catálogo de versiones de Registradores (VersionesLegalia.xml, 1.5.7)
BYTES_MAXIMOS_ZIP = 314_572_800  # 300 MiB
BYTES_AVISO_ZIP = 346_030_080

# IRUS (Identificador Registral Mercantil) — Legalia 1.5.7; validación IRUSNoTiene13Digitos
IRUS_DIGITS = 13


def resolve_stem(tipo: str) -> str:
    """Resuelve tipo de config / stem oficial → STEM Legalia en mayúsculas."""
    return resolve_book_type(tipo).stem


def validate_irus(irus: str) -> str | None:
    """Devuelve mensaje de error o None si OK (vacío permitido)."""
    v = (irus or "").strip()
    if not v:
        return None
    if not v.isdigit() or len(v) != IRUS_DIGITS:
        return (
            f"IRUS debe tener exactamente {IRUS_DIGITS} dígitos "
            f"(Legalia: IRUSNoTiene13Digitos); recibido {irus!r}"
        )
    return None


@dataclass
class Libro:
    """Un libro a legalizar."""

    tipo: str  # clave amigable o stem oficial (DIARIO, INV_CUEN, …)
    path: str  # ruta al fichero fuente
    numero: int = 1  # nº de tomo/libro (1 si es el primero)
    apertura: str = ""  # DDMMYYYY
    cierre: str = ""  # DDMMYYYY
    cierre_anterior: str = ""  # DDMMYYYY del último legalizado; vacío si numero==1

    def book_type(self):
        return resolve_book_type(self.tipo)

    def stem(self) -> str:
        return self.book_type().stem

    def display_name(self) -> str:
        """Texto exacto del campo DATOS NNN01 (Descripcion Legalia)."""
        return display_name_for(self.tipo)

    def zip_filename(self) -> str:
        """Nombre dentro del ZIP: STEM_NNN.EXT (DameNombreFichero)."""
        stem = self.stem()
        ext = Path(self.path).suffix.upper().lstrip(".") or "BIN"
        return f"{stem}_{self.numero:03d}.{ext}"


@dataclass
class Sociedad:
    razon_social: str
    cif: str
    domicilio: str
    municipio: str
    codigo_postal: str
    provincia_ine: str  # p.ej. "28" Madrid
    telefono: str = ""
    registro_codigo: str = ""  # p.ej. "28000" → en ZIP LL28000…
    registro_nombre: str = "REGISTRO MERCANTIL"
    tomo: str = ""
    seccion: str = ""  # DATOS 202 (libro/sección registral)
    folio: str = ""
    hoja: str = ""  # p.ej. M-12345 — DATOS 206
    provincia_registro: str = ""  # p.ej. "MADRID" — DATOS 100
    # IRUS: Identificador Registral Mercantil (Legalia 1.5.7). Va en DESC.TXT como IRUS=
    irus: str = ""
    # DATOS 207 — otros datos registrales (opcional)
    otros: str = ""


@dataclass
class Presentante:
    nombre: str
    apellido1: str
    apellido2: str = ""
    nif: str = ""
    domicilio: str = ""
    municipio: str = ""
    codigo_postal: str = ""
    provincia_ine: str = ""
    telefono: str = ""
    email: str = ""
    fax: str = ""  # DATOS 309 si se informa


@dataclass
class Expediente:
    """Expediente completo listo para empaquetar."""

    sociedad: Sociedad
    presentante: Presentante
    libros: list[Libro] = field(default_factory=list)
    ejercicio: int = 2025
    etiqueta: str = ""  # texto libre DESC.TXT primera línea
    fecha_presentacion: str = ""  # DDMMYYYY; default hoy
    version_legalia: str = "1.5.7"
    # 401 = solicita retención presentante (NO/SI); visto en capturas reales
    campo_401: str = "NO"
    # TipoPersona en DESC: J=jurídica (default), F=física
    tipo_persona: str = "J"

    def zip_basename(self) -> str:
        """Nombre canónico LL{registro 5 dígitos}{CIF}.ZIP (NombreZipPorDefecto)."""
        reg = (self.sociedad.registro_codigo or "00000").zfill(5)[-5:]
        cif = self.sociedad.cif.strip().upper()
        return f"LL{reg}{cif}.ZIP"

    def validate_libros(self) -> list[str]:
        """Validaciones al estilo Legalia (TipoLibroInexistente, TipoLibroNumeroRepetido)."""
        errors: list[str] = []
        seen: set[tuple[str, int]] = set()
        for i, lb in enumerate(self.libros, 1):
            try:
                stem = lb.stem()
            except ValueError as e:
                errors.append(f"[{i}] {e}")
                continue
            if lb.numero < 1 or lb.numero > 999:
                errors.append(f"[{i}] número de libro fuera de rango 1–999: {lb.numero}")
            key = (stem, lb.numero)
            if key in seen:
                errors.append(
                    f"[{i}] tipo+número repetido (TipoLibroNumeroRepetido): "
                    f"{stem}_{lb.numero:03d}"
                )
            seen.add(key)
        return errors

    def validate(self) -> list[str]:
        """Validaciones de expediente (libros + IRUS)."""
        errors = self.validate_libros()
        irus_err = validate_irus(self.sociedad.irus)
        if irus_err:
            errors.append(irus_err)
        tp = (self.tipo_persona or "J").upper()
        if tp not in ("J", "F"):
            errors.append(f"tipo_persona debe ser J o F, no {self.tipo_persona!r}")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
