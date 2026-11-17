# BIOS Tuning

Agent skills for changing motherboard BIOS/UEFI settings and flashing firmware **remotely, through an IP-KVM**,
with a record of what was there before and proof of what changed.

The agent sees the firmware screen through the KVM's web UI (a browser it drives) and types through the KVM
(over SSH to the USB HID gadget, the PiKVM API, or the browser). Linux-side checks confirm each change after boot.

## Skills

| Skill | What it does |
| --- | --- |
| `bios-profile` | Board, BIOS version, latest available firmware, Secure Boot, virtualisation, memory and WoL from Linux; a screenshot baseline of every non-default setting via the KVM |
| `bios-recommend` | A change plan from a role profile (always-on server, workstation, low-power box) or your own requests, with why, risk and how to verify each row |
| `kvm-console` | Check the KVM, reboot into setup, read the screen, send keys, save or discard |
| `bios-apply` | Applies an approved plan with before/after screenshots, checks the save dialog, verifies from Linux after boot |
| `bios-update` | Downloads and checksums firmware, stages it on the ESP or KVM virtual media, flashes with the board's tool, restores settings |

Reference: `reference/kvm-backends.md` (eyes and hands per KVM model), `reference/vendor-firmware.md`
(setup keys, flash tools and setting names for Gigabyte, MSI, ASUS, ASRock and others; Linux readouts),
`reference/machines-schema.md`.

Scripts (stdlib/bash only): `scripts/hid-keys.py` (keystrokes via SSH HID gadget or kvmd API),
`scripts/firmware-facts.sh` (read-only firmware facts as JSON), `scripts/bios-checksum.py` (vendor checksum,
incl. Gigabyte's 16-bit sum), `scripts/make-flash-image.sh` (FAT32 virtual-USB image for the flash tool),
`scripts/overlay-paths.sh`.

Walkthrough with real screens: `docs/screenshots/gigabyte-f23-to-f25/` (a full F23 -> F25 flash through a PicoKVM).

## Your machines: the overlay

Nothing about your machines lives in this repo. `scripts/overlay-paths.sh dir` names your data folder
(`$BIOS_TUNING_HOME`, else `$CLAUDE_USER_DATA/bios-tuning`, else `~/.claude-user-data/bios-tuning`).
It holds `machines.json`, per-machine facts, baselines, plans and logs. Put your own role profiles in
`<overlay>/roles/<name>.md` to override the built-in ones.

## Safety

Every reboot, setting change and flash waits for your yes. Plans record the recovery route before anything
is changed. A flash needs a fresh baseline and a checked vendor checksum.

## Install

```bash
claude plugins install bios-tuning@danielrosehill
```

## License

MIT
