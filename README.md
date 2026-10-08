# PCBA Partner Fabrication Toolkit for KiCad

A local, vendor-neutral fabrication exporter for the KiCad PCB Editor. It reads the saved project and writes:

| Output | Contents |
|---|---|
| `<board>_<timestamp>_Gerber_Drill.zip` | All enabled copper layers, front/back mask, paste and silkscreen, Edge.Cuts, separate PTH/NPTH Excellon drills, drill maps and a Gerber job file |
| `<board>_<timestamp>_BOM.csv` | Grouped BOM: Designator, Value, Footprint, Qty, Manufacturer, MPN; DNP and symbols excluded from BOM are omitted |
| `<board>_<timestamp>_CPL.csv` | Both-side placement in mm: Designator, Value, Package, Mid X, Mid Y, Rotation, Layer; DNP and footprints excluded from position files are omitted |
| `<board>_<timestamp>_preflight.txt` | Missing MPNs, missing schematic footprints, BOM/placement differences, empty placement and missing Edge.Cuts objects |

BOM and CPL include through-hole parts when KiCad includes them. The output uses KiCad's absolute board origin and native placement rotation conventions. A timestamp keeps repeated exports separate. All commands complete in a staging directory before the files are copied into the output folder.

The exporter makes no network requests, uploads no design data and opens no commercial-service page. Send the files to an assembler of your choice after reviewing them.

## Status and compatibility

Version **0.1.0**, testing release. Validated with **KiCad 10.0.6 on macOS**, including real PCM installation and a successful PCB Editor menu export. The GUI-produced BOM, CPL and report match the CLI reference; the manufacturing ZIP contains all 16 expected files for the four-layer fixture. This package declares compatibility with KiCad **10.0 only** and uses the legacy SWIG action-plugin runtime plus `kicad-cli`. KiCad 8, 9 and other operating systems have not been validated.

Source and issue tracking are hosted at [pcbapartner/pcba-fabrication-toolkit](https://github.com/pcbapartner/pcba-fabrication-toolkit). Release assets are provided through the repository's Releases page when available. This plugin has not been accepted into KiCad's official repository. See [PUBLISHING.md](PUBLISHING.md) for release and submission steps, and [VALIDATION.md](VALIDATION.md) for actual checks.


Repository URL maintenance on the current branch keeps version 0.1.0 and exporter behavior unchanged. The published v0.1.0 tag, installation ZIP, source ZIP and SHA-256 assets retain their original bytes; their embedded historical URLs are not rewritten. This working-branch update is not a new package release or official KiCad acceptance.

## Install

From the KiCad project manager, open **Plugin and Content Manager → Install from File…** and select `dist/pcbapartner-fabrication-toolkit-0.1.0.zip`. Apply pending changes if shown. Reopen the PCB Editor, or refresh plugins using **Tools → External Plugins → Refresh Plugins**.

Once an official repository submission has been accepted, users can also install by searching the package name in PCM. Official acceptance is a separate publication step.

## Use

1. Save both the board and schematic. The root schematic must have the same filename as the board and sit beside it; referenced child sheets are supported.
2. Click the toolbar button, or **Tools → External Plugins → PCBA Partner Fabrication Toolkit**.
3. Review the completion summary and `_preflight.txt`. The files are written to `<project>/pcbapartner/`; the plugin opens that folder after the summary is dismissed.

Unsaved editor changes are excluded from exports. A board without a matching schematic still exports Gerbers and CPL, and the report states that the BOM is missing. An error in the basic pre-flight report does not prevent writing files for inspection; a failed CLI command does prevent publishing that export's partial files.

### Command line / CI

```bash
python3 plugins/pcbapartner_export.py path/to/board.kicad_pcb -o out/
```

Set `KICAD_CLI=/full/path/to/kicad-cli` when it is not on your PATH. On macOS, the standard `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` is detected automatically. Python 3.9 or later is used for the validated command-line workflow. The CLI exits with 1 on an export failure, and 0 after exporting successfully even if the pre-flight report contains errors or warnings.

## MPN and Manufacturer fields

For each component, the first nonempty value from these aliases is used, case-insensitively:

- MPN: `MPN`, `Manufacturer Part Number`, `MFR PN`, `MFG PN`, `Mfr. No`, `PartNumber`, `Part Number`, `MPN1`
- Manufacturer: `Manufacturer`, `MFR`, `MFG`, `Mfr`, `Manufacturer_Name`

The canonical BOM always contains Manufacturer and MPN columns. Components are grouped only when Value, Footprint, Manufacturer and MPN all match. Field aliases can vary between components without losing their values. Only the root schematic and its referenced child sheets are inspected.

## Limits

The report is a basic consistency check. It does not validate closed outlines, electrical rules, footprint-to-symbol synchronization, manufacturer rotation requirements, sourcing availability or fabrication tolerances. Inspect the Gerbers and run KiCad's DRC before ordering. The exporter uses the default assembly variant; alternate variants are not currently exposed in the plugin.

## License

GPL-3.0-or-later. The full license is in `LICENSE` and is included as `plugins/LICENSE` in the installation ZIP. Maintained by PCBA Partner. Source contributions and [issue reports](https://github.com/pcbapartner/pcba-fabrication-toolkit/issues) are welcome.
