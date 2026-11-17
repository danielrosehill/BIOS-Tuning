# Role: workstation

Goal: performance the hardware was sold with, sane noise, multi-monitor graphics, easy recovery.

| Setting | Target | Why | Risk if wrong |
| --- | --- | --- | --- |
| Memory profile (XMP/EXPO) | Enabled at the kit's rated profile | DIMMs run at JEDEC default without it | Instability: run a memory test after |
| Resizable BAR + Above 4G | Enabled with a modern GPU | GPU performance | None on supported cards |
| Primary display / iGPU | Discrete GPU primary; iGPU multi-monitor on if an IP-KVM uses the motherboard output | Keeps all monitors on the GPU and a spare port for the KVM | Setup screen may only show on the primary adapter |
| Power on after power loss | Off (stay off) | Desktops usually should not start unattended | None |
| Wake-on-LAN | Enabled if the user wakes it remotely | Remote start | None |
| VT-x / SVM, IOMMU | Enabled | VMs, WSL, containers | None |
| Fan curves | Quiet at idle | Noise | Heat under load if too flat |
| Secure Boot | Keep as found unless the user decides | Unsigned modules (NVIDIA, DKMS) | Driver failures |
| Fast boot | Off if the user needs the setup key from a KVM | Setup key window | Locked out of setup |
