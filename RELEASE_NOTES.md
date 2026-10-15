# 0.1.1 testing release

- Correct child-sheet discovery: only direct `Sheetfile` properties of actual `sheet` nodes are followed; escaped sheet filenames are decoded. An ordinary symbol custom field no longer causes a missing-child export failure.
- Refuse existing output names, preserve prior exports and recover this attempt's published files if a final move fails. Report any rollback failure with filenames requiring manual cleanup.
- Map only the generated official legacy outer license label to GPL-3.0. Actual source/installed metadata and full license remain GPL-3.0-or-later; schema compatibility does not imply upstream policy approval.
- Explicitly declare macOS / KiCad 10.0 native compatibility. The exact 0.1.1 ZIP passed offline PCM upgrade, menu and toolbar export on macOS KiCad 10.0.6, including the ordinary-Sheetfile regression fixture.
- Add read-only regression CI on Ubuntu, Windows and macOS. Version-0.1.1 run 38708668214 passed 8 tests and explicitly skipped the unavailable native CLI test in each job. Local macOS ran all 9 successfully. Three-OS CI is not three-OS native/GUI coverage.

The exporter remains local and vendor-neutral without uploads or commercial-service connections. These changes were AI-assisted; no independent human-review, official KiCad acceptance, complete DRC or fabrication approval is claimed. The frozen v0.1.0 tag/assets remain preserved. See VALIDATION.md for exact evidence and PUBLISHING.md for publication checks.
