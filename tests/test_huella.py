"""Tests de la huella y del empaquetado (sin datos reales de sociedad)."""
from __future__ import annotations

import base64
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from open_legalia_huella.cli import main
from open_legalia_huella.datos import parse_huellas_from_datos
from open_legalia_huella.hashing import huella_legalia, huella_legalia_bytes
from open_legalia_huella.models import Expediente, Libro, Presentante, Sociedad
from open_legalia_huella.pack import (
    format_missing_libros,
    missing_libros,
    pack_zip,
    verify_zip,
)


def test_huella_is_base64_sha256(tmp_path: Path):
    f = tmp_path / "libro.bin"
    payload = b"contenido de prueba legalizacion 2025\n"
    f.write_bytes(payload)
    h = huella_legalia(f)
    expected = base64.b64encode(hashlib.sha256(payload).digest()).decode()
    assert h == expected
    assert huella_legalia_bytes(payload) == expected


def test_same_bytes_same_huella_year_independent(tmp_path: Path):
    """La huella no 'cambia cada año': solo cambia si cambia el contenido."""
    a = tmp_path / "a.xlsx"
    b = tmp_path / "b.xlsx"
    data = b"PK\x03\x04fake-xlsx-same-bytes"
    a.write_bytes(data)
    b.write_bytes(data)
    assert huella_legalia(a) == huella_legalia(b)
    b.write_bytes(data + b"x")
    assert huella_legalia(a) != huella_legalia(b)


def test_pack_and_verify_roundtrip(tmp_path: Path):
    d = tmp_path / "diario.xlsx"
    inv = tmp_path / "inv.pdf"
    d.write_bytes(b"DIARIO-CONTENT-AAA")
    inv.write_bytes(b"%PDF-1.4 fake inventory")

    exp = Expediente(
        sociedad=Sociedad(
            razon_social="EJEMPLO SL",
            cif="B12345678",
            domicilio="Calle 1",
            municipio="Madrid",
            codigo_postal="28001",
            provincia_ine="28",
            provincia_registro="MADRID",
            telefono="600111222",
            registro_codigo="28000",
            tomo="1",
            seccion="8",
            folio="3",
            hoja="M-1",
        ),
        presentante=Presentante(
            nombre="ANA",
            apellido1="PRUEBA",
            apellido2="DEMO",
            nif="00000000T",
            domicilio="Calle 1",
            municipio="Madrid",
            codigo_postal="28001",
            provincia_ine="28",
            telefono="600111222",
            email="ana@example.com",
        ),
        libros=[
            Libro(
                tipo="diario",
                path=str(d),
                numero=1,
                apertura="01012025",
                cierre="31122025",
                cierre_anterior="",
            ),
            Libro(
                tipo="inventario",
                path=str(inv),
                numero=1,
                apertura="01012025",
                cierre="31122025",
                cierre_anterior="",
            ),
        ],
        ejercicio=2025,
        etiqueta="Libros 2025 EJEMPLO",
        fecha_presentacion="25072026",
    )
    zpath = tmp_path / exp.zip_basename()
    pack_zip(exp, zpath)
    assert zpath.is_file()
    assert zpath.name.startswith("LL28000B12345678")

    with zipfile.ZipFile(zpath) as zf:
        names = set(zf.namelist())
        assert "DATOS.TXT" in names
        assert "DESC.TXT" in names
        assert "NOMBRES.TXT" in names
        assert "DIARIO_001.XLSX" in names
        assert "INV_CUEN_001.PDF" in names

    rows = verify_zip(zpath)
    assert all(r["ok"] for r in rows)
    assert len(rows) == 2


def test_parse_huellas_from_datos_sample():
    sample = (
        "00101Diario\r\n"
        "001024\r\n"
        "00106U24mob72eS3Ps+5BNPDas0Mf2ATaTaHIzT/UerWxX0g=\r\n"
        "00201Inventario y cuentas anuales\r\n"
        "00206/3GFLQl+JeCenL61Aj+0X5aYYo1Uk+3QUeum83pduPs=\r\n"
    )
    pairs = parse_huellas_from_datos(sample)
    assert pairs[0][0] == "Diario"
    assert pairs[0][1] == "U24mob72eS3Ps+5BNPDas0Mf2ATaTaHIzT/UerWxX0g="
    assert pairs[1][0].startswith("Inventario")
    assert pairs[1][1] == "/3GFLQl+JeCenL61Aj+0X5aYYo1Uk+3QUeum83pduPs="


def test_pack_missing_libro_lists_all(tmp_path: Path):
    """pack_zip lista todos los libros ausentes, no solo el primero."""
    exp = Expediente(
        sociedad=Sociedad(
            razon_social="X SL",
            cif="B1",
            domicilio="c",
            municipio="m",
            codigo_postal="1",
            provincia_ine="28",
            registro_codigo="28000",
        ),
        presentante=Presentante(nombre="A", apellido1="B", nif="1"),
        libros=[
            Libro(
                tipo="diario",
                path=str(tmp_path / "no1.xlsx"),
                numero=1,
                apertura="01012025",
                cierre="31122025",
            ),
            Libro(
                tipo="inventario",
                path=str(tmp_path / "no2.pdf"),
                numero=1,
                apertura="01012025",
                cierre="31122025",
            ),
        ],
        ejercicio=2025,
    )
    miss = missing_libros(exp)
    assert len(miss) == 2
    msg = format_missing_libros(miss)
    assert "no1.xlsx" in msg and "no2.pdf" in msg
    with pytest.raises(FileNotFoundError) as ei:
        pack_zip(exp, tmp_path / "out.zip")
    assert "no1.xlsx" in str(ei.value)
    assert "no2.pdf" in str(ei.value)


def test_cli_pack_missing_file_no_traceback(tmp_path: Path):
    """CLI pack con ruta inexistente: mensaje ERROR limpio, exit 1, sin traceback."""
    cfg = {
        "ejercicio": 2025,
        "sociedad": {
            "razon_social": "X SL",
            "cif": "B12345678",
            "domicilio": "c",
            "municipio": "m",
            "codigo_postal": "28001",
            "provincia_ine": "28",
            "registro_codigo": "28000",
        },
        "presentante": {"nombre": "A", "apellido1": "B", "nif": "00000000T"},
        "libros": [
            {
                "tipo": "diario",
                "path": str(tmp_path / "missing.xlsx"),
                "numero": 1,
                "apertura": "01012025",
                "cierre": "31122025",
            }
        ],
    }
    cfg_path = tmp_path / "exp.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    rc = main(["pack", "-c", str(cfg_path), "-o", str(tmp_path / "out.zip")])
    assert rc == 1


def test_cli_verify_missing_zip(tmp_path: Path):
    rc = main(["verify", str(tmp_path / "nope.ZIP")])
    assert rc == 1


def test_official_stems_and_zip_filename():
    from open_legalia_huella.models import OFFICIAL_STEMS, Libro, resolve_stem

    assert "DIARIO" in OFFICIAL_STEMS
    assert "INV_CUEN" in OFFICIAL_STEMS
    assert "SOCUNICO" in OFFICIAL_STEMS
    assert resolve_stem("contratos") == "SOCUNICO"  # no CONTRAT inventado
    assert resolve_stem("actas") == "ACTASCON"
    lb = Libro(tipo="diario", path="/tmp/x.xlsx", numero=4)
    assert lb.zip_filename() == "DIARIO_004.XLSX"
    lb2 = Libro(tipo="INV_CUEN", path="/tmp/y.pdf", numero=4)
    assert lb2.zip_filename() == "INV_CUEN_004.PDF"


def test_tipo_numero_repetido():
    from open_legalia_huella.models import Expediente, Libro, Presentante, Sociedad

    exp = Expediente(
        sociedad=Sociedad(
            razon_social="X",
            cif="B1",
            domicilio="c",
            municipio="m",
            codigo_postal="1",
            provincia_ine="28",
            registro_codigo="28000",
        ),
        presentante=Presentante(nombre="A", apellido1="B", nif="1"),
        libros=[
            Libro(tipo="diario", path="a.xlsx", numero=1),
            Libro(tipo="diario", path="b.xlsx", numero=1),
        ],
    )
    errs = exp.validate_libros()
    assert any("repetido" in e for e in errs)


def test_unknown_tipo_raises():
    from open_legalia_huella.models import Libro, resolve_stem
    import pytest

    with pytest.raises(ValueError):
        resolve_stem("no_existe_este_libro")
    with pytest.raises(ValueError):
        Libro(tipo="no_existe", path="x.bin", numero=1).zip_filename()


def test_official_display_names_nnn01():
    """Descripcion exacta del catálogo TiposLibro de Legalia2 → NNN01."""
    from open_legalia_huella.book_types import display_name_for
    from open_legalia_huella.models import Libro

    assert display_name_for("diario") == "Diario"
    assert display_name_for("inventario") == "Inventario y cuentas anuales"
    assert display_name_for("bal_sums") == "Balances comprobación (sumas y saldos)"
    assert display_name_for("per_gan") == "Libro de pérdidas y ganancias"
    assert display_name_for("actas") == "Libro de actas"
    assert display_name_for("contratos").startswith("Libro-registro de contratos")
    assert display_name_for("ACTACODE") == "Libro de detalle de actas del consejo"
    lb = Libro(tipo="socios", path="x.pdf", numero=1)
    assert lb.display_name() == "Registro de socios"


def test_irus_validation_and_desc():
    from open_legalia_huella.datos import build_desc_txt, parse_desc_kv
    from open_legalia_huella.models import (
        Expediente,
        Libro,
        Presentante,
        Sociedad,
        validate_irus,
    )

    assert validate_irus("") is None
    assert validate_irus("123") is not None
    assert validate_irus("1234567890123") is None  # 13 dígitos
    assert validate_irus("123456789012a") is not None

    exp = Expediente(
        sociedad=Sociedad(
            razon_social="X SL",
            cif="B12345678",
            domicilio="c",
            municipio="m",
            codigo_postal="28001",
            provincia_ine="28",
            registro_codigo="28000",
            irus="1234567890123",
        ),
        presentante=Presentante(nombre="A", apellido1="B", nif="00000000T"),
        libros=[Libro(tipo="diario", path="a.xlsx", numero=1)],
        ejercicio=2025,
    )
    desc = build_desc_txt(exp)
    kv = parse_desc_kv(desc)
    assert kv["IRUS"] == "1234567890123"
    assert kv["TipoPersona"] == "J"
    assert "VersionLegalia2=1.5.7" in desc.replace("\r\n", "\n")


def test_datos_nnn01_uses_official_descripcion(tmp_path: Path):
    from open_legalia_huella.datos import build_datos_txt
    from open_legalia_huella.models import Expediente, Libro, Presentante, Sociedad

    f = tmp_path / "d.xlsx"
    f.write_bytes(b"x")
    exp = Expediente(
        sociedad=Sociedad(
            razon_social="X SL",
            cif="B1",
            domicilio="c",
            municipio="m",
            codigo_postal="1",
            provincia_ine="28",
            registro_codigo="28000",
        ),
        presentante=Presentante(nombre="A", apellido1="B", nif="1"),
        libros=[
            Libro(
                tipo="actas",
                path=str(f),
                numero=1,
                apertura="01012025",
                cierre="31122025",
            )
        ],
    )
    datos = build_datos_txt(exp)
    assert "00101Libro de actas" in datos.replace("\r\n", "\n")
