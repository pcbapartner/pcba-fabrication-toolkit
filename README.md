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

Version **0.1.1**, testing release for **macOS / KiCad 10.0**, using the legacy SWIG action-plugin runtime plus `kicad-cli`. Native validation used KiCad **10.0.6**. Windows/Linux native support, KiCad 8/9 support and official KiCad acceptance are not claimed. Release availability and downloaded-asset verification are tracked separately on the repository's [Releases page](https://github.com/pcbapartner/pcba-fabrication-toolkit/releases).

The repaired exporter distinguishes actual child-sheet `Sheetfile` properties from ordinary symbol fields, protects prior output names and recovers this attempt's files after a final publication error. Recovery is not a crash-proof multi-file transaction; a failed rollback lists remaining files for manual cleanup. The generated official legacy license label maps to GPL-3.0, while source and installed-package metadata remain GPL-3.0-or-later.

The exact 0.1.1 ZIP was installed through real PCM **Install from File** under the formal package identifier. In a fresh PCB Editor process, the single menu entry and single toolbar button both exported the synthetic regression fixture successfully, including an ordinary-symbol `Sheetfile` field. Installed files matched the ZIP; BOM/CPL/full report matched a new CLI reference byte for byte. Manufacturing data matched after creation-date fields only were normalized. See [VALIDATION.md](VALIDATION.md) for the exact ZIP SHA, counts and limits.

[GitHub Actions run 38708668214](https://github.com/pcbapartner/pcba-fabrication-toolkit/actions/runs/38708668214), at version-0.1.1 commit `c0e727113a23dcc9e54fc9458d9bec8c0a56acc2`, completed successfully on Ubuntu, Windows and macOS. Each job had **8 passes and 1 explicit skip because KiCad CLI was unavailable**. That is standard-library CI, not native KiCad or GUI validation on three platforms. Local macOS tests also passed 9/9, including native KiCad CLI.

The changes and technical review were AI-assisted. No person's independent technical review or maintenance acceptance is represented as complete. A company person must actually review, understand and take responsibility for a future official submission and personally write its required commit/MR/comment text, following KiCad's applicable tool policy. No specific professional title or separately hired maintainer is asserted as an official requirement. [PUBLISHING.md](PUBLISHING.md) separates company GitHub release steps from official KiCad submission.

The frozen v0.1.0 tag and installation/source assets remain unchanged. Source and issues: [pcbapartner/pcba-fabrication-toolkit](https://github.com/pcbapartner/pcba-fabrication-toolkit).

## Install

For the verified local ZIP or a published release asset, open **Plugin and Content Manager → Install from File…** and select `dist/pcbapartner-fabrication-toolkit-0.1.1.zip`. Apply pending changes if shown. Reopen the PCB Editor, or refresh plugins using **Tools → External Plugins → Refresh Plugins**.

Once an official repository submission has been accepted, users can also install by searching the package name in PCM. Official acceptance is a separate publication step.

## Use

1. Save both the board and schematic. The root schematic must have the same filename as the board and sit beside it; referenced child sheets are supported.
2. Click the toolbar button, or **Tools → External Plugins → PCBA Partner Fabrication Toolkit**.
3. Review the completion summary and `_preflight.txt`. The files are written to `<project>/pcbapartner/`; the plugin opens that folder after the summary is dismissed.

Unsaved editor changes are excluded from exports. A board without a matching schematic still exports Gerbers and CPL, and the report states that the BOM is missing. An error in the basic pre-flight report does not prevent writing files for inspection; a failed CLI command does prevent publishing that export's partial files.

### Command line

```bash
python3 plugins/pcbapartner_export.py path/to/board.kicad_pcb -o out/
```

Set `KICAD_CLI=/full/path/to/kicad-cli` when it is not on your PATH. On macOS, the standard `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` is detected automatically. Python 3.9 or later is used for the validated command-line workflow. The CLI exits with 1 on an export failure, and 0 after exporting successfully even if the pre-flight report contains errors or warnings.

### Regression tests

```bash
python -m unittest discover -s tests -p test_regressions.py -v
```

This suite uses only the standard library. Its native test is explicitly skipped when KiCad CLI is unavailable, unreadable or outside the declared 10.0 series. The three-OS CI workflow uses Python 3.12, read-only repository permission and pinned official actions. It installs no KiCad and publishes no packages.

## MPN and Manufacturer fields

For each component, the first nonempty value from these aliases is used, case-insensitively:

- MPN: `MPN`, `Manufacturer Part Number`, `MFR PN`, `MFG PN`, `Mfr. No`, `PartNumber`, `Part Number`, `MPN1`
- Manufacturer: `Manufacturer`, `MFR`, `MFG`, `Mfr`, `Manufacturer_Name`

The canonical BOM always contains Manufacturer and MPN columns. Components are grouped only when Value, Footprint, Manufacturer and MPN all match. Field aliases can vary between components without losing their values. Only the root schematic and its referenced child sheets are inspected.

## Limits

The report is a basic consistency check. It does not validate closed outlines, electrical rules, footprint-to-symbol synchronization, manufacturer rotation requirements, sourcing availability or fabrication tolerances. Inspect the Gerbers and run KiCad's DRC before ordering. The exporter uses the default assembly variant; alternate variants are not currently exposed in the plugin.

## License

GPL-3.0-or-later. The full license is in `LICENSE` and is included as `plugins/LICENSE` in the installation ZIP. Maintained by PCBA Partner. Source contributions and [issue reports](https://github.com/pcbapartner/pcba-fabrication-toolkit/issues) are welcome.
