#!/usr/bin/env bash
# Read everything about a machine's firmware that Linux can see without a reboot. Prints JSON.
# Run on the target:  ssh <target> 'sudo bash -s' < firmware-facts.sh > facts.json
# Needs root for dmidecode. Read-only: changes nothing.
set -uo pipefail

j() { python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'; }
dmi() { dmidecode -s "$1" 2>/dev/null | head -1 | j; }
cmd() { "$@" 2>/dev/null | j; }

sb=$(mokutil --sb-state 2>/dev/null | head -1)
[[ -z "$sb" && -d /sys/firmware/efi ]] && sb="unknown (mokutil missing)"
[[ -d /sys/firmware/efi ]] && boot=UEFI || boot=legacy

virt=none
grep -qw vmx /proc/cpuinfo && virt=vmx
grep -qw svm /proc/cpuinfo && virt=svm
iommu=$( [[ -d /sys/kernel/iommu_groups ]] && ls /sys/kernel/iommu_groups | wc -l || echo 0)

wol="[]"
if command -v ethtool >/dev/null; then
  wol=$(for i in $(ls /sys/class/net | grep -vE '^(lo|docker|br-|veth|virbr|tailscale|wg)'); do
          w=$(ethtool "$i" 2>/dev/null | awk -F': ' '/^\s*Wake-on:/{print $2}')
          [[ -n "$w" ]] && printf '{"iface":"%s","wake_on":"%s"},' "$i" "$w"
        done | sed 's/,$//'); wol="[$wol]"
fi

mem=$(dmidecode -t memory 2>/dev/null | awk -F': ' '
  function out() { if (size != "" && size !~ /No Module/) printf "{\"slot\":\"%s\",\"size\":\"%s\",\"rated\":\"%s\",\"configured\":\"%s\",\"part\":\"%s\"},", loc, size, spd, cfg, pn; size=""; spd=""; cfg=""; loc=""; pn="" }
  /^Memory Device/ {out()}
  /^\tSize:/ {size=$2} /^\tSpeed:/ {spd=$2} /^\tConfigured Memory Speed:/ {cfg=$2}
  /^\tLocator:/ {loc=$2} /^\tPart Number:/ {pn=$2; gsub(/ +$/, "", pn)}
  END {out()}' | sed 's/,$//')

cat <<EOF
{
  "collected_at": "$(date -u +%FT%TZ)",
  "hostname": $(hostname | j),
  "board_vendor": $(dmi baseboard-manufacturer),
  "board_model": $(dmi baseboard-product-name),
  "board_version": $(dmi baseboard-version),
  "system_product": $(dmi system-product-name),
  "bios_vendor": $(dmi bios-vendor),
  "bios_version": $(dmi bios-version),
  "bios_date": $(dmi bios-release-date),
  "cpu": $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | j),
  "microcode": $(grep -m1 microcode /proc/cpuinfo | cut -d: -f2 | j),
  "boot_mode": "$boot",
  "secure_boot": $(echo "$sb" | j),
  "virtualisation_flag": "$virt",
  "iommu_groups": $iommu,
  "memory": [${mem}],
  "wake_on_lan": $wol,
  "efi_boot_entries": $(cmd efibootmgr),
  "fwupd_devices": $(fwupdmgr get-devices --json 2>/dev/null | python3 -c 'import json,sys
try:
  d=json.load(sys.stdin); print(json.dumps([{"name":x.get("Name"),"version":x.get("Version"),"updatable":"updatable" in x.get("Flags",[])} for x in d.get("Devices",[]) if x.get("Version")]))
except Exception: print("null")')
}
EOF
