# BIOS-Tuning (plugin `bios-tuning`)

Public, generic plugin. Follows the Public Plugin, Private Overlay standard
(github.com/danielrosehill/Public-Plugin-Private-Overlay): no hosts, IPs, names or secrets in this repo;
the user's machines live in the overlay (`scripts/overlay-paths.sh`).

- Release tier: **small** (`v1.0`, `v1.1`, ...). `plugin.json` version is 1.x.y for Claude Code; tags use the tier.
- Scripts stay stdlib Python / plain bash so they run on any host.
- `reference/kvm-backends.md`: mark each claim tested (with date) or "as documented". PicoKVM rows tested
  2026-11-17 (SSH HID gadget works; on-device v4l2 frame grab does not).
- Created 2026-11-17. First real flash the same day (Gigabyte F23 -> F25); its lessons are in bios-update and kvm-console, screens in docs/screenshots/
