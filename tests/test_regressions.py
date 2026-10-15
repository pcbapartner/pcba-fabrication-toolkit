"""Focused, offline regressions. Standard library only; native KiCad 10 is optional."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("toolkit_core", ROOT / "plugins" / "pcbapartner_export.py")
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)


def staged_export(_board, directory):
    """Exercise actual publication IO without rerunning Gerber generation."""
    result = {"out_dir": directory, "issues": []}
    for key in ("zip", "cpl", "bom", "report"):
        path = Path(directory) / ("attempt_" + key + ".dat")
        path.write_text(key, encoding="utf-8")
        result[key] = str(path)
    return result


class HierarchyRegression(unittest.TestCase):
    def test_symbol_sheetfile_custom_field_is_not_a_child(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root.kicad_sch"
            root.write_text('(kicad_sch (symbol (property "Sheetfile" "not-a-child.kicad_sch") '
                            '(property "MPN" "DEMO")))', encoding="utf-8")
            self.assertIn("MPN", core.schematic_fields(str(root)))

    def test_actual_sheet_context_relative_paths_and_cycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "sub").mkdir()
            root = directory / "root.kicad_sch"
            root.write_text('(kicad_sch (symbol (property "Sheetfile" "not-a-child")) '
                            '(sheet (property "Sheetfile" "sub/child.kicad_sch")))', encoding="utf-8")
            (directory / "sub" / "child.kicad_sch").write_text(
                '(kicad_sch (symbol (property "MPN" "DEMO")) '
                '(sheet (property "Sheetfile" "../root.kicad_sch")))', encoding="utf-8")
            (directory / "unrelated.kicad_sch").write_text('(property "Unrelated" "x")', encoding="utf-8")
            fields = core.schematic_fields(str(root))
            self.assertIn("MPN", fields)
            self.assertNotIn("Unrelated", fields)

    def test_escaped_sheet_filename_is_decoded(self):
        self.assertEqual(list(core._sheet_files(
            '(sheet (property "Sheetfile" "child\\\"quoted.kicad_sch"))')),
            ['child"quoted.kicad_sch'])


class PublicationRegression(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        # Only a file-existence stub for filesystem tests, not a valid PCB design.
        self.board = self.directory / "filesystem-test.kicad_pcb"
        self.board.write_text("(kicad_pcb)", encoding="utf-8")
        self.target = self.directory / "output"
        self.target.mkdir()
        self.prior = self.target / "previous-export.txt"
        self.prior.write_text("previous output must survive", encoding="utf-8")

    def assert_prior_only(self):
        self.assertEqual(sorted(path.name for path in self.target.iterdir()), [self.prior.name])
        self.assertEqual(self.prior.read_text(encoding="utf-8"), "previous output must survive")

    def test_each_final_move_failure_rolls_back_new_files(self):
        original_replace = os.replace
        for failing_move in range(1, 5):
            with self.subTest(failing_move=failing_move):
                calls = [0]

                def fail_selected_move(source, destination):
                    calls[0] += 1
                    if calls[0] == failing_move:
                        raise OSError("simulated final publication failure")
                    return original_replace(source, destination)

                with patch.object(core, "_run_export", staged_export), patch.object(core.os, "replace", fail_selected_move):
                    with self.assertRaises(core.ExportError):
                        core.run_export(str(self.board), str(self.target))
                self.assert_prior_only()

    def test_existing_output_name_is_not_overwritten(self):
        collision = self.target / "attempt_zip.dat"
        collision.write_text("keep existing file", encoding="utf-8")
        with patch.object(core, "_run_export", staged_export):
            with self.assertRaisesRegex(core.ExportError, "already exists"):
                core.run_export(str(self.board), str(self.target))
        self.assertEqual(collision.read_text(encoding="utf-8"), "keep existing file")
        self.assertEqual(len(list(self.target.iterdir())), 2)

    def test_failed_rollback_names_remaining_file(self):
        original_replace, original_remove = os.replace, os.remove
        calls = [0]

        def fail_second_move(source, destination):
            calls[0] += 1
            if calls[0] == 2:
                raise OSError("simulated final publication failure")
            return original_replace(source, destination)

        def fail_new_file_cleanup(path):
            if str(path).endswith("attempt_zip.dat"):
                raise OSError("simulated rollback failure")
            return original_remove(path)

        with patch.object(core, "_run_export", staged_export), \
                patch.object(core.os, "replace", fail_second_move), \
                patch.object(core.os, "remove", fail_new_file_cleanup):
            with self.assertRaisesRegex(core.ExportError, "manual cleanup: attempt_zip.dat"):
                core.run_export(str(self.board), str(self.target))
        self.assertTrue((self.target / "attempt_zip.dat").is_file())
        self.assertEqual(self.prior.read_text(encoding="utf-8"), "previous output must survive")

    def test_success_publishes_all_four_outputs(self):
        with patch.object(core, "_run_export", staged_export):
            result = core.run_export(str(self.board), str(self.target))
        for key in ("zip", "cpl", "bom", "report"):
            self.assertEqual(Path(result[key]).parent, self.target)
            self.assertEqual(Path(result[key]).read_text(encoding="utf-8"), key)
        self.assertEqual(len(list(self.target.iterdir())), 5)


class BuildLabelRegression(unittest.TestCase):
    def test_legacy_submission_label_does_not_change_actual_package_license(self):
        # This is not the upstream schema validator. Its current v1/v2 validation
        # is recorded separately; no schema download or jsonschema dependency here.
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for relative in ("build.py", "metadata.json", "LICENSE", "plugins/__init__.py", "plugins/pcbapartner_export.py"):
                target = directory / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            subprocess.run([sys.executable, str(directory / "build.py")], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
            submission = json.loads((directory / "pcm-submission" / "packages" / metadata["identifier"] / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["license"], "GPL-3.0-or-later")
            self.assertEqual(submission["license"], "GPL-3.0")
            archives = list((directory / "dist").glob("*.zip"))
            self.assertEqual(len(archives), 1)
            with zipfile.ZipFile(archives[0]) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(json.loads(archive.read("metadata.json"))["license"], "GPL-3.0-or-later")
                self.assertEqual(archive.read("plugins/LICENSE"), (directory / "LICENSE").read_bytes())


class OptionalNativeKiCadRegression(unittest.TestCase):
    def test_native_bom_accepts_ordinary_sheetfile_property(self):
        cli = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
        mac_cli = Path("/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        if not cli and mac_cli.is_file():
            cli = str(mac_cli)
        if not cli:
            self.skipTest("KiCad CLI is unavailable; optional native validation was not run")
        try:
            version = subprocess.run([cli, "--version"], check=True, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            self.skipTest("KiCad CLI version could not be read")
        if not re.match(r"^10\.0(?:\.|$)", version):
            self.skipTest("Optional native regression requires the declared KiCad 10.0 series")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            root_id, symbol_id = str(uuid.uuid4()), str(uuid.uuid4())
            schematic = f'''(kicad_sch (version 20250114) (generator "eeschema") (uuid "{root_id}") (paper "A4")
(lib_symbols (symbol "Audit:Part" (pin_names (offset 0)) (in_bom yes) (on_board yes)
        (property "Reference" "R" (at 0 2 0) (effects (font (size 1.27 1.27))))
        (property "Value" "Part" (at 0 -2 0) (effects (font (size 1.27 1.27))))
        (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
        (symbol "Part_0_1" (rectangle (start -1 1) (end 1 -1) (stroke (width .1) (type default)) (fill (type none))))
        (symbol "Part_1_1"
            (pin passive line (at -2.54 0 0) (length 1.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
            (pin passive line (at 2.54 0 180) (length 1.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        )))
(symbol (lib_id "Audit:Part") (at 30 30 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{symbol_id}")
(property "Reference" "R1" (at 30 30 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "Value" "Test" (at 30 30 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "Footprint" "Audit:SMD" (at 30 30 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "MPN" "DEMO" (at 30 30 0) (effects (font (size 1.27 1.27)) (hide yes)))
(property "Sheetfile" "not-a-child.kicad_sch" (at 30 30 0) (effects (font (size 1.27 1.27)) (hide yes)))
(instances (project "native-risk" (path "/{root_id}" (reference "R1") (unit 1)))))
(sheet_instances (path "/" (page "1"))) (embedded_fonts no))'''
            path = directory / "native-risk.kicad_sch"
            path.write_text(schematic, encoding="utf-8")
            _, rows, has_mpn = core.export_bom(cli, str(path), str(directory), str(directory), "native-risk")
            self.assertTrue(has_mpn)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["Designator"], "R1")
            self.assertEqual(rows[0]["MPN"], "DEMO")


if __name__ == "__main__":
    unittest.main()
