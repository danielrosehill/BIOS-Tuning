---
name: bios-profile
description: Profile a motherboard, BIOS version, available updates and current BIOS settings, from Linux and via the KVM; set up machines.json.
---

# BIOS profile

Builds the record every later step depends on: what the board is, what firmware it runs, what is newer,
and what every non-default setting is right now.

## Inputs

- Machine name. New machine: ask for its SSH target, its role (`scripts/overlay-paths.sh templates`) and its KVM.
- `--no-kvm`: Linux facts only, no reboot.

## Steps

1. Overlay: `bash ${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh`. Create `machines.json` from
   `reference/machines-schema.md` if missing. Add or update the machine entry.
2. Linux facts (read-only, no reboot):
   `ssh <ssh> 'sudo bash -s' < ${CLAUDE_PLUGIN_ROOT}/scripts/firmware-facts.sh > <overlay>/machines/<name>/facts-<YYYY-MM-DD>.json`.
   Fill `board` in `machines.json` from it.
3. Latest firmware: find the board's support page from the vendor and exact model plus revision (wrong revision
   pages carry incompatible files). Record latest stable version, date, checksum and the release notes'
   headline changes. `fwupdmgr get-updates` covers boards on LVFS; most consumer boards are not on it, so an
   empty fwupd answer is not "up to date".
4. Baseline settings (skip with `--no-kvm`): kvm-console `check`, then `enter-setup`. Walk every page,
   screenshotting each one with a non-default or role-relevant value (role table: the machine's role profile).
   Save to `<overlay>/machines/<name>/baseline-<YYYY-MM-DD>/NN-<page>.png` and transcribe each value into
   `baseline-<date>/settings.md` as `Path > Setting = value`. Then kvm-console `exit-discard`.
5. Report: board, BIOS installed vs latest, Secure Boot, virtualisation, memory configured vs rated speed,
   WoL, and the baseline file. Say which values came from Linux and which were read off the screen.

## Data storage

Writes `machines.json` and `machines/<name>/{facts-*.json,baseline-*/}` in the overlay
(`scripts/overlay-paths.sh dir`). Nothing in the plugin folder.

## Notes

- Step 4 reboots the machine: kvm-console asks first.
- The baseline is the restore point after a BIOS flash (most flashes reset every setting). Do not flash
  without one newer than the last settings change.
