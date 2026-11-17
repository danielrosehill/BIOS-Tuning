---
name: kvm-console
description: Drive a machine's BIOS/UEFI setup through an IP-KVM: check the KVM, reboot into setup, read the screen, send keys, save and exit.
---

# KVM console

The hands-and-eyes layer the other skills use. Read `${CLAUDE_PLUGIN_ROOT}/reference/kvm-backends.md`
for how to see and type on the user's KVM model.

## Inputs

- Machine name (an entry in the overlay's `machines.json`; see `reference/machines-schema.md`).
- What to do: `check`, `enter-setup`, `navigate`, `save-exit`, `exit-discard`.

## Steps

**check** (run before every session)
1. Load the machine's `kvm` entry: `bash ${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh dir`, then `machines.json`.
2. Ping the KVM. For `ssh-hidg`: `ssh <kvm.ssh> 'cat /sys/class/udc/*/state'` must print `configured`.
   For `pikvm`: `GET /api/hid` reports `online`.
3. Open the KVM web UI in the browser and take a screenshot. It must show the host's screen, not "No signal".
4. If the agent's own tools live on the target machine (its `depends_on_it` list), confirm this plugin and
   the browser tooling run locally first; they are about to lose their backend.

**enter-setup**
1. Tell the user what goes down (`depends_on_it`) and get a yes for the reboot.
2. Reboot from the OS (`ssh <machine.ssh> 'sudo systemctl reboot'`). Do not use hard reset unless the OS is hung.
3. Wait until the target stops answering ping (an OS shutdown with many containers can take minutes), then
   tap the setup key and keep going through POST. Extra taps once setup is open are harmless:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/hid-keys.py --machine <name> --repeat 40 --delay 0.15 Del`
   (key per vendor: `reference/vendor-firmware.md`).
4. Screenshot. If the OS boot screen appears instead, wait for the OS, reboot and try again with a longer
   repeat. After two misses, check fast boot is off (it shortens the key window) and stop to ask.
5. If the board opens in EZ mode, switch to Advanced (F2 Gigabyte, F7 MSI/ASUS).

**navigate**
- If no highlight is visible after an arrow key (graphical setups such as Gigabyte's often hide it until
  the mouse moves), click the item in the KVM video with the browser: KVMs with an absolute mouse pass the
  click through. Then use keys again; the highlight follows the click.
- One key, then one screenshot. Arrow keys move the highlight; read where it is before Enter.
- Read every value on the screen before changing anything. Crop or zoom the screenshot when the text is small.
- When you find a setting's real path, write it into the machine's `settings_map` in `machines.json`.
- Never press F10/Enter or any "Load defaults" key unless the step you are executing says so.

**save-exit / exit-discard**
- Save: F10 (Supermicro F4), screenshot the confirmation dialog, which on most boards lists every pending change.
  Check the list matches the plan exactly, then Enter. If anything unexpected is listed, Esc and stop.
- Discard: Esc to the exit page, choose "Exit without saving" / "Discard changes and exit", confirm on screen.
- After the reboot, wait for SSH on the target and run its Linux checks (bios-apply step 6).
- Then check the boot was recorded as good. GRUB machines: `grub-editenv /boot/grub/grubenv list` must not
  show `recordfail=1`, and `systemctl --failed` should show nothing new compared with the previous boot
  (`journalctl -b -1 -u <unit>`). A leftover `recordfail` makes the next unattended boot stop at the GRUB menu,
  which defeats power-on-after-power-loss. Clear it by re-running the distro's unit (Ubuntu: `grub2-common`).

## Data storage

Reads `machines.json` in the overlay and writes back newly found `settings_map` paths. Screenshots go to
`<overlay>/machines/<name>/` under the session folder the calling skill set up. Overlay: `scripts/overlay-paths.sh dir`.

## Notes

- Reboots the target and sends keystrokes to it: always behind a user yes.
- Gadget KVMs powered from the host's USB port lose power when the host powers off; a reboot is fine, a
  power-off is not.
- A KVM web UI answering HTTP 200 proves nothing; some answer 200 for every path. Check the video.
