"""Carga/guarda expediente desde YAML o JSON (sin dependencias extra: JSON nativo).

YAML es opcional si hay PyYAML instalado; si no, se usa JSON.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Expediente, Libro, Presentante, Sociedad


def _load_raw(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError as e:
            raise SystemExit(
                "Para YAML instala PyYAML (`pip install pyyaml`) o usa un .json"
            ) from e
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("El fichero de config debe ser un objeto/mapa")
    return data


def load_expediente(path: str | Path) -> Expediente:
    raw = _load_raw(Path(path))
    soc = Sociedad(**raw["sociedad"])
    pre = Presentante(**raw["presentante"])
    libros = [Libro(**lb) for lb in raw.get("libros", [])]
    return Expediente(
        sociedad=soc,
        presentante=pre,
        libros=libros,
        ejercicio=int(raw.get("ejercicio", 2025)),
        etiqueta=raw.get("etiqueta", ""),
        fecha_presentacion=raw.get("fecha_presentacion", ""),
        version_legalia=raw.get("version_legalia", "1.5.7"),
        campo_401=raw.get("campo_401", "NO"),
    )


def example_config_dict() -> dict[str, Any]:
    return {
        "ejercicio": 2025,
        "etiqueta": "Libros 2025 EJEMPLO SA",
        "fecha_presentacion": "",  # vacío = hoy DDMMYYYY
        "version_legalia": "1.5.7",
        "sociedad": {
            "razon_social": "EJEMPLO SOCIEDAD LIMITADA",
            "cif": "B00000000",
            "domicilio": "Calle Mayor 1",
            "municipio": "Madrid",
            "codigo_postal": "28001",
            "provincia_ine": "28",
            "provincia_registro": "MADRID",
            "telefono": "600000000",
            "registro_codigo": "28000",
            "registro_nombre": "REGISTRO MERCANTIL",
            "tomo": "1",
            "seccion": "8",
            "folio": "1",
            "hoja": "M-0",
        },
        "presentante": {
            "nombre": "NOMBRE",
            "apellido1": "APELLIDO1",
            "apellido2": "APELLIDO2",
            "nif": "00000000T",
            "domicilio": "Calle Mayor 1",
            "municipio": "Madrid",
            "codigo_postal": "28001",
            "provincia_ine": "28",
            "telefono": "600000000",
            "email": "ejemplo@example.com",
        },
        "libros": [
            {
                "tipo": "diario",
                "path": "./libros/diario.xlsx",
                "numero": 1,
                "apertura": "01012025",
                "cierre": "31122025",
                "cierre_anterior": "",
            },
            {
                "tipo": "inventario",
                "path": "./libros/inventario.pdf",
                "numero": 1,
                "apertura": "01012025",
                "cierre": "31122025",
                "cierre_anterior": "",
            },
        ],
    }


def write_example_config(path: str | Path, fmt: str = "json") -> Path:
    path = Path(path)
    data = example_config_dict()
    if fmt == "yaml":
        try:
            import yaml  # type: ignore
        except ImportError as e:
            raise SystemExit("pip install pyyaml para escribir YAML") from e
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
