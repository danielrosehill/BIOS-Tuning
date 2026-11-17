# Firmware setup by board vendor

Names drift between BIOS releases. Treat these as search terms for the screen, not exact paths, and record
the real path for the user's board in the overlay (`machines.json` -> `settings_map`).

## Keys

| Vendor | Enter setup | Boot menu | Flash utility (key at POST / where in setup) | Save and exit |
| --- | --- | --- | --- | --- |
| Gigabyte (AMI) | Del | F12 | Q-Flash: End at POST, or F8 / button in setup | F10, Enter; or Save & Exit tab (Yes/No dialog) |
| MSI (AMI) | Del | F11 | M-Flash: setup left panel (reboots into flash mode) | F10, Enter |
| ASUS (AMI) | Del or F2 | F8 | EZ Flash: Tool menu, or Alt+F2 at POST on some | F10, Enter |
| ASRock (AMI) | F2 or Del | F11 | Instant Flash: Tool menu | F10, Enter |
| Supermicro | Del | F11 | Usually BMC/IPMI or a UEFI shell flash, not in setup | F4, Enter |
| Dell / HP / Lenovo desktops | F2 / F10 / F1 | F12 / F9 / F12 | Vendor capsule, often via fwupd/LVFS from Linux | varies |

Many boards open in an "EZ" or simplified mode first: F7 (MSI, ASUS) or F2 (Gigabyte) switches to Advanced.

## Common settings

| Intent | Gigabyte | MSI | ASUS | ASRock |
| --- | --- | --- | --- | --- |
| Power on after a power cut | Settings > Platform Power > AC BACK = Always On | Settings > Advanced > Power Management > Restore after AC Power Loss = Power On | Advanced > APM > Restore AC Power Loss = Power On | Advanced > Chipset > Restore on AC/Power Loss = Power On |
| Deep sleep that blocks the above and WoL | Platform Power > ErP | Power Management > ErP Ready | APM > ErP Ready | Chipset > Deep Sleep |
| Wake-on-LAN | Platform Power > Wake on LAN | Wake Up Event Setup > Resume By PCI-E Device | APM > Power On By PCI-E | Chipset > PCIE Devices Power On |
| Virtualisation (VT-x / SVM) | Tweaker > Advanced CPU > Intel Virtualization Technology | OC > CPU Features | Advanced > CPU Configuration | Advanced > CPU Configuration |
| IOMMU (VT-d / AMD-Vi) | Settings > Miscellaneous > VT-d | Settings > Advanced > PCI Subsystem / Integrated | Advanced > System Agent | Advanced > Chipset |
| Memory profile | Tweaker > Extreme Memory Profile (X.M.P.) | OC > A-XMP / Memory Try It | Ai Tweaker > Ai Overclock Tuner | OC Tweaker > DRAM Profile |
| Fan curves | Smart Fan 6 (F6) | Hardware Monitor | Monitor > Q-Fan / Fan Xpert | H/W Monitor > FAN-Tastic |
| Secure Boot | Boot > Secure Boot | Settings > Security > Secure Boot | Boot > Secure Boot | Security > Secure Boot |
| Primary display | Settings > IO Ports > Initial Display Output | Settings > Advanced > Integrated Graphics | Advanced > System Agent > Graphics | Advanced > Chipset > Primary Graphics Adapter |
| Resizable BAR | Settings > IO Ports > Above 4G Decoding + Re-Size BAR | Settings > Advanced > PCIe Sub-system | Advanced > PCI Subsystem | Advanced > Chipset |

## Reading a setting from Linux instead of the screen

Prefer this when it exists: it checks the effect, not the label.

| Setting | Linux check |
| --- | --- |
| BIOS version | `dmidecode -s bios-version` |
| Secure Boot | `mokutil --sb-state` |
| VT-x / SVM | `grep -wE 'vmx|svm' /proc/cpuinfo` |
| VT-d / IOMMU | `ls /sys/kernel/iommu_groups | wc -l` > 0, `dmesg | grep -i -e DMAR -e IOMMU` |
| Memory profile | `dmidecode -t memory` Configured Memory Speed vs rated |
| Wake-on-LAN | `ethtool <iface>` Wake-on (OS side; the BIOS side is only proven by a wake test) |
| Power on after power loss | No Linux readout. Read it on screen, or test by cutting power with a smart plug |
| Boot order | `efibootmgr` |

## Flashing safety

- Read the release notes and the vendor's checksum before flashing. Never flash a beta unless the user asks.
- Find out if the board has a backup BIOS chip (Gigabyte DualBIOS on some models, ASUS/MSI Flashback) and
  how recovery works if a flash fails. Write it in the plan before starting.
- A flash resets every setting on most consumer boards. Capture the baseline first (bios-profile).
- Never cut power or reset during a flash. The KVM must not be powered from a port that flash can drop.
