#!/usr/bin/env python3
"""Compat: redirige al CLI del paquete."""
from open_legalia_huella.cli import main
import sys

if __name__ == "__main__":
    # open-legalia-huella huella ...
    raise SystemExit(main(["huella", *sys.argv[1:]]))
