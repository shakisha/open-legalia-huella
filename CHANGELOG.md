# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-07-25

### Added

- Official **TiposLibro** catalog from Legalia2 1.5.7 (20 book types): exact
  `Descripcion` text for DATOS field `NNN01` and ZIP stem (`NombreFichero`).
- Module `book_types.py` with codes, stems, and date-validation flags.
- **IRUS** (Identificador Registral Mercantil): optional `sociedad.irus` in
  config; written as `IRUS=` in `DESC.TXT`; validated as **13 digits** when set.
- DATOS field **207** (`sociedad.otros`) and presentante **fax** (309).
- `tipo_persona` (`J` / `F`) in config → `TipoPersona=` in `DESC.TXT`.
- `parse_desc_kv()` helper and `validate_irus()`.
- Dry-run shows official NNN01 labels, IRUS, and ZIP entry names.

### Changed

- Display names for books now use Legalia’s official Spanish descriptions
  (e.g. actas → «Libro de actas», not a shortened label).
- Expediente validation covers books + IRUS + `tipo_persona`.

### Documentation

- `docs/GUIA_USO.md`: full TiposLibro table and IRUS section.
- Example `expediente.example.json` includes `irus`, `otros`, `tipo_persona`.

## [0.3.0] — 2026-07-25

### Added

- Full ZIP stem catalog (`DIARIO`, `INV_CUEN`, `SOCUNICO`, `ACTASCON`, …)
  with config aliases (`diario`, `contratos` → `SOCUNICO`, etc.).
- Pack validation: unknown book type; **same type + number** twice
  (`TipoLibroNumeroRepetido`).
- ZIP size limit **300 MiB** (`BytesMaximosZip` from Registradores catalog).
- Dry-run prints resolved ZIP filenames (`STEM_NNN.EXT`).

### Fixed

- `contratos` no longer maps to the non-existent stem `CONTRAT` (correct:
  `SOCUNICO`).

## [0.2.0] — 2026-07-25

### Added

- Initial public release: CLI `huella`, `verify`, `init`, `pack`.
- Huella formula: `Base64(SHA-256(file bytes))` (Legalia2-compatible).
- Pack ZIP with `DATOS.TXT`, `DESC.TXT`, `NOMBRES.TXT`.
- Clean error messages (missing files, bad config, corrupt ZIP).
- Synthetic examples and tests only (no real company data).

---

[0.4.0]: https://github.com/shakisha/open-legalia-huella/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/shakisha/open-legalia-huella/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/shakisha/open-legalia-huella/releases/tag/v0.2.0
