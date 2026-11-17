#!/usr/bin/env bash
# Build a small FAT32 disk image holding a BIOS file, for a KVM to present as a virtual USB stick.
# Use when the board's flash tool cannot see the OS disk (e.g. NVMe behind Intel VMD/RST: Gigabyte
# Q-Flash listed only the KVM drive, 2026-11-17).
#
#   make-flash-image.sh <bios-file> <out.img> [size-MB, default 64]
#
# Uses mtools (mcopy) if installed, else a loop mount (needs sudo). Re-checks the copy's sha256.
set -euo pipefail
src=${1:?bios file}; out=${2:?output image}; mb=${3:-64}
command -v mkfs.vfat >/dev/null || { echo "need mkfs.vfat (dosfstools)" >&2; exit 2; }
truncate -s "${mb}M" "$out"
mkfs.vfat -F 32 -n BIOSFLASH "$out" >/dev/null
name=$(basename "$src")
if command -v mcopy >/dev/null; then
  mcopy -i "$out" "$src" "::$name"
  copy_sha=$(mtype -i "$out" "::$name" | sha256sum | cut -d' ' -f1)
else
  m=$(mktemp -d); sudo mount -o loop,uid="$(id -u)" "$out" "$m"
  cp "$src" "$m/"; sync; copy_sha=$(sha256sum "$m/$name" | cut -d' ' -f1); sudo umount "$m"; rmdir "$m"
fi
src_sha=$(sha256sum "$src" | cut -d' ' -f1)
[[ "$src_sha" == "$copy_sha" ]] || { echo "copy in image differs from source" >&2; exit 1; }
echo "ok $out ($mb MB FAT32) contains $name sha256=$src_sha"
