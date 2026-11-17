---
name: bios-apply
description: Apply an approved BIOS change plan through the IP-KVM, with screenshots before and after, save, reboot and verify from Linux.
---

# BIOS apply

Executes an `approved` plan from bios-recommend, one row at a time, and proves each change took.

## Inputs

- Machine name and plan file (`<overlay>/machines/<name>/plans/*.md`, status `approved`).

## Steps

1. Read the plan. Refuse a plan that is not `approved` or whose baseline is older than the last applied plan.
2. kvm-console `check`. Tell the user what goes down and for how long (setup sessions run 5-10 min); get a yes.
3. kvm-console `enter-setup`. Session folder: `<overlay>/machines/<name>/apply-<YYYY-MM-DDTHHMM>/`.
4. For each row:
   a. Navigate to the setting; screenshot `NN-before.png`. If "Now" on screen differs from the plan, stop and ask.
   b. Change it; screenshot `NN-after.png`. Read the new value back off the screenshot.
5. kvm-console `save-exit`. The save dialog's change list must equal the plan rows. Screenshot it.
6. Verify after boot: wait for SSH, then run each row's "Linux check after" and
   `firmware-facts.sh` again (`facts-<date>.json`). Rows with no Linux readout are verified by the
   after-screenshot only: say so. Power-on-after-loss can be proven only by cutting power (smart plug);
   offer it, do not do it unasked.
7. Update the plan to `applied` with a result column (`verified-linux`, `verified-screen`, `failed`),
   append one line to `<overlay>/machines/<name>/log.md`, and save new menu paths to `settings_map`.

## Data storage

Screenshots and the updated plan under `<overlay>/machines/<name>/` (`scripts/overlay-paths.sh dir`).

## Notes

- Changes firmware settings and reboots the machine. Each session needs the user's yes.
- One plan per session. If a change makes the machine fail to boot: enter setup again and revert that row
  from the before-screenshot; if setup is unreachable, use the plan's recovery line and tell the user at once.
