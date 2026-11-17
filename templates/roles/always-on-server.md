# Role: always-on server

Goal: comes back by itself after any power event, stays stable, can be managed remotely.

| Setting | Target | Why | Risk if wrong |
| --- | --- | --- | --- |
| Power on after power loss | Power On / Always On | Returns after a power cut with nobody home | "Last state" leaves it off if it was off at the cut |
| ErP / deep sleep | Disabled | ErP can cut standby power, which breaks power-on-after-loss and WoL on some boards | Slightly higher standby draw |
| Wake-on-LAN | Enabled | Remote power-on if it was shut down on purpose | None |
| VT-x / SVM | Enabled | VMs, containers with nested virt | None |
| VT-d / IOMMU | Enabled if it runs VMs with passthrough | PCI passthrough | Rare driver issues; test |
| Memory profile (XMP/EXPO) | Off or a conservative profile | Stability over speed; check RAM is stable before enabling | Instability, silent corruption |
| Secure Boot | Keep as found unless the user decides | Changing it can stop unsigned modules (DKMS) loading | Boot or driver failures |
| Fan curves | Quiet at idle, full by about 75-80 C CPU | Headless boxes in cabinets run warm | Thermal throttling |
| Boot order | OS disk first; USB/network boot off or after | Avoids booting a forgotten stick after a power cut | Boots wrong media |
| POST delay / fast boot | Fast boot off, setup key window kept | The KVM needs time to catch the setup key | Locked out of setup without a CMOS clear |
| Watchdog (if offered) | Leave off unless the OS feeds it | An unfed watchdog reboots the box | Boot loops |
