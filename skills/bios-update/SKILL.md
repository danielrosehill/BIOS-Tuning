---
name: bios-update
description: Update (flash) motherboard BIOS through an IP-KVM: download, verify checksum, stage, flash with Q-Flash/M-Flash/EZ Flash, restore settings.
---

# BIOS update

Flashes newer firmware with the board's own setup-time utility, then restores the settings the flash reset.
First done end to end on 2026-11-17 (Gigabyte B760M DS3H DDR4, F23 -> F25, PicoKVM); the notes below come from it.

## Inputs

- Machine name. Target version (default: latest stable from the bios-profile record).

## Steps

1. **Pre-flight checks**, all before any reboot, all required:
   - Backups healthy: the machine's backup jobs last ran with success (ask, or read the user's backup tool).
   - Recovery route written down: backup BIOS chip, USB flashback button, or "needs a person on site". If it
     needs a person, ask the user whether someone can be there if the flash fails, and say it plainly.
   - Fallback boot loader on the EFI partition (`\EFI\BOOT\BOOTX64.EFI`): a flash can wipe NVRAM boot entries,
     and the fallback is what boots the OS then.
   - Pending Secure Boot key enrolment: `ls /sys/firmware/efi/efivars | grep -c MokNew`, `mokutil --list-new`.
     A flash or reboot can consume or drop it; note its state before and after.
   - kvm-console `check` passes. On KVMs powered by the host's USB port, ErP must be Disabled so standby power
     keeps the KVM up through the flash's shutdown (it did on 2026-11-17).
2. **Find the real file.** Read the download link off the vendor's support page (a browser `read_page` on the
   download button gives the href). Do not guess the URL: Gigabyte's names carry a build code
   (`mb_bios_b760m-ds3h-ddr4_8arpt044_f25.zip`); the obvious `..._f25.zip` 404s. Note the page's checksum and
   release notes (ME/CSME updates, "update to X first", no-downgrade warnings). Check size with a HEAD request.
3. **Ask the user** with filename, source, size, checksum, downtime (20-25 min incl. a settings pass), what goes
   down, and the recovery route. One yes covers download, flash and the settings restore.
4. **Download and verify** (in its own empty directory):
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/bios-checksum.py <file.zip> --expect <page checksum>` must print MATCH.
   For Gigabyte the page checksum is the 16-bit byte sum of the image; Q-Flash shows the same value before writing.
5. **Stage where the flash tool can see it.** Prefer KVM virtual media: the OS disk may be invisible to the flash
   tool (NVMe behind Intel VMD/RST was, on 2026-11-17; Q-Flash listed only the KVM drive).
   - Build: `bash ${CLAUDE_PLUGIN_ROOT}/scripts/make-flash-image.sh <image-file> f25.img`
   - Gadget KVMs over SSH: copy the image to the KVM, then point the mass-storage LUN at it read-only
     (`/sys/kernel/config/usb_gadget/<g>/functions/mass_storage.*/lun.0/{ro,file}`). Other KVMs: the web UI's
     virtual media upload.
   - **Attach before the reboot.** UEFI enumerates USB at power-on; media swapped in while setup is open is not
     seen (the drive stays listed but empty). If that happens: Exit Without Saving, catch setup again.
   - The EFI system partition is the fallback when the flash tool can see the disk.
6. **Baseline in the same session**: kvm-console `enter-setup`, screenshot every role-relevant page (bios-profile
   step 4) into `baseline-<date>/` with `settings.md` marking each value to RESTORE. Linux readouts taken before
   the reboot (Secure Boot, VT-x, IOMMU, memory speed) cover pages that are slow to reach.
7. **Flash.** Open the flash tool (Gigabyte: F8 or the Q-Flash button in setup), Update BIOS, pick the file.
   Read the "Update BIOS" panel: model, version, date and checksum must match step 2 before "Start". Gigabyte
   then warns the system will shut down and continue after restart: OK. Video drops ("no signal") while it
   power-cycles; send no keys. Screenshot progress every 30-60 s.
8. **Settings pass, always.** The board may boot straight into the OS on defaults. Linux checks pass even when
   a setting with no Linux readout was reset: on 2026-11-17 F25 came back with AC BACK = **Always Off** and PTT
   = Enabled, while VT-d, VMD, Secure Boot, CSM and the fan preset survived. Reboot into setup, compare every
   RESTORE line with the baseline, fix differences, F10: the save dialog's "Last Modified" list must equal the
   changes you made.
9. **Verify and clean up**: `firmware-facts.sh` shows the new `bios_version`; boot entries intact; Secure Boot
   as baseline; `grub-editenv list` clean; `systemctl --failed` unchanged. Detach and delete the virtual media
   image, delete staged files on the ESP and the download directory.
10. **Record**: `log.md`, `machines.json` board firmware, the flash screenshots, and the user's own records.

## Data storage

Session screenshots, baseline and restore plan under `<overlay>/machines/<name>/` (`scripts/overlay-paths.sh dir`).
The firmware file and disk image are deleted after the flash.

## Notes

- Highest-risk action in this plugin. Never unattended, never on battery or a flaky supply, never a beta unless
  the user named it.
- Boards on LVFS (`fwupdmgr get-updates` lists the system firmware) can update from Linux; prefer that route then.
- See kvm-console for input pacing: setup UIs drop keys sent faster than ~0.3 s apart.
