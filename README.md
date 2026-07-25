# open-legalia-huella

**Legalización de libros mercantiles sin Legalia2 en Windows.**

Calcula la **huella digital** de tus libros y genera el **ZIP de presentación** al Registro Mercantil (España), con el mismo algoritmo de huella que usa Legalia2.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ¿La huella cambia cada año?

**No por ser “otro año”.**  
La huella es solo:

```text
Base64( SHA-256( contenido del fichero ) )
```

| Situación | ¿Nueva huella? |
|-----------|----------------|
| Mismos bytes del PDF/XLSX | No |
| Libros del ejercicio siguiente (otros asientos) | **Sí** (otro contenido) |
| Excel re-guardado que toca metadatos internos | Sí |

No se mezcla el CIF ni la fecha en el hash: eso va en `DATOS.TXT`.

## Instalación

```bash
git clone https://github.com/shakisha/open-legalia-huella.git
cd open-legalia-huella
python3 -m pip install -e .
open-legalia-huella --help
```

Python **≥ 3.10**. Sin dependencias obligatorias.

Versión actual: **0.4.0** — catálogo TiposLibro Legalia (textos NNN01 exactos) + IRUS 13 dígitos en DESC.TXT.

## Uso rápido

```bash
# 1) Huella de un libro (igual que Legalia)
open-legalia-huella huella diario.xlsx inventario.pdf

# 2) Verificar un ZIP generado por Legalia o por esta herramienta
open-legalia-huella verify LL28000B00000000.ZIP

# 3) Plantilla de expediente + empaquetado
open-legalia-huella init -o expediente.json
# ... edita sociedad, presentante, rutas de libros ...
open-legalia-huella pack -c expediente.json --dry-run
open-legalia-huella pack -c expediente.json -o salida.ZIP
```

## Documentación

- **[Guía de uso completa](docs/GUIA_USO.md)** — flujo anual, formato DATOS.TXT, límites legales/técnicos
- **[Changelog](CHANGELOG.md)** — historial de versiones
- **[Ejemplo de config](examples/expediente.example.json)**

## Prueba del algoritmo

La huella de Legalia2 es exactamente el SHA-256 del fichero en Base64. Puedes comprobarlo con OpenSSL:

```bash
openssl dgst -sha256 -binary diario.xlsx | base64
# → misma cadena que el campo NNN06 de DATOS.TXT
```

Los tests del repo generan un ZIP sintético, lo verifican y comprueban round-trip pack/verify.

## Qué incluye / qué no

| Incluye | No incluye |
|---------|------------|
| Huella idéntica a Legalia2 | Certificado / Autofirma / pago de tasas |
| Pack ZIP multiplataforma (Mac/Linux/Win) | Garantía de admisión en todos los RM sin prueba |
| Verificación de ZIPs existentes | UI completa ni validaciones de negocio de Legalia |
| Código MIT auditable | Software oficial del Colegio de Registradores |

## Estructura del repo

```
src/open_legalia_huella/   # librería + CLI
tests/                     # pytest
docs/GUIA_USO.md
examples/
```

## Desarrollo

```bash
python3 -m pip install -e ".[dev]"
pytest -q
```

## Licencia

MIT — ver [LICENSE](LICENSE).

**Disclaimer:** ingeniería inversa de interoperabilidad sobre el formato de huella/ZIP observado. No hay afiliación con el Colegio de Registradores ni con Legalia2. Uso bajo tu responsabilidad.
