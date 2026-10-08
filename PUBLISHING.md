# Release and KiCad PCM submission

Prepared on 2026-10-07. The current source target is `pcbapartner/pcba-fabrication-toolkit`. Version 0.1.0 was published and anonymously download-verified under `13712831373g-alt/pcba-fabrication-toolkit`; its tag and four release assets are frozen. This working-branch change updates canonical ownership URLs only and does not publish a new version. No official KiCad merge request has been submitted.

## Current release artifacts

- Installation ZIP: `dist/pcbapartner-fabrication-toolkit-0.1.0.zip`
- SHA-256 file: `dist/pcbapartner-fabrication-toolkit-0.1.0.zip.sha256`
- Official-repository folder: `pcm-submission/packages/com.pcbapartner.fabrication-toolkit/`
- Release text: `RELEASE_NOTES.md`
- Source: `plugins/`, `resources/`, `metadata.json`, `build.py`, `LICENSE`

The package identifier uses PCBA Partner's domain namespace. A maintainer who controls that domain and the public source repository should make the submission. If the repository owner/name differs from the planned path, update `metadata.json` → `resources.homepage` and `build.py` → `REPO_RELEASE_URL`, then rebuild and repeat the hash/schema checks before publishing.

## Public source and testing release

**Historical command example below; do not rerun it for v0.1.0.** Updating current-branch URLs must not replace the published ZIPs, move the v0.1.0 tag, or upload a rebuilt 0.1.0 asset. A future package with changed embedded metadata needs its own separately authorized version and validation. No 0.1.1 publication is part of this URL-maintenance change.

For subsequent releases, a maintainer authenticated in GitHub CLI can run these commands from a clone of the public source repository after reviewing `VALIDATION.md`. A new repository is not required.

```bash
gh auth status
python3 build.py
gh release create v0.1.0 dist/pcbapartner-fabrication-toolkit-0.1.0.zip dist/pcbapartner-fabrication-toolkit-0.1.0.zip.sha256 --title "Fabrication Toolkit 0.1.0" --notes-file RELEASE_NOTES.md --prerelease
```

After upload, download the actual public asset and compare its hash with the local release; verify that the source's issues tracker is enabled and the URL works without authentication. Do not submit the PCM merge request while its `download_url` returns 404.

## Official PCM submission

**On hold for a technical human maintainer.** The steps and prepared text below are retained historical, tool-assisted material, not human-authored or human-reviewed contribution prose. Do not use them to open a merge request before a maintainer understands and reviews the contribution and provides their own text as required. The KiCad tool-generated-content policy scope for metadata-only submissions still requires confirmation; no official MR is authorized by this repository URL change.

The [official KiCad addons guide](https://dev-docs.kicad.org/en/addons/index.html) requires public downloads, SHA-256 metadata, GPL-compatible open-source code, English metadata and a source host with issue tracking. New packages should use schema v2; this package does. The [upstream metadata repository](https://gitlab.com/kicad/addons/metadata) accepts the package folder by merge request, rather than a merge request to the generated public repository.

1. Fork `kicad/addons/metadata` under the maintainer's GitLab account.
2. Clone the fork, create a branch, and copy `pcm-submission/packages/com.pcbapartner.fabrication-toolkit/` into its `packages/` directory.
3. Commit and push the folder. Open a merge request targeting `kicad/addons/metadata` → `main`.
4. Use the description below, confirm upstream CI passes, and answer the maintainer's review.

Prepared merge-request title:

> Add PCBA Partner Fabrication Toolkit 0.1.0

Prepared description:

```text
Adds a GPL-3.0-or-later local fabrication exporter for KiCad 10.0 (testing release, legacy SWIG runtime).

The plugin exports multi-layer Gerbers and Excellon drills in a ZIP, a normalized grouped BOM, a both-side mm placement CSV and a basic consistency report. It performs no uploads, network requests or commercial-service connection. Output is vendor-neutral.

Validated using KiCad 10.0.6 on macOS: real PCM installation and a successful PCB Editor menu export, plus two- and four-copper-layer CLI exports, DNP exclusion, bottom-side and through-hole placement, mixed MPN aliases, manufacturer-aware grouping, missing schematic/outline and output failure handling. Metadata validates against KiCad's shipped PCM v2 JSON schema. The archive includes the GPL license and 64 px/24 px icons.

The download_sha256, download_size and install_size in this submission match the uploaded ZIP. See the source repository's VALIDATION.md for the exact GUI validation status and limitations.
```

Verify the public-download claim only after the release asset is available. The real GUI check is complete and recorded in VALIDATION.md. Official inclusion is subject to upstream review; a built package is not an accepted submission.

## If a commercial connection is added later

The [commercial-services policy](https://dev-docs.kicad.org/en/addons/index.html#commercial-services) requires the provider to contact KiCad before submitting a plugin that links to or connects to a commercial service. The FAQ allows an exporter that only formats data without connecting to the provider. This build removed the previous quote-page prompt, browser launch and RFQ report links.

A future commercial version should first send this draft through the contact link shown in that official policy; the exact contact address should be copied from the live page. No such message has been sent.

```text
Subject: Commercial plugin discussion — PCBA Partner KiCad fabrication toolkit

Hello KiCad team,

I represent PCBA Partner and would like to discuss your commercial plugin process before proposing a version of our fabrication toolkit that connects users to our quoting service.

Our current GPL-3.0-or-later plugin exports vendor-neutral fabrication and assembly files locally, without uploads or service connections. A future version may offer an explicit user-initiated link or upload to our quoting service.

Could you advise on the agreement and review process required for that commercial version? We can provide source code, a data-flow description, privacy terms and maintainer contact information.

[Maintainer's real name, role and company email]
[Public source URL, once published]
```
