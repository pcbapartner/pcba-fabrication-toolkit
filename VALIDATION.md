# Verification record for 0.1.1

Recorded on 2026-10-15. Version 0.1.1 is a testing release for macOS / KiCad 10.0. This record verifies local package bytes, real GUI outputs and the cited CI run. Public release availability and anonymous asset downloads require their separate observed release records. No official KiCad acceptance or independent human technical-review approval is claimed.

## Exact installation package and schemas

```text
File: pcbapartner-fabrication-toolkit-0.1.1.zip
SHA-256: d3532161b5ad8bd442e2c163ff8a0b2d8bda310fdba2680a3b376e2d4afa8da0
ZIP bytes: 20051
Uncompressed bytes: 56481
Identifier: com.pcbapartner.fabrication-toolkit
Version: 0.1.1
Platforms: macos
KiCad: 10.0–10.0; SWIG runtime
```

The six members are metadata.json, resources/icon.png, plugins/__init__.py, plugins/pcbapartner_export.py, plugins/icon.png and plugins/LICENSE. All match the verified source bytes. Two builds produced the same installation ZIP SHA. The full GPL license and 64 px / 24 px icons are present. The source ZIP uses an audited 15-file allowlist without fixtures, customer files or credentials; its SHA is listed separately to avoid a self-referencing source hash.

Source/installed metadata pass the saved current PCM v2 schema. Generated official metadata pass both saved v1 and v2 schemas. Actual GPL-3.0-or-later remains unchanged; only the official legacy outer label maps to GPL-3.0. The schema snapshots were fetched 2026-10-15. Local schema validation is distinct from the official metadata repository's network CI and upstream license-policy acceptance.

## Regressions and actual 0.1.1 hosted CI

Local macOS ran `python -m unittest discover -s tests -p test_regressions.py -v`: 9 passed, 0 skipped, including the native KiCad 10.0.6 BOM test. Tests cover sheet context/nested relative paths/cycles/escaping, all four final-move failures, existing-file protection, failed-rollback disclosure, successful publication and real temporary-package license behavior.

[Run 38708668214](https://github.com/pcbapartner/pcba-fabrication-toolkit/actions/runs/38708668214), at version-0.1.1 commit `c0e727113a23dcc9e54fc9458d9bec8c0a56acc2`, completed successfully:

| Job | Actual image | CPython | Result |
|---|---|---|---|
| [Ubuntu job 116334327731](https://github.com/pcbapartner/pcba-fabrication-toolkit/actions/runs/38708668214/job/116334327731) | ubuntu-24.04 | 3.12.15 | 8 passed, 1 native skip |
| [Windows job 116334327559](https://github.com/pcbapartner/pcba-fabrication-toolkit/actions/runs/38708668214/job/116334327559) | windows-2025-vs2026 | 3.12.10 | 8 passed, 1 native skip |
| [macOS job 116334327964](https://github.com/pcbapartner/pcba-fabrication-toolkit/actions/runs/38708668214/job/116334327964) | macos-26-arm64 | 3.12.10 | 8 passed, 1 native skip |

Each log states `Ran 9 tests`, `OK (skipped=1)` and explicitly reports KiCad CLI unavailable. These 24 standard-library passes and 3 skips do not establish Windows/Linux native KiCad, PCM or GUI behavior. Earlier run 38706165277 tested the repaired core before its 0.1.0 version string was bumped; it is historical evidence, not substituted for this 0.1.1 run.

## Exact 0.1.1 GUI and output checks

Real PCM Install from File upgraded the formal identifier to the exact ZIP above. All four installed plugin files matched its members byte for byte, including core SHA `bd220160fef8a1f78a3577cc504558142906ffdaac4418520594d508d4afc5f5`. A fresh PCB Editor exposed only one formal plugin menu entry and one toolbar button. Both exported the saved synthetic board/schematic containing an ordinary-symbol `Sheetfile=not-a-child.kicad_sch` property.

Each menu/toolbar export produced 4 copper layers, 7 BOM rows, 8 CPL parts, 0 errors, 3 warnings and 1 information item; the report says 0.1.1. BOM, CPL and full report matched a new real KiCad 10.0.6 CLI reference byte for byte. All 32 manufacturing ZIP members were unique/nonempty, CRC-correct and structurally valid; their full bytes matched after only creation-date values were normalized. No coordinate, aperture, tool, layer, path, project ID, size or manufacturing value was removed or changed. The board and schematic hashes stayed unchanged.

Only the observed Gerber TF.CreationDate and generation-comment date, Excellon generation-comment/TF.CreationDate, and gbrjob Header.CreationDate values were normalized. Container ZIP hashes alone were not used as an equivalence test.

Earlier repaired-core GUI testing used isolated identifier com.pcbapartner.fabrication-toolkit-review, prior 0.1.0 version string and a distinct display name: menu, toolbar and ordinary-Sheetfile toolbar all passed. It was uninstalled and original formal files were preserved at that stage. The final 0.1.1 test deliberately upgraded the formal identifier; it does not claim the old installed 0.1.0 core remained unchanged.

## Limits, responsibility and preserved history

- Native GUI evidence is macOS KiCad 10.0.6 only, using offline Install from File. A temporary online PCM index was not verified after catalog SSL connection errors; TLS/certificates were not bypassed.
- Saved synthetic fixtures were checked. Do not infer complete unsaved-project/error-path/large-project, manufacturer-rotation, DRC or fabrication approval from these tests.
- The work was AI-assisted. Before an official submission, a company person must actually review and understand it, take responsibility and personally write required official commit/MR/comment text under applicable KiCad tool policy. The optional maintainer field does not impose a separately hired person or specific professional credential.
- Official GitLab MR acceptance remains separate. Public tag/source/asset identity and anonymous downloads must be verified when publication occurs. Frozen v0.1.0 stays at dfad891aaab095475809fae179539f7dc28c6c0d with its four assets unchanged.
