"""Modelos de datos del expediente de legalización."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Prefijos de fichero en el ZIP = enumTipoLibro / NombreFichero de Legalia2 1.5.7
# (extraídos del ensamblado Legalia 2: <NombreFichero>…</NombreFichero>).
# Formato en ZIP: {STEM}_{NNN}.{EXT}  p.ej. DIARIO_004.XLSX
# ---------------------------------------------------------------------------
BOOK_ZIP_STEMS: dict[str, str] = {
    # Claves amigables (config) → stem oficial Legalia
    "diario": "DIARIO",
    "inventario": "INV_CUEN",
    "inventario_cuentas": "INV_CUEN",
    "inventar": "INVENTAR",
    "mayor": "MAYOR",
    "socios": "SOCIOS",
    "actas": "ACTASCON",  # actas “consecutivo” (defecto razonable)
    "actas_con": "ACTASCON",
    "actas_det": "ACTASDET",
    "acta_code": "ACTACODE",
    "acta_lcon": "ACTALCON",
    "contratos": "SOCUNICO",  # contratos con el socio único (NO "CONTRAT")
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
    # Permitir el stem oficial tal cual
    "DIARIO": "DIARIO",
    "INV_CUEN": "INV_CUEN",
    "INVENTAR": "INVENTAR",
    "MAYOR": "MAYOR",
    "SOCIOS": "SOCIOS",
    "ACTASCON": "ACTASCON",
    "ACTASDET": "ACTASDET",
    "ACTACODE": "ACTACODE",
    "ACTALCON": "ACTALCON",
    "SOCUNICO": "SOCUNICO",
    "BALANCES": "BALANCES",
    "BAL_SUMS": "BAL_SUMS",
    "DET_DIA": "DET_DIA",
    "FAC_EMIT": "FAC_EMIT",
    "FAC_RECI": "FAC_RECI",
    "IVA": "IVA",
    "MEMORIA": "MEMORIA",
    "PER_GAN": "PER_GAN",
    "ACCIONES": "ACCIONES",
    "OTROS": "OTROS",
}

# Stems oficiales únicos (canónicos en el ZIP)
OFFICIAL_STEMS: frozenset[str] = frozenset(
    {
        "DIARIO",
        "INV_CUEN",
        "INVENTAR",
        "MAYOR",
        "SOCIOS",
        "ACTASCON",
        "ACTASDET",
        "ACTACODE",
        "ACTALCON",
        "SOCUNICO",
        "BALANCES",
        "BAL_SUMS",
        "DET_DIA",
        "FAC_EMIT",
        "FAC_RECI",
        "IVA",
        "MEMORIA",
        "PER_GAN",
        "ACCIONES",
        "OTROS",
    }
)

# Nombre legible en DATOS.TXT campo NNN01 (textos habituales en sede / Legalia UI)
BOOK_DISPLAY_NAMES: dict[str, str] = {
    "diario": "Diario",
    "DIARIO": "Diario",
    "inventario": "Inventario y cuentas anuales",
    "inventario_cuentas": "Inventario y cuentas anuales",
    "INV_CUEN": "Inventario y cuentas anuales",
    "inventar": "Inventario",
    "INVENTAR": "Inventario",
    "mayor": "Mayor",
    "MAYOR": "Mayor",
    "socios": "Registro de socios",
    "SOCIOS": "Registro de socios",
    "actas": "Actas",
    "actas_con": "Actas",
    "ACTASCON": "Actas",
    "actas_det": "Actas detalladas",
    "ACTASDET": "Actas detalladas",
    "contratos": "Contratos con el socio único",
    "socio_unico": "Contratos con el socio único",
    "SOCUNICO": "Contratos con el socio único",
    "balances": "Balances",
    "BALANCES": "Balances",
    "bal_sums": "Balance de sumas y saldos",
    "sumas_saldos": "Balance de sumas y saldos",
    "BAL_SUMS": "Balance de sumas y saldos",
    "det_dia": "Detalle del diario",
    "DET_DIA": "Detalle del diario",
    "fac_emit": "Facturas emitidas",
    "FAC_EMIT": "Facturas emitidas",
    "fac_reci": "Facturas recibidas",
    "FAC_RECI": "Facturas recibidas",
    "iva": "IVA",
    "IVA": "IVA",
    "memoria": "Memoria",
    "MEMORIA": "Memoria",
    "per_gan": "Pérdidas y ganancias",
    "pyg": "Pérdidas y ganancias",
    "PER_GAN": "Pérdidas y ganancias",
    "acciones": "Acciones",
    "ACCIONES": "Acciones",
    "otros": "Otros",
    "OTROS": "Otros",
}

# Límites del catálogo de versiones de Registradores (VersionesLegalia.xml, 1.5.7)
BYTES_MAXIMOS_ZIP = 314_572_800  # 300 MiB
BYTES_AVISO_ZIP = 346_030_080


def resolve_stem(tipo: str) -> str:
    """Resuelve tipo de config / stem oficial → STEM Legalia en mayúsculas."""
    t = (tipo or "").strip()
    if t in BOOK_ZIP_STEMS:
        return BOOK_ZIP_STEMS[t]
    up = t.upper()
    if up in OFFICIAL_STEMS:
        return up
    raise ValueError(
        f"Tipo de libro desconocido: {tipo!r}. "
        f"Usa una clave de BOOK_ZIP_STEMS o un stem oficial: {', '.join(sorted(OFFICIAL_STEMS))}"
    )


@dataclass
class Libro:
    """Un libro a legalizar."""

    tipo: str  # clave de BOOK_ZIP_STEMS o stem oficial (DIARIO, INV_CUEN, …)
    path: str  # ruta al fichero fuente
    numero: int = 1  # nº de tomo/libro (1 si es el primero)
    apertura: str = ""  # DDMMYYYY
    cierre: str = ""  # DDMMYYYY
    cierre_anterior: str = ""  # DDMMYYYY del último legalizado; vacío si numero==1

    def stem(self) -> str:
        return resolve_stem(self.tipo)

    def display_name(self) -> str:
        if self.tipo in BOOK_DISPLAY_NAMES:
            return BOOK_DISPLAY_NAMES[self.tipo]
        stem = self.stem()
        return BOOK_DISPLAY_NAMES.get(stem, stem)

    def zip_filename(self) -> str:
        """Nombre dentro del ZIP: STEM_NNN.EXT (como DameNombreFichero de Legalia)."""
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
