---
name: bios-update
description: Update (flash) motherboard BIOS through an IP-KVM: download, verify checksum, stage, flash with Q-Flash/M-Flash/EZ Flash, restore settings.
---

# BIOS update

Flashes newer firmware with the board's own setup-time utility, then restores the settings the flash reset.

## Inputs

- Machine name. Target version (default: latest stable from the bios-profile record).

## Steps

1. Preconditions, all required:
   - A baseline (`baseline-*/settings.md`) newer than the last applied plan. If not, run bios-profile first.
   - Backups of the machine's data are healthy (ask, or check the user's backup tool). A flash should not
     touch disks, but a failed one leaves the box down until someone is on site.
   - Recovery route written down: backup BIOS chip, USB flashback, or "needs a person on site".
   - kvm-console `check` passes, and the KVM is not powered from a port the flash can cut.
2. Download from the vendor page for the exact model and revision. Check the file's checksum against the
   one the vendor publishes (Gigabyte prints it on the page, e.g. `checksum C6AF`). Read the release notes
   for steps that must come first (ME firmware, intermediate versions).
3. Stage the file where the flash tool can read it: the EFI system partition (FAT32, usually `/boot/efi/`)
   or a FAT32 virtual USB from the KVM. `sync` after copying.
4. Tell the user: downtime estimate (10-20 min), what goes down, and that power must not be cut. Get a yes.
5. Reboot into the flash utility: the vendor's POST key or the setup menu entry
   (`reference/vendor-firmware.md`). Pick the staged file; screenshot the version and confirmation screens;
   start the flash. Screenshot progress every 30-60 s. Send no keys while it runs.
6. After the automatic reboot, enter setup. Restore settings from the baseline with bios-apply: build a
   plan whose rows are every baseline value that now differs, mark it `approved` (the user approved the
   baseline values earlier), apply it.
7. Verify: `firmware-facts.sh` shows the new `bios_version`; boot entries in `efibootmgr` still point at the
   OS loader; Secure Boot state matches the baseline. Remove the staged file from the ESP.
8. Record: `log.md` line, update `machines.json` board firmware, and the user's own records if they keep any.

## Data storage

Session screenshots and the restore plan under `<overlay>/machines/<name>/` (`scripts/overlay-paths.sh dir`).
The downloaded firmware file is not kept after the flash.

## Notes

- Highest-risk action in this plugin. Never run it unattended, never on battery or a flaky supply, never with
  a beta file unless the user named it.
- Secure Boot keys (db/dbx, MOK) can be reset by a flash: check pending MOK enrolment (`mokutil --list-new`)
  and module signing after.
- Boards on LVFS (`fwupdmgr get-updates` lists the system firmware) can update from Linux instead; prefer
  that route when it exists.
