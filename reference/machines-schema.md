# machines.json (overlay)

Lives in the overlay folder (`scripts/overlay-paths.sh dir`), never in the plugin. One entry per machine
the user tunes. Secrets are references to the user's secret store, never values.

```json
{
  "machines": [
    {
      "name": "server",
      "aliases": ["homeserver"],
      "role": "always-on-server",
      "ssh": "user@server",
      "board": {"vendor": "Gigabyte", "model": "B760M DS3H DDR4", "revision": "1.0",
                "support_url": "https://www.gigabyte.com/...", "backup_bios": false,
                "recovery": "Q-Flash Plus from USB, needs someone on site"},
      "kvm": {
        "model": "Luckfox PicoKVM",
        "url": "http://kvm.lan/",
        "ssh": "root@kvm.lan",
        "keys_backend": "ssh-hidg",
        "eyes": "browser",
        "password_ref": "<secret store reference>",
        "powered_by_host": true
      },
      "settings_map": {
        "power_on_after_power_loss": "Settings > Platform Power > AC BACK"
      },
      "depends_on_it": ["DNS", "home automation", "the agent gateway"],
      "notes": "Free text: anything the next session needs."
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `role` | A role profile name (`scripts/overlay-paths.sh templates`) that bios-recommend starts from |
| `kvm.keys_backend` | `ssh-hidg`, `pikvm` or `browser` (see `kvm-backends.md`) |
| `kvm.eyes` | `browser` or `pikvm-snapshot` |
| `settings_map` | Real menu paths found on this board, so later sessions navigate without searching |
| `depends_on_it` | What goes down with the machine; shown to the user before any reboot |

Per-machine history goes in `<overlay>/machines/<name>/`: `facts-<date>.json` (firmware-facts.sh output),
`baseline-<date>/` (screenshots + `settings.md`), `plans/<date>-<slug>.md`, `log.md` (one line per session).
