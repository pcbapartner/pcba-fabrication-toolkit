# Release and official-submission procedure for 0.1.1

Version 0.1.1 is a testing release for macOS / KiCad 10.0 using the SWIG runtime. Repository: https://github.com/pcbapartner/pcba-fabrication-toolkit. These instructions and source were AI-assisted. They do not claim a release URL is already downloadable, an independent human review is complete, or KiCad has accepted the plugin. Actual availability and public-download evidence are recorded by the GitHub release operation.

## Release artifacts and source

- pcbapartner-fabrication-toolkit-0.1.1.zip and its .sha256: six-member installation package, full GPL license and icons.
- pcba-fabrication-toolkit-0.1.1-source.zip and its .sha256: audited 15-file source tree, tests and read-only CI workflow; no fixtures, work files or credentials.
- pcm-submission/packages/com.pcbapartner.fabrication-toolkit/metadata.json and icon.png: official-submission material, kept separate from installed metadata. Actual source/package GPL-3.0-or-later is preserved; the legacy outer v1 label maps to GPL-3.0 and must remain disclosed.
- VALIDATION.md records exact 0.1.1 offline PCM/menu/toolbar proof, local 9/9 tests, real 0.1.1 three-OS standard-library CI with native skips, and local schemas. This does not establish official network CI or online-index installation.

The build script creates the installation ZIP, checksum and submission folder. The source archive uses the source-file allowlist. Source ZIP hashes are recorded outside the archive to avoid a circular checksum. Both metadata and the core VERSION constant must remain 0.1.1 for these asset names.

## GitHub testing-release steps

1. Review the exact source changes, metadata, docs and licenses at the intended commit. Keep tests/workflow and the explicit macos declaration consistent with the verified scope. AI assistance must not be mislabeled as a person's independent review.
2. Retain the exact-package GUI record for installation ZIP SHA d3532161b5ad8bd442e2c163ff8a0b2d8bda310fdba2680a3b376e2d4afa8da0. It passed formal-identifier upgrade plus menu and toolbar on the saved Sheetfile-regression fixture. Any change to installed members requires new byte/hash checks and an appropriate retest.
3. Verify the intended source commit's CI and final four asset hashes. Each hosted job's absent-native skip stays a skip, not a native pass. Inspect source and installation archives for the declared version, correct layout and absence of customer data.
4. Check public v0.1.1/tag/asset-name availability immediately before creation. Once authorized, create a new pre-release at the intended source commit and upload the four exact assets. Do not move v0.1.0 or overwrite its frozen assets.
5. Download the actual public assets anonymously; verify bytes/SHA/size, source members, tag commit and installed/submission metadata. Record the observed URLs and results. A prepared URL or a successful upload is not anonymous download proof.

Expected installation path: https://github.com/pcbapartner/pcba-fabrication-toolkit/releases/download/v0.1.1/pcbapartner-fabrication-toolkit-0.1.1.zip
Expected source path: https://github.com/pcbapartner/pcba-fabrication-toolkit/releases/download/v0.1.1/pcba-fabrication-toolkit-0.1.1-source.zip

## Official KiCad submission is a separate decision

Do not open an official MR before the session's hold is lifted. KiCad's addons schema allows a company/team author; maintainer is optional when the same as author. The checked rules did not require separately hiring a person with a particular professional title or certification. The real responsibility condition still matters: a company person must actually review, understand and take responsibility, answer review questions and personally write official commit/MR/comment text. Non-English original wording may be translated. Do not label generated prose as human-written.

Follow the applicable [tool-generated-content policy](https://dev-docs.kicad.org/en/rules-guidelines/tool-generated-content/), including meaningful tool/testing disclosure and human review/approval before agent activity in KiCad spaces. The checked policy is not a blanket ban on all independent plugin AI code, and no independent-plugin exemption is assumed. If policy scope for metadata-only text remains unclear, resolve it with upstream without pretending approval has been obtained.

Recheck the [addons guide](https://dev-docs.kicad.org/en/addons/) and [metadata repository](https://gitlab.com/kicad/addons/metadata) at submission time. Only packages/com.pcbapartner.fabrication-toolkit/metadata.json and icon.png belong in that contribution. Run actual fork validate/build, test the resulting temporary PCM repository and obtain upstream review. Local schemas, company CI and offline installation do not substitute for those recommended steps. Never send customer designs or fixtures as metadata-submission contents.

The current exporter formats data locally without a commercial-service connection. If a future version adds such a connection, follow KiCad's then-current commercial-services process. Branding alone is not treated as proof that a supplier contract is required.
