# Gigabyte F23 -> F25 through a PicoKVM (2026-11-17)

A real session driven by an agent with this plugin: Gigabyte B760M DS3H DDR4, Intel 12th gen, NVMe behind
Intel VMD, Luckfox PicoKVM (keys over SSH HID gadget, screen in the browser). Screens are the KVM web UI.

| # | Screen | What it shows |
| --- | --- | --- |
| 01 | Settings > Platform Power | AC BACK = Always On, ErP Disabled: the power-cut setting before the flash |
| 02 | IO Ports > VMD setup menu | VMD controller Enabled: why Q-Flash could not see the NVMe EFI partition |
| 03 | Boot | Boot order, CSM Disabled (orange star = changed from default), Fast Boot |
| 04 | Q-Flash > File | The only drive Q-Flash lists is the KVM virtual USB; the FAT32 image with the BIOS file shows up once attached before power-on |
| 05 | Q-Flash > Run | "Update BIOS" panel: model, F25, date, checksum C6AF. Compare with the vendor page before Start |
| 06 | Q-Flash progress | Updating BIOS Now; send no keys |
| 07 | KVM UI | "HDMI signal not detected" while the board power-cycles after the flash: expected |
| 08 | Platform Power after F25 | AC BACK reset to **Always Off**: why the settings pass after a flash is not optional |
| 09 | Save & Exit dialog | "Last Modified" lists exactly the restored changes (AC BACK, PTT) |

Steps and lessons: `skills/bios-update/SKILL.md`, `skills/kvm-console/SKILL.md`, `reference/vendor-firmware.md`.
