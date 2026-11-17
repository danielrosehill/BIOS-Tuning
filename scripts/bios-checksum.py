#!/usr/bin/env python3
"""Check a BIOS image against the checksum the vendor prints on its download page.

Gigabyte lists a 4-hex-digit "Checksum" per BIOS (e.g. C6AF). It is the 16-bit sum of every byte
of the image file inside the zip (verified 2026-11-17: B760MDS3HDDR4.F25 -> C6AF, matching the page
and the Q-Flash screen). Other vendors publish SHA-256 or MD5; pass --sha256 / --md5 for those.

  bios-checksum.py image.F25 --expect C6AF
  bios-checksum.py bios.zip --expect C6AF          # checks every member over 1 MB
  bios-checksum.py image.bin --sha256 <hex>

Exit 0 on match, 1 on mismatch. Stdlib only. Read-only.
"""
import argparse
import hashlib
import sys
import zipfile


def sum16(data):
    return "%04X" % (sum(data) & 0xFFFF)


def blobs(path):
    if zipfile.is_zipfile(path):
        z = zipfile.ZipFile(path)
        bad = z.testzip()
        if bad:
            sys.exit(f"zip CRC error in {bad}")
        for i in z.infolist():
            if i.file_size > 1_000_000:
                yield i.filename, z.read(i)
    else:
        with open(path, "rb") as f:
            yield path, f.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--expect", help="vendor 16-bit checksum, hex (Gigabyte style)")
    ap.add_argument("--sha256")
    ap.add_argument("--md5")
    a = ap.parse_args()
    ok = True
    for name, data in blobs(a.path):
        s16, sha, md5 = sum16(data), hashlib.sha256(data).hexdigest(), hashlib.md5(data).hexdigest()
        print(f"{name}\tsize={len(data)}\tsum16={s16}\tsha256={sha}")
        if a.expect and s16 != a.expect.upper():
            ok = False
        if a.sha256 and sha != a.sha256.lower():
            ok = False
        if a.md5 and md5 != a.md5.lower():
            ok = False
    print("MATCH" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
