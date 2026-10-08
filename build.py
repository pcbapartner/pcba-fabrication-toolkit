"""Build the KiCad PCM package and the submission metadata.

    python3 build.py

Produces:
  dist/pcbapartner-fabrication-toolkit-<ver>.zip   (upload as a GitHub release asset)
  pcm-submission/packages/com.pcbapartner.fabrication-toolkit/metadata.json
  (copy that folder into a fork of gitlab.com/kicad/addons/metadata and open a merge request)
"""

import hashlib
import json
import os
import shutil
import struct
import zipfile
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_RELEASE_URL = "https://github.com/pcbapartner/pcba-fabrication-toolkit/releases/download/v{v}/{f}"


def png(path, size=48):
    """Draw a simple 'board' icon without external libraries."""
    green, gold, white = (0x0E, 0x6B, 0x3A), (0xE0, 0xB0, 0x30), (0xFF, 0xFF, 0xFF)
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            px = (0, 0, 0, 0)
            if 3 <= x < size - 3 and 3 <= y < size - 3:
                px = green + (255,)
                if (x - 12) ** 2 + (y - 12) ** 2 < 20 or (x - 35) ** 2 + (y - 35) ** 2 < 20:
                    px = gold + (255,)
                if 18 <= x <= 30 and 18 <= y <= 30:
                    px = white + (255,)
                if y in (12, 35) and 12 <= x <= 35:
                    px = gold + (255,)
            row += bytes(px)
        rows.append(bytes(row))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


def main():
    meta = json.load(open(os.path.join(ROOT, "metadata.json")))
    ver = meta["versions"][0]["version"]
    os.makedirs(os.path.join(ROOT, "resources"), exist_ok=True)
    png(os.path.join(ROOT, "resources", "icon.png"), 64)
    png(os.path.join(ROOT, "plugins", "icon.png"), 24)
    shutil.copyfile(os.path.join(ROOT, "LICENSE"), os.path.join(ROOT, "plugins", "LICENSE"))

    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    fname = "pcbapartner-fabrication-toolkit-%s.zip" % ver
    zpath = os.path.join(ROOT, "dist", fname)
    install_size = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in ["metadata.json", "resources/icon.png", "plugins/__init__.py",
                    "plugins/pcbapartner_export.py", "plugins/icon.png", "plugins/LICENSE"]:
            full = os.path.join(ROOT, rel)
            with open(full, "rb") as fh:
                data = fh.read()
            info = zipfile.ZipInfo(rel, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
            install_size += len(data)

    sha = hashlib.sha256(open(zpath, "rb").read()).hexdigest()
    sub = dict(meta)
    sub["versions"] = [dict(meta["versions"][0],
                            download_url=REPO_RELEASE_URL.format(v=ver, f=fname),
                            download_sha256=sha,
                            download_size=os.path.getsize(zpath),
                            install_size=install_size)]
    sub_dir = os.path.join(ROOT, "pcm-submission", "packages", meta["identifier"])
    os.makedirs(sub_dir, exist_ok=True)
    json.dump(sub, open(os.path.join(sub_dir, "metadata.json"), "w"), indent=2)
    png(os.path.join(sub_dir, "icon.png"), 64)
    with open(os.path.join(ROOT, "dist", fname + ".sha256"), "w") as fh:
        fh.write("%s  %s\n" % (sha, fname))
    print("package:", zpath)
    print("sha256 :", sha)
    print("submission metadata:", sub_dir)


if __name__ == "__main__":
    main()
