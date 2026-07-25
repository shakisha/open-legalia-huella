#!/usr/bin/env python3
"""CLI open-legalia-huella."""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from . import __version__
from .config_io import load_expediente, write_example_config
from .hashing import huella_legalia, sha256_hex
from .pack import format_missing_libros, missing_libros, pack_zip, verify_zip_report


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def cmd_huella(args: argparse.Namespace) -> int:
    rc = 0
    for f in args.files:
        p = Path(f)
        if not p.is_file():
            _err(f"no existe el fichero: {p}")
            rc = 1
            continue
        h = huella_legalia(p)
        print(f"{p.name}\t{h}")
        if args.hex:
            print(f"  sha256_hex\t{sha256_hex(p)}")
            print(f"  size\t{p.stat().st_size}")
    return rc


def cmd_verify(args: argparse.Namespace) -> int:
    zpath = Path(args.zip)
    if not zpath.is_file():
        _err(f"no existe el ZIP: {zpath}")
        return 1
    try:
        ok, report = verify_zip_report(zpath)
    except zipfile.BadZipFile:
        _err(f"no es un ZIP válido: {zpath}")
        return 1
    except ValueError as e:
        _err(str(e))
        return 1
    print(report)
    if not ok:
        print("\nVerificación fallida: al menos una huella no coincide con DATOS.TXT.", file=sys.stderr)
    return 0 if ok else 2


def cmd_init(args: argparse.Namespace) -> int:
    out = Path(args.out)
    try:
        write_example_config(out, fmt=args.format)
    except SystemExit as e:
        # config_io usa SystemExit para YAML sin PyYAML
        msg = e.code if isinstance(e.code, str) else "no se pudo escribir la plantilla"
        _err(str(msg))
        return 1
    print(f"Plantilla escrita: {out.resolve()}")
    print("Edita sociedad, presentante y rutas de libros; luego:")
    print(f"  open-legalia-huella pack -c {out.name}")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    cfg = Path(args.config)
    if not cfg.is_file():
        _err(f"no existe el config: {cfg}")
        print("  Tip: open-legalia-huella init -o expediente.json", file=sys.stderr)
        return 1

    try:
        exp = load_expediente(cfg)
    except json.JSONDecodeError as e:
        _err(f"JSON inválido en {cfg}: {e.msg} (línea {e.lineno})")
        return 1
    except KeyError as e:
        _err(f"falta el campo obligatorio en el config: {e.args[0]}")
        print("  Revisa sociedad, presentante y libros[].", file=sys.stderr)
        return 1
    except (TypeError, ValueError) as e:
        _err(f"config inválido ({cfg}): {e}")
        return 1
    except SystemExit as e:
        msg = e.code if isinstance(e.code, str) else str(e)
        _err(msg)
        return 1

    out = Path(args.out) if args.out else Path(exp.zip_basename())
    missing = missing_libros(exp)

    if args.dry_run:
        print(f"ZIP destino: {out}")
        print(f"Ejercicio: {exp.ejercicio}  libros: {len(exp.libros)}")
        for i, lb in enumerate(exp.libros, 1):
            p = Path(lb.path)
            print(f"  [{i}] {lb.display_name()}  num={lb.numero}  {p}")
            if p.is_file():
                print(f"       huella={huella_legalia(p)}")
            else:
                print("       ERROR: fichero no encontrado")
        if not exp.libros:
            _err("el expediente no tiene libros (libros[] vacío).")
            return 1
        if missing:
            print(file=sys.stderr)
            _err(format_missing_libros(missing))
            return 1
        print("Dry-run OK: todos los libros existen.")
        return 0

    if missing:
        _err(format_missing_libros(missing))
        return 1
    if not exp.libros:
        _err("el expediente no tiene libros (libros[] vacío).")
        return 1

    try:
        path = pack_zip(exp, out)
    except FileNotFoundError as e:
        _err(str(e))
        return 1
    except ValueError as e:
        _err(str(e))
        return 1
    except OSError as e:
        _err(f"no se pudo escribir el ZIP ({out}): {e}")
        return 1

    print(f"ZIP generado: {path}")
    print(f"Tamaño: {path.stat().st_size} bytes")
    ok, report = verify_zip_report(path)
    print(report)
    if args.json_summary:
        summary = {
            "zip": str(path),
            "size": path.stat().st_size,
            "ok": ok,
            "basename": exp.zip_basename(),
        }
        print(json.dumps(summary, ensure_ascii=False))
    if not ok:
        _err("el ZIP se generó pero la auto-verificación falló (huellas).")
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="open-legalia-huella",
        description=(
            "Huellas digitales y ZIP de legalización de libros mercantiles "
            "(compatible con el formato observado de Legalia2). "
            "Huella = Base64(SHA-256(fichero))."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("huella", help="Calcula la huella de uno o más ficheros")
    h.add_argument("files", nargs="+", help="PDF/XLSX/… del libro")
    h.add_argument("--hex", action="store_true", help="Mostrar también SHA-256 hex")
    h.set_defaults(func=cmd_huella)

    v = sub.add_parser("verify", help="Verifica huellas de un ZIP Legalia")
    v.add_argument("zip", help="Ruta al ZIP (LL….ZIP)")
    v.set_defaults(func=cmd_verify)

    i = sub.add_parser("init", help="Crea plantilla de configuración JSON/YAML")
    i.add_argument("-o", "--out", default="expediente.json", help="Fichero de salida")
    i.add_argument(
        "-f",
        "--format",
        choices=("json", "yaml"),
        default="json",
        help="Formato (yaml requiere PyYAML)",
    )
    i.set_defaults(func=cmd_init)

    pk = sub.add_parser("pack", help="Genera el ZIP de presentación desde config")
    pk.add_argument("-c", "--config", required=True, help="expediente.json / .yaml")
    pk.add_argument("-o", "--out", default="", help="Ruta ZIP (default: LL{reg}{CIF}.ZIP)")
    pk.add_argument("--dry-run", action="store_true", help="Solo muestra huellas, no escribe ZIP")
    pk.add_argument("--json-summary", action="store_true")
    pk.set_defaults(func=cmd_pack)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\nCancelado.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
