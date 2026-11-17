---
name: bios-recommend
description: Recommend BIOS settings for a machine's role (server, workstation, low-power) or a user's request; outputs a change plan to apply.
---

# BIOS recommend

Turns the profile plus the machine's job (or a change the user asked for) into a written change plan.

## Inputs

- Machine name, with a profile (run bios-profile first if there is no `facts-*.json`).
- Optional: the user's own requested changes ("make it power on after a power cut"). These go in the plan
  as-is, with any risk noted; suggestions are added only if the user asked for a review.

## Steps

1. Load `machines.json`, the newest `facts-*.json` and `baseline-*/settings.md` for the machine.
2. Load the role profile: `bash ${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh template <role>` (a user
   copy in the overlay `roles/` wins over the built-in one).
3. Compare each role row and each requested change to the current value. Linux facts confirm some values
   (see the readout table in `reference/vendor-firmware.md`); the baseline covers the rest. A value you
   cannot see is `unknown`, not assumed.
4. Write `<overlay>/machines/<name>/plans/<YYYY-MM-DD>-<slug>.md`:

   ```markdown
   # <machine>: <slug>  (status: proposed)
   Board / BIOS: <model> <version>. Baseline: <file>. Goes down during apply: <depends_on_it>.
   | # | Setting (menu path) | Now | Target | Why | Linux check after |
   Recovery if setup becomes unreachable: <CMOS clear / backup BIOS / vendor recovery>.
   ```

   Menu paths: `settings_map` first, then `reference/vendor-firmware.md` as search terms.
5. Show the plan as a short table and ask which rows to keep. Mark the plan `approved` with the kept rows.

## Data storage

Writes `plans/*.md` under `<overlay>/machines/<name>/` (`scripts/overlay-paths.sh dir`).

## Notes

- Read-only on the machine. Nothing changes until bios-apply runs an approved plan.
- Leave Secure Boot, memory overclocks and anything that can stop the OS booting out of a plan unless the
  user asked; when they did, add the recovery route to that row.
