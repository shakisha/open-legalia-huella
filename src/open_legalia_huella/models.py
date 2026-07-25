"""Modelos de datos del expediente de legalización."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# Prefijos de fichero en el ZIP (observados en Legalia 1.5.7)
BOOK_ZIP_STEMS: dict[str, str] = {
    "diario": "DIARIO",
    "inventario": "INV_CUEN",
    "inventario_cuentas": "INV_CUEN",
    "actas": "ACTAS",
    "socios": "SOCIOS",
    "contratos": "CONTRAT",
    "mayor": "MAYOR",
}

# Nombre legible en DATOS.TXT campo NNN01
BOOK_DISPLAY_NAMES: dict[str, str] = {
    "diario": "Diario",
    "inventario": "Inventario y cuentas anuales",
    "inventario_cuentas": "Inventario y cuentas anuales",
    "actas": "Actas",
    "socios": "Registro de socios",
    "contratos": "Contratos con el socio único",
    "mayor": "Mayor",
}


@dataclass
class Libro:
    """Un libro a legalizar."""

    tipo: str  # clave de BOOK_ZIP_STEMS
    path: str  # ruta al fichero fuente
    numero: int = 1  # nº de tomo/libro (1 si es el primero)
    apertura: str = ""  # DDMMYYYY
    cierre: str = ""  # DDMMYYYY
    cierre_anterior: str = ""  # DDMMYYYY del último legalizado; vacío si numero==1

    def display_name(self) -> str:
        return BOOK_DISPLAY_NAMES.get(self.tipo, self.tipo)

    def zip_filename(self) -> str:
        stem = BOOK_ZIP_STEMS.get(self.tipo)
        if not stem:
            stem = f"LIBRO{self.tipo.upper()[:6]}"
        ext = Path(self.path).suffix.upper().lstrip(".") or "BIN"
        # Legalia usa XLSX en mayúsculas
        if ext == "XLSX":
            ext = "XLSX"
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
    seccion: str = ""
    folio: str = ""
    hoja: str = ""  # p.ej. M-12345
    provincia_registro: str = ""  # p.ej. "MADRID"


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
    # 401NO visto en capturas reales
    campo_401: str = "NO"

    def zip_basename(self) -> str:
        """Nombre canónico LL{registro 5 dígitos}{CIF}.ZIP"""
        reg = (self.sociedad.registro_codigo or "00000").zfill(5)[-5:]
        cif = self.sociedad.cif.strip().upper()
        return f"LL{reg}{cif}.ZIP"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
