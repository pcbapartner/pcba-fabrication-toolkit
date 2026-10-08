"""PCBA Partner Fabrication Toolkit - core exporter.

Generates an assembly-ready package (Gerbers + drill ZIP, BOM CSV, CPL CSV and a
pre-flight check report) from a KiCad project by driving `kicad-cli`.

This module has no dependency on pcbnew/wx so it can also be used from a shell:

    python3 pcbapartner_export.py path/to/board.kicad_pcb [-o OUTPUT_DIR]

License: GPL-3.0-or-later
"""

import argparse
import csv
import datetime
import glob
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

VERSION = "0.1.0"

# Candidate schematic field names, first match wins.
MPN_FIELDS = ["MPN", "Manufacturer Part Number", "MFR PN", "MFG PN", "Mfr. No", "PartNumber", "Part Number", "MPN1"]
MFR_FIELDS = ["Manufacturer", "MFR", "MFG", "Mfr", "Manufacturer_Name"]

FIXED_LAYERS = [
    "F.Paste", "F.Silkscreen", "F.Mask",
    "B.Mask", "B.Silkscreen", "B.Paste",
    "Edge.Cuts",
]


class ExportError(Exception):
    pass


# --------------------------------------------------------------------------- #
# kicad-cli discovery
# --------------------------------------------------------------------------- #
def find_kicad_cli():
    candidates = []
    env = os.environ.get("KICAD_CLI")
    if env:
        candidates.append(env)
    which = shutil.which("kicad-cli")
    if which:
        candidates.append(which)
    # Inside KiCad's bundled Python the interpreter lives next to (or below) kicad-cli.
    exe_dir = os.path.dirname(sys.executable)
    for up in range(0, 6):
        d = os.path.abspath(os.path.join(exe_dir, *([".."] * up)))
        candidates += [
            os.path.join(d, "kicad-cli"),
            os.path.join(d, "kicad-cli.exe"),
            os.path.join(d, "bin", "kicad-cli.exe"),
            os.path.join(d, "MacOS", "kicad-cli"),
        ]
    candidates += [
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
        "/usr/bin/kicad-cli",
        "/usr/local/bin/kicad-cli",
    ]
    for pf in (os.environ.get("ProgramFiles"), r"C:\Program Files"):
        if pf:
            candidates += glob.glob(os.path.join(pf, "KiCad", "*", "bin", "kicad-cli.exe"))
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise ExportError(
        "kicad-cli was not found. Install KiCad 10.0, or set the KICAD_CLI "
        "environment variable to the full path of kicad-cli."
    )


def _run(cli, args):
    try:
        proc = subprocess.run([cli] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as exc:
        raise ExportError("Could not run kicad-cli: %s" % exc) from exc
    out = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0:
        raise ExportError("kicad-cli %s failed:\n%s" % (" ".join(args[:3]), out))
    return out


# --------------------------------------------------------------------------- #
# Board / schematic inspection
# --------------------------------------------------------------------------- #
def copper_layers(board_text):
    """Return copper layer names in stack order, e.g. F.Cu, In1.Cu, ..., B.Cu."""
    m = re.search(r"\(layers\s*(.*?)\n\s*\)", board_text, re.S)
    block = m.group(1) if m else board_text
    inner = sorted(
        set(re.findall(r'"(In\d+\.Cu)"', block)),
        key=lambda n: int(re.search(r"\d+", n).group()),
    )
    return ["F.Cu"] + inner + ["B.Cu"]


def schematic_fields(schematic):
    """Inspect only this schematic and its referenced child sheets."""
    names = set()
    pending, visited = [os.path.abspath(schematic)], set()
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        with open(path, encoding="utf-8", errors="replace") as fh:
            source = fh.read()
        names.update(re.findall(r'\(property\s+"([^"]+)"', source))
        for child in re.findall(r'\(property\s+"Sheetfile"\s+"([^"\\]+)"', source, re.I):
            # KiCad resolves child sheets relative to their parent schematic.
            child = child.replace("${KIPRJMOD}", os.path.dirname(os.path.abspath(schematic)))
            pending.append(os.path.abspath(os.path.join(os.path.dirname(path), child)))
    return names


def _alias_fields(candidates, available):
    """Keep every case variant, in deterministic alias priority order."""
    fields = []
    for candidate in candidates:
        matches = sorted((field for field in available if field.lower() == candidate.lower()),
                         key=lambda field: (field != candidate, field))
        fields.extend(field for field in matches if field not in fields)
    return fields


# --------------------------------------------------------------------------- #
# Exporters
# --------------------------------------------------------------------------- #
def export_gerbers_zip(cli, board, board_text, out_dir, base):
    tmp = tempfile.mkdtemp(prefix="pcbapartner_")
    try:
        layers = copper_layers(board_text) + FIXED_LAYERS
        _run(cli, ["pcb", "export", "gerbers", "-o", tmp, "-l", ",".join(layers),
                   "--subtract-soldermask", "--check-zones", board])
        _run(cli, ["pcb", "export", "drill", "-o", tmp, "--format", "excellon",
                   "--excellon-units", "mm", "--excellon-separate-th",
                   "--generate-map", "--map-format", "gerberx2", board])
        zpath = os.path.join(out_dir, base + "_Gerber_Drill.zip")
        files = sorted(f for f in os.listdir(tmp) if os.path.isfile(os.path.join(tmp, f)))
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(os.path.join(tmp, f), f)
        return zpath, files, len(layers) - len(FIXED_LAYERS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def export_cpl(cli, board, out_dir, base):
    raw = os.path.join(out_dir, ".pos_raw.csv")
    _run(cli, ["pcb", "export", "pos", "-o", raw, "--format", "csv", "--units", "mm",
               "--side", "both", "--exclude-dnp", board])
    rows = []
    with open(raw, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "Designator": r.get("Ref", ""),
                "Value": r.get("Val", ""),
                "Package": r.get("Package", ""),
                "Mid X (mm)": r.get("PosX", ""),
                "Mid Y (mm)": r.get("PosY", ""),
                "Rotation": r.get("Rot", ""),
                "Layer": "Top" if r.get("Side", "").lower().startswith("top") else "Bottom",
            })
    os.remove(raw)
    path = os.path.join(out_dir, base + "_CPL.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else
                           ["Designator", "Value", "Package", "Mid X (mm)", "Mid Y (mm)", "Rotation", "Layer"])
        w.writeheader()
        w.writerows(rows)
    return path, rows


def _expand_refs(refs):
    """'R1-R4,C2' -> ['R1','R2','R3','R4','C2']"""
    out = []
    for part in [p.strip() for p in refs.split(",") if p.strip()]:
        m = re.match(r"^([A-Za-z_#]+)(\d+)-([A-Za-z_#]+)?(\d+)$", part)
        if m:
            prefix, a, b = m.group(1), int(m.group(2)), int(m.group(4))
            out += ["%s%d" % (prefix, i) for i in range(a, b + 1)]
        else:
            out.append(part)
    return out


def export_bom(cli, sch, project_dir, out_dir, base):
    available = schematic_fields(sch)
    mpn_fields = _alias_fields(MPN_FIELDS, available)
    mfr_fields = _alias_fields(MFR_FIELDS, available)
    fields = ["Reference", "Value", "Footprint", "${QUANTITY}"]
    labels = ["Designator", "Value", "Footprint", "Qty"]
    aliases = mfr_fields + mpn_fields
    fields.extend(aliases)
    labels.extend("Field%d" % index for index in range(len(aliases)))
    path = os.path.join(out_dir, base + "_BOM.csv")
    raw = os.path.join(out_dir, ".bom_raw.csv")
    try:
        # Normalize aliases per component before grouping. This prevents one
        # alias masking another and different manufacturers being merged.
        _run(cli, ["sch", "export", "bom", "-o", raw,
                   "--fields", ",".join(fields), "--labels", ",".join(labels),
                   "--group-by", "", "--ref-range-delimiter", "",
                   "--ref-delimiter", ",", "--exclude-dnp", sch])
        grouped = {}
        with open(raw, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                values = [(row.get("Field%d" % index) or "").strip()
                          for index in range(len(aliases))]
                mfr = next((value for value in values[:len(mfr_fields)] if value), "")
                mpn = next((value for value in values[len(mfr_fields):] if value), "")
                key = (row.get("Value", ""), row.get("Footprint", ""), mfr, mpn)
                refs = _expand_refs(row.get("Designator", ""))
                if key not in grouped:
                    grouped[key] = []
                grouped[key].extend(refs)
        rows = []
        for (value, footprint, mfr, mpn), refs in grouped.items():
            refs = list(dict.fromkeys(refs))
            rows.append({"Designator": ",".join(refs), "Value": value,
                         "Footprint": footprint, "Qty": str(len(refs)),
                         "Manufacturer": mfr, "MPN": mpn})
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["Designator", "Value", "Footprint",
                                                   "Qty", "Manufacturer", "MPN"])
            writer.writeheader()
            writer.writerows(rows)
    finally:
        if os.path.exists(raw):
            os.remove(raw)
    return path, rows, bool(mpn_fields)


# --------------------------------------------------------------------------- #
# Pre-flight checks (mirrors pcbapartner.com/tools/bom-checker/)
# --------------------------------------------------------------------------- #
def preflight(bom_rows, cpl_rows, mpn_field, board_text):
    issues = []
    if "Edge.Cuts" not in board_text or not re.search(r'\(layer "Edge\.Cuts"\)', board_text):
        issues.append(("ERROR", "No board outline found on Edge.Cuts."))
    if not cpl_rows:
        issues.append(("ERROR", "Placement file is empty - no footprints to assemble."))
    if bom_rows is None:
        issues.append(("WARN", "No schematic found next to the board - BOM not generated. "
                               "Supply your own BOM to the assembler."))
        return issues
    if not mpn_field:
        issues.append(("WARN", "No MPN field found in the schematic. Add an 'MPN' field so parts "
                               "can be sourced exactly."))
    bom_refs = set()
    for r in bom_rows:
        refs = _expand_refs(r.get("Designator", ""))
        bom_refs.update(refs)
        if mpn_field and not (r.get("MPN") or "").strip():
            issues.append(("WARN", "Missing MPN: %s (%s, %s)" % (
                r.get("Designator", ""), r.get("Value", ""), r.get("Footprint", ""))))
        if not (r.get("Footprint") or "").strip():
            issues.append(("WARN", "Missing footprint: %s" % r.get("Designator", "")))
    cpl_refs = {r["Designator"] for r in cpl_rows}
    only_cpl = sorted(r for r in cpl_refs - bom_refs if r)
    only_bom = sorted(r for r in bom_refs - cpl_refs if r)
    if only_cpl:
        issues.append(("WARN", "On the board but not in the BOM: %s" % ", ".join(only_cpl[:40])))
    if only_bom:
        issues.append(("INFO", "In the BOM but not placed (through-hole/virtual/hand-soldered?): %s"
                       % ", ".join(only_bom[:40])))
    return issues


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _run_export(board, out_dir=None):
    board = os.path.abspath(board)
    if not board.endswith(".kicad_pcb") or not os.path.isfile(board):
        raise ExportError("Not a KiCad board file: %s" % board)
    cli = find_kicad_cli()
    project_dir = os.path.dirname(board)
    name = os.path.splitext(os.path.basename(board))[0]
    out_dir = os.path.abspath(out_dir or os.path.join(project_dir, "pcbapartner"))
    os.makedirs(out_dir, exist_ok=True)
    base = "%s_%s" % (name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    with open(board, encoding="utf-8", errors="replace") as fh:
        board_text = fh.read()

    zpath, gerber_files, n_copper = export_gerbers_zip(cli, board, board_text, out_dir, base)
    cpl_path, cpl_rows = export_cpl(cli, board, out_dir, base)

    sch = os.path.join(project_dir, name + ".kicad_sch")
    bom_path, bom_rows, mpn = (None, None, None)
    if os.path.isfile(sch):
        bom_path, bom_rows, mpn = export_bom(cli, sch, project_dir, out_dir, base)

    issues = preflight(bom_rows, cpl_rows, mpn, board_text)
    report_path = os.path.join(out_dir, base + "_preflight.txt")
    buf = io.StringIO()
    buf.write("PCBA Partner Fabrication Toolkit v%s\n" % VERSION)
    buf.write("Board: %s\nCopper layers: %d\nGerber/drill files: %d\n" % (
        os.path.basename(board), n_copper, len(gerber_files)))
    buf.write("Placed parts (CPL): %d\nBOM lines: %s\n\n" % (
        len(cpl_rows), len(bom_rows) if bom_rows is not None else "n/a"))
    if issues:
        for level, msg in issues:
            buf.write("[%s] %s\n" % (level, msg))
    else:
        buf.write("No issues found.\n")
    buf.write("\nExports use the saved board and schematic, with KiCad's absolute board origin.\n")
    buf.write("CPL includes both SMD and through-hole footprints unless excluded in KiCad.\n")
    buf.write("This is a basic data check, not a DRC or a fabrication approval.\n")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(buf.getvalue())

    return {
        "out_dir": out_dir,
        "zip": zpath,
        "cpl": cpl_path,
        "bom": bom_path,
        "report": report_path,
        "report_text": buf.getvalue(),
        "issues": issues,
        "copper_layers": n_copper,
        "parts": len(cpl_rows),
    }


def run_export(board, out_dir=None):
    """Stage an export so failed CLI commands do not leave a partial package."""
    board = os.path.abspath(board)
    target = os.path.abspath(out_dir or os.path.join(os.path.dirname(board), "pcbapartner"))
    try:
        if not board.endswith(".kicad_pcb") or not os.path.isfile(board):
            raise ExportError("Not a KiCad board file: %s" % board)
        os.makedirs(target, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".pcbapartner_", dir=target) as staging:
            res = _run_export(board, staging)
            for key in ("zip", "cpl", "bom", "report"):
                if res[key]:
                    final_path = os.path.join(target, os.path.basename(res[key]))
                    os.replace(res[key], final_path)
                    res[key] = final_path
            res["out_dir"] = target
            return res
    except OSError as exc:
        raise ExportError("Could not read the project or write the export: %s" % exc) from exc


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export a PCBA Partner assembly package from KiCad.")
    ap.add_argument("board", help="path to .kicad_pcb")
    ap.add_argument("-o", "--output", help="output directory (default: <project>/pcbapartner)")
    a = ap.parse_args(argv)
    try:
        res = run_export(a.board, a.output)
    except ExportError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print(res["report_text"])
    print("Output folder: %s" % res["out_dir"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
