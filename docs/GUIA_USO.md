# Guía de uso — open-legalia-huella

Herramienta **open source** para:

1. Calcular la **huella digital** de los libros mercantiles (mismo algoritmo que Legalia2).
2. **Verificar** un ZIP generado por Legalia2 (o por esta herramienta).
3. **Empaquetar** un ZIP de presentación (`LL{registro}{CIF}.ZIP`) en macOS/Linux/Windows.

No sustituye el certificado digital ni el pago en la sede de Registradores.

---

## 1. ¿La huella cambia cada año?

**No por el año en sí.** Cambia solo si cambia el **contenido del fichero**.

| Situación | ¿Cambia la huella? |
|-----------|--------------------|
| Mismo PDF/XLSX bit a bit | **No** (misma huella) |
| Nuevo ejercicio 2026 con otros asientos | **Sí** (otro contenido → otro SHA-256) |
| Re-exportas Excel y Excel reescribe metadatos internos | **Sí** (aunque “parezca” igual) |
| Renombras el fichero sin tocar bytes | **No** |

Fórmula (Legalia2 1.5.7, verificada con ZIP real):

```text
huella = Base64( SHA-256( bytes del fichero ) )
```

No entra el CIF, ni la fecha, ni el número de libro en el hash: eso va en `DATOS.TXT` aparte.

---

## 2. Instalación (Mac / Linux / Windows)

```bash
# Clonar (cuando esté en GitHub)
git clone https://github.com/shakisha/open-legalia-huella.git
cd open-legalia-huella

# Opción A: editable
python3 -m pip install -e .

# Opción B: sin instalar, desde el repo
export PYTHONPATH=src
python3 -m open_legalia_huella.cli --help
```

Requisito: **Python 3.10+**. Sin dependencias obligatorias.

Opcional YAML: `pip install 'open-legalia-huella[yaml]'`

---

## 3. Comandos

### 3.1 Calcular huellas

```bash
open-legalia-huella huella diario_2025.xlsx inventario_2025.pdf
open-legalia-huella huella --hex diario_2025.xlsx
```

Salida: nombre + huella Base64 (la misma que pondría Legalia en `DATOS.TXT`).

Equivalente con OpenSSL:

```bash
openssl dgst -sha256 -binary diario_2025.xlsx | base64
```

### 3.2 Verificar un ZIP de Legalia

```bash
open-legalia-huella verify LL28000B00000000.ZIP
```

Comprueba que cada binario del ZIP tiene el SHA-256 Base64 declarado en `DATOS.TXT`.

### 3.3 Crear plantilla de expediente

```bash
open-legalia-huella init -o expediente.json
# o: open-legalia-huella init -o expediente.yaml -f yaml
```

Edita:

- `sociedad` (CIF, domicilio, tomo/folio/hoja, código de registro)
- `presentante` (quien firma en sede)
- `libros[].path` → rutas a tus PDF/XLSX
- fechas `apertura` / `cierre` / `cierre_anterior` en **DDMMYYYY**
- `numero` de libro (1, 2, 3…; si no es 1, `cierre_anterior` suele ser obligatorio en Legalia)

### 3.4 Generar el ZIP de presentación

```bash
# Simulación (solo huellas)
open-legalia-huella pack -c expediente.json --dry-run

# Generar
open-legalia-huella pack -c expediente.json -o LL28000B00000000.ZIP
```

El ZIP incluye:

```
DIARIO_00N.XLSX   (o .PDF)
INV_CUEN_00N.PDF
DATOS.TXT
DESC.TXT
NOMBRES.TXT
```

Nombre por defecto: `LL` + código registro (5 dígitos) + CIF + `.ZIP`  
(ej. registro `28000` → `LL28000B00000000.ZIP`).

---

## 4. Flujo recomendado (legalización anual)

```text
1. Exportar Diario + Inventario/CCAA desde tu contabilidad (PDF/XLSX definitivos)
2. open-legalia-huella huella …          # anotar / auditar
3. open-legalia-huella pack -c …         # ZIP
4. open-legalia-huella verify …          # control de calidad
5. Sede registradores.org → LEGALIZACIÓN (no depósito CCAA)
6. Adjuntar ZIP, firmar con certificado, pagar tasa, guardar acuse WEBT…
```

**Cada año nuevo:** repites con los ficheros del ejercicio. Las huellas serán distintas porque los libros son distintos — no porque el algoritmo “caduque”.

---

## 5. Formato DATOS.TXT (resumen)

Líneas `CODIGO`+`valor`, CRLF, encoding Latin-1 (tildes).

| Código | Significado (observado) |
|--------|-------------------------|
| 100 | Provincia registro (texto) |
| 101 | Fecha presentación DDMMYYYY |
| 102 | Razón social |
| 105 | CIF |
| 106–109 | Domicilio, municipio, CP, provincia INE |
| 111–112 | Teléfono, código RM |
| 201–206 | Tomo, sección, folio, “REGISTRO MERCANTIL”, hoja |
| 301–311 | Presentante (nombre, apellidos, NIF, domicilio, email…) |
| 401 | Flag (p.ej. `NO`) |
| 501 | Número de libros |
| NNN01 | Nombre del libro (“Diario”, “Inventario y cuentas anuales”) |
| NNN02 | Número de libro |
| NNN03–05 | Apertura, cierre, cierre anterior (DDMMYYYY) |
| NNN06 | **Huella** Base64(SHA-256) |

---

## 6. Limitaciones y honestidad open source

| Sí | No |
|----|-----|
| Misma huella que Legalia2 sobre el mismo binario | Garantía legal de admisión del ZIP en todos los RM sin probar |
| Pack multiplataforma (Mac/Linux/Win) | Sustituir Autofirma / certificado / pago de tasas |
| Verificar ZIPs existentes | Clonar toda la UI y validaciones de negocio de Legalia |
| Código auditable MIT | Afiliación con el Colegio de Registradores |

Recomendación: la primera vez, genera el ZIP aquí, **verifícalo**, y si puedes contrasta con un ZIP de Legalia2 sobre los mismos ficheros (`verify` debe dar OK en ambos).

---

## 7. Publicar en GitHub

```bash
cd open-legalia-huella
# Quita datos reales de sociedad de examples/ si los hubiera
git init
git add .
git commit -m "Initial open-legalia-huella: SHA-256 Base64 huellas + pack ZIP"
# gh auth login
gh repo create open-legalia-huella --public --source=. --remote=origin --push
```

Actualiza en `pyproject.toml` la URL `Homepage` con tu usuario.

---

## 8. Licencia

MIT — ver `LICENSE`.
