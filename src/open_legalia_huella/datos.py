"""Lectura/escritura de DATOS.TXT, DESC.TXT y NOMBRES.TXT (formato Legalia2)."""
from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from .hashing import huella_legalia
from .models import Expediente, Libro


def _ddmmyyyy_today() -> str:
    t = date.today()
    return f"{t.day:02d}{t.month:02d}{t.year:04d}"


def _line(code: str, value: str) -> str:
    return f"{code}{value}"


def build_datos_txt(exp: Expediente, huellas: dict[int, str] | None = None) -> str:
    """Construye DATOS.TXT (texto Latin-1, líneas lógicas).

    `huellas` opcional: {índice_1based: base64sha256}. Si falta, se calcula
    desde cada Libro.path.
    """
    s = exp.sociedad
    p = exp.presentante
    fecha = exp.fecha_presentacion or _ddmmyyyy_today()
    lines: list[str] = []

    # Sociedad / registro
    lines.append(_line("100", s.provincia_registro or s.municipio))
    lines.append(_line("101", fecha))
    lines.append(_line("102", s.razon_social))
    lines.append(_line("105", s.cif.upper()))
    lines.append(_line("106", s.domicilio))
    lines.append(_line("107", s.municipio))
    lines.append(_line("108", s.codigo_postal))
    lines.append(_line("109", s.provincia_ine.zfill(2)))
    if s.telefono:
        lines.append(_line("111", s.telefono))
    if s.registro_codigo:
        lines.append(_line("112", s.registro_codigo.lstrip("0") and s.registro_codigo or s.registro_codigo))
        # Keep as provided (3026); ZIP name zero-pads separately
        lines[-1] = _line("112", s.registro_codigo)

    if s.tomo:
        lines.append(_line("201", s.tomo))
    if s.seccion:
        lines.append(_line("202", s.seccion))
    if s.folio:
        lines.append(_line("204", s.folio))
    lines.append(_line("205", s.registro_nombre))
    if s.hoja:
        lines.append(_line("206", s.hoja))

    # Presentante
    lines.append(_line("301", p.nombre))
    lines.append(_line("302", p.apellido1))
    if p.apellido2:
        lines.append(_line("303", p.apellido2))
    lines.append(_line("304", p.nif.upper()))
    if p.domicilio:
        lines.append(_line("305", p.domicilio))
    if p.municipio:
        lines.append(_line("306", p.municipio))
    if p.codigo_postal:
        lines.append(_line("307", p.codigo_postal))
    if p.provincia_ine:
        lines.append(_line("308", p.provincia_ine.zfill(2)))
    if p.telefono:
        lines.append(_line("310", p.telefono))
    if p.email:
        lines.append(_line("311", p.email))

    lines.append(_line("401", exp.campo_401))
    lines.append(_line("501", str(len(exp.libros))))

    for i, libro in enumerate(exp.libros, start=1):
        idx = f"{i:03d}"
        h = None
        if huellas and i in huellas:
            h = huellas[i]
        else:
            h = huella_legalia(libro.path)
        cierre_prev = libro.cierre_anterior
        if not cierre_prev and libro.numero == 1:
            cierre_prev = ""  # Legalia permite vacío en libro 1
        lines.append(_line(f"{idx}01", libro.display_name()))
        lines.append(_line(f"{idx}02", str(libro.numero)))
        lines.append(_line(f"{idx}03", libro.apertura))
        lines.append(_line(f"{idx}04", libro.cierre))
        lines.append(_line(f"{idx}05", cierre_prev))
        lines.append(_line(f"{idx}06", h))

    return "\r\n".join(lines) + "\r\n"


def build_nombres_txt(libros: Iterable[Libro]) -> str:
    return "\r\n".join(libro.zip_filename() for libro in libros) + "\r\n"


def build_desc_txt(exp: Expediente) -> str:
    etiqueta = exp.etiqueta or f"Libros {exp.ejercicio}"
    lines = [
        etiqueta,
        f"VersionLegalia2={exp.version_legalia}",
        "Formato=2",
        f"Ejercicio={exp.ejercicio}",
        "Enviado=",
        f"NombreZip={exp.zip_basename()}",
        "TipoPersona=J",
        "IRUS=",
        "eDocNumeroDocumento=",
        "eDocEntradaTipo=",
        "eDocEntradaSubsanada=",
        "eDocIdTramite=",
        "eDocNombreFicheroEnviado=",
        "eDocNombreFicheroAcuseEntrada=",
        "eDocNombreFicheroNE=",
        "EnvioReintentable=",
        "CodAccesoNif=",
        "PresentanteNombreConfirmado=",
        "PresentanteApellidosConfirmados=",
        "PresentanteCorreoElectronicoConfirmado=",
        "",
    ]
    return "\r\n".join(lines)


def parse_huellas_from_datos(datos: str | bytes) -> list[tuple[str, str]]:
    """Lista ordenada [(nombre_libro, huella_b64), ...] desde DATOS.TXT."""
    if isinstance(datos, bytes):
        text = datos.decode("latin-1", errors="replace")
    else:
        text = datos
    names: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip("\r")
        m = re.match(r"^(\d{3})01(.+)$", line)
        if m:
            names[m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r"^(\d{3})06(.+)$", line)
        if m:
            hashes[m.group(1)] = m.group(2).strip()
    out: list[tuple[str, str]] = []
    for k in sorted(hashes.keys()):
        out.append((names.get(k, k), hashes[k]))
    return out
