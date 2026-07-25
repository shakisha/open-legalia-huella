"""Empaquetado y verificación del ZIP de legalización."""
from __future__ import annotations

import zipfile
from pathlib import Path

from .datos import (
    build_datos_txt,
    build_desc_txt,
    build_nombres_txt,
    parse_huellas_from_datos,
)
from .hashing import huella_legalia, huella_legalia_bytes
from .models import Expediente


def missing_libros(exp: Expediente) -> list[tuple[int, str, Path]]:
    """Libros del expediente cuya ruta no existe (índice 1-based, etiqueta, path)."""
    missing: list[tuple[int, str, Path]] = []
    for i, libro in enumerate(exp.libros, 1):
        p = Path(libro.path)
        if not p.is_file():
            missing.append((i, libro.display_name(), p))
    return missing


def format_missing_libros(missing: list[tuple[int, str, Path]]) -> str:
    """Mensaje legible con todos los libros ausentes."""
    if not missing:
        return ""
    lines = ["No se encontraron estos libros del expediente:"]
    for i, label, p in missing:
        lines.append(f"  [{i}] {label}: {p}")
    lines.append("Revisa las rutas en el config (campo libros[].path) y vuelve a intentar.")
    return "\n".join(lines)


def pack_zip(exp: Expediente, out_path: str | Path | None = None) -> Path:
    """Genera el ZIP LL{registro}{CIF}.ZIP con libros + DATOS/DESC/NOMBRES."""
    out = Path(out_path) if out_path else Path(exp.zip_basename())
    missing = missing_libros(exp)
    if missing:
        raise FileNotFoundError(format_missing_libros(missing))
    if not exp.libros:
        raise ValueError("El expediente no tiene libros (libros[] vacío).")

    datos = build_datos_txt(exp)
    desc = build_desc_txt(exp)
    nombres = build_nombres_txt(exp.libros)

    # Latin-1 para tildes (como Legalia)
    def enc(s: str) -> bytes:
        return s.encode("latin-1", errors="replace")

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for libro in exp.libros:
            data = Path(libro.path).read_bytes()
            # ZipInfo con fecha del fichero fuente
            zf.writestr(libro.zip_filename(), data)
        zf.writestr("DATOS.TXT", enc(datos))
        zf.writestr("DESC.TXT", enc(desc))
        zf.writestr("NOMBRES.TXT", enc(nombres))

    return out.resolve()


def verify_zip(zip_path: str | Path) -> list[dict]:
    """Verifica huellas del ZIP. Devuelve lista de dicts por fichero de libro."""
    zip_path = Path(zip_path)
    results: list[dict] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        datos_key = next((n for n in names if n.upper() == "DATOS.TXT"), None)
        if not datos_key:
            raise ValueError("ZIP sin DATOS.TXT")
        huellas = parse_huellas_from_datos(zf.read(datos_key))
        nombres_key = next((n for n in names if n.upper() == "NOMBRES.TXT"), None)
        if nombres_key:
            orden = [
                ln.strip()
                for ln in zf.read(nombres_key).decode("latin-1").splitlines()
                if ln.strip()
            ]
        else:
            meta = {"DATOS.TXT", "DESC.TXT", "NOMBRES.TXT"}
            orden = [n for n in names if n not in meta and not n.endswith("/")]

        for i, fname in enumerate(orden):
            expected = huellas[i][1] if i < len(huellas) else None
            label = huellas[i][0] if i < len(huellas) else fname
            if fname not in names:
                results.append(
                    {
                        "file": fname,
                        "label": label,
                        "ok": False,
                        "error": "listado en NOMBRES pero ausente en ZIP",
                    }
                )
                continue
            data = zf.read(fname)
            got = huella_legalia_bytes(data)
            ok = expected is not None and got == expected
            results.append(
                {
                    "file": fname,
                    "label": label,
                    "ok": ok,
                    "expected": expected,
                    "got": got,
                    "size": len(data),
                }
            )
    return results


def verify_zip_report(zip_path: str | Path) -> tuple[bool, str]:
    rows = verify_zip(zip_path)
    lines = [f"ZIP: {zip_path}", f"Libros: {len(rows)}"]
    all_ok = True
    for r in rows:
        if r["ok"]:
            lines.append(f"  OK  {r['file']} ({r['label']})  {r['got']}")
        else:
            all_ok = False
            lines.append(f"  FAIL {r['file']} ({r.get('label')})")
            if r.get("expected"):
                lines.append(f"       esperado:  {r['expected']}")
                lines.append(f"       calculado: {r.get('got')}")
            if r.get("error"):
                lines.append(f"       error: {r['error']}")
    return all_ok, "\n".join(lines)
