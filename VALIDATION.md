# Verification record

Checked on 2026-10-07 with KiCad **10.0.6** on macOS. This release declares compatibility only with KiCad 10.0. Windows, Linux and KiCad 8/9 have not been tested.

## Code repairs

- Normalizes Manufacturer and MPN aliases per component before grouping; retains case variants and separates different manufacturers.
- Inspects only the root schematic and referenced child sheets, instead of unrelated schematics in the project tree.
- Reports every placement reference missing from the BOM, including references previously suppressed by broad prefixes such as `G`.
- Stages an export before publishing it and translates filesystem/CLI launch errors into a concise export error.
- Uses unique timestamps to keep repeated exports separate.
- Removes quote-page/browser connections and promotional report links from the local exporter.
- Includes the full GPL license in the installation package; uses schema v2, GPL-3.0-or-later and explicit SWIG/KiCad 10.0 metadata.
- Builds the ZIP reproducibly and writes a SHA-256 file.

## Executed checks

| Check | Result |
|---|---|
| `kicad-cli version` | `10.0.6` |
| Bundled Python `import pcbnew; import wx` | Passed; pcbnew 10.0.6, wx 4.2.2a1 / wxWidgets 3.2.8 |
| Four-layer fixture | Passed: 16 Gerber/drill/job files, 8 CPL parts, 7 grouped BOM lines |
| Two-layer fixture | Passed: 14 Gerber/drill/job files, 8 CPL parts, 7 grouped BOM lines |
| KiCad Arduino Nano template | Passed: 14 Gerber/drill/job files, 2 CPL parts, 2 BOM lines; missing-MPN-field warning |
| DNP | R6 absent from both BOM and CPL |
| Bottom-side / through-hole | C1 exported as Bottom; J1 included |
| MPN aliases / grouping | Mixed-case `mpn` / `MPN` CLI test passed; R3 alias retained; R1/R2 different manufacturers kept separate; R4/R5 grouped with Qty 2 |
| Report issues | Missing C1 MPN, U1 footprint and G1 board/BOM mismatch detected |
| No schematic / no outline | Missing BOM warning and missing Edge.Cuts error detected; no phantom BOM written |
| Failure after Gerber generation | No partial package or staging directory left in target |
| Invalid output destination | Concise `ExportError` returned |
| Hierarchical field discovery | Child fields found; unrelated schematic fields ignored |
| PCM JSON schema | Package and submission metadata pass KiCad's bundled PCM v2 schema |
| Archive layout/license/icons | Six correct members, full GPL license, 64 px PCM and 24 px toolbar icons |
| SHA-256 and sizes | Archive hash, downloaded size and uncompressed size match submission metadata |
| Reproducible build | Two successive builds produce the same SHA-256 |

The test boards are synthetic fixtures for export verification; they do not represent a functional or approved circuit. CLI success can coexist with report warnings and errors, by design.

## Final installation package

```text
File: dist/pcbapartner-fabrication-toolkit-0.1.0.zip
SHA-256: 56fd3e363197e701b35346a7257cee35df976af52a351e0ff97314d52c2ce23a
ZIP bytes: 19400
Uncompressed bytes: 54523
```

ZIP members:

```text
metadata.json
resources/icon.png
plugins/__init__.py
plugins/pcbapartner_export.py
plugins/icon.png
plugins/LICENSE
```

## GUI check

**Passed in the real KiCad 10.0.6 PCB Editor on macOS.** The main task installed the original local-delivery ZIP through PCM → Install from File; PCM listed PCBA Partner Fabrication Toolkit as installed. It then opened the synthetic four-layer fixture and ran **Tools → External Plugins → PCBA Partner Fabrication Toolkit**.

The completion dialog reported **Copper layers 4, Placed parts 8, Errors 0, Warnings 3**. The exported BOM has 7 rows and CPL has 8 parts; both CSV contents match the CLI reference exactly. The report also matches exactly. The Gerber/drill ZIP has all 16 expected nonempty members, with the same member list as the CLI reference.

The local execution record retains screenshots of PCM installation and PCB Editor export completion. They are not bundled in the public source candidate.

The menu-triggered workflow and exported files are verified for the original local-delivery ZIP. This publication candidate changes only the source/issue/release target URLs in package metadata; its plugin code and icons are byte-identical to the GUI-tested version. The candidate ZIP itself has not undergone a separate GUI reinstall. A separate toolbar-button click and other operating systems were not tested. Calling `ActionPlugin.register()` from an independent bundled-Python process requires the PCB Editor's host context; the real GUI test covers that missing context.

## Publication status

The current source target is `pcbapartner/pcba-fabrication-toolkit`. Version 0.1.0 was originally published and anonymously download-verified under `13712831373g-alt/pcba-fabrication-toolkit` at commit `dfad891aaab095475809fae179539f7dc28c6c0d`. The official KiCad merge request has not been submitted; official acceptance is unverified.

## Repository URL maintenance

The current-branch metadata homepage, issue tracker and future-build release URL use the brand organization path. Version stays 0.1.0. This documentation and metadata change does not rerun or broaden any of the earlier CLI, GUI, operating-system or KiCad-version checks. The exporter, ActionPlugin, icons and license files are unchanged.

The frozen v0.1.0 tag remains at `dfad891aaab095475809fae179539f7dc28c6c0d`; its original installation/source ZIPs and SHA-256 files are not rebuilt or overwritten. The original public owner `13712831373g-alt/pcba-fabrication-toolkit` and its verification records are retained as historical provenance. Actual transfer identity, old/new URL redirects and anonymous asset downloads must be recorded separately after they have been observed; this working-branch text is not a transfer-verification result. No new release, human technical review or official KiCad MR is claimed.
