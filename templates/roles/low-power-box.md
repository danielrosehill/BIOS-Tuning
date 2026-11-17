# Role: low-power always-on box (mini PC, NAS, router appliance)

Goal: lowest idle draw that still returns after a power cut.

| Setting | Target | Why | Risk if wrong |
| --- | --- | --- | --- |
| Power on after power loss | Power On | Unattended recovery | Stays off after a cut |
| C-states / package C-states | Enabled, deepest the board offers | Idle power | Rare NIC latency or instability: test |
| ASPM (PCIe power management) | Enabled | Idle power | Some NICs drop link: test |
| Unused devices (audio, serial, Wi-Fi, RGB) | Disabled | Power and attack surface | None |
| ErP | Disabled if power-on-after-loss or WoL is needed | ErP blocks both on some boards | Higher standby draw |
| Turbo / PL1-PL2 limits | Leave default unless heat is a problem | Fanless boxes may need lower limits | Throttling or slower jobs |
