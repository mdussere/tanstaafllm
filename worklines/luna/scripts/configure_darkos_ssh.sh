#!/usr/bin/env bash
# Configure a mounted disposable dArkOS card for the currently active host
# Wi-Fi and key-based SSH. Physical panel timing is selected by BOOT DTBs,
# not by this script. Run as root; it never prints Wi-Fi secrets.
set -euo pipefail

if [[ ${EUID} -ne 0 || $# -ne 2 ]]; then
  echo "Usage: sudo $0 <mounted-dArkOS-ROOTFS> <public-key-file>" >&2
  exit 64
fi

rootfs=$1
public_key=$2

for required_path in \
  "$rootfs/etc/NetworkManager/NetworkManager.conf" \
  "$rootfs/etc/passwd" \
  "$public_key"; do
  [[ -f $required_path ]] || {
    echo "Required file is missing: $required_path" >&2
    exit 66
  }
done

wifi_device="$(nmcli -t -f DEVICE,TYPE,STATE device status | awk -F: '$2 == "wifi" && $3 == "connected" { print $1; exit }')"
[[ -n $wifi_device ]] || {
  echo "No connected host Wi-Fi device was found." >&2
  exit 69
}

profile_name="$(nmcli -g GENERAL.CONNECTION device show "$wifi_device")"
profile_uuid="$(nmcli -g connection.uuid connection show "$profile_name")"
runtime_store=/run/NetworkManager/system-connections
[[ -d $runtime_store ]] || {
  echo "NetworkManager runtime profile store is unavailable." >&2
  exit 69
}

source_profile="$(awk -v uuid="$profile_uuid" '$0 == "uuid=" uuid { print FILENAME; exit }' "$runtime_store"/*.nmconnection)"
[[ -n $source_profile && -f $source_profile ]] || {
  echo "Could not locate the active host Wi-Fi profile by UUID." >&2
  exit 69
}

read -r ark_uid ark_gid < <(awk -F: '$1 == "ark" { print $3, $4; exit }' "$rootfs/etc/passwd")
[[ -n ${ark_uid:-} && -n ${ark_gid:-} ]] || {
  echo "The target root filesystem has no ark account." >&2
  exit 66
}

profile_dir="$rootfs/etc/NetworkManager/system-connections"
target_profile="$profile_dir/host-wifi.nmconnection"
ssh_link="$rootfs/etc/systemd/system/multi-user.target.wants/ssh.service"
authorized_keys="$rootfs/home/ark/.ssh/authorized_keys"

install -d -o root -g root -m 700 "$profile_dir"
install -o root -g root -m 600 "$source_profile" "$target_profile"
# The host profile is explicitly bound to its PCI Wi-Fi device; Luna uses wlan0.
sed -i '/^interface-name=/d' "$target_profile"

install -d -o root -g root -m 755 "$(dirname "$ssh_link")"
ln -sfn /usr/lib/systemd/system/ssh.service "$ssh_link"

install -d -o "$ark_uid" -g "$ark_gid" -m 700 "$(dirname "$authorized_keys")"
touch "$authorized_keys"
chown "$ark_uid:$ark_gid" "$authorized_keys"
chmod 600 "$authorized_keys"
if ! grep -Fqx -f "$public_key" "$authorized_keys"; then
  cat "$public_key" >> "$authorized_keys"
fi

[[ ! -s $target_profile ]] && { echo "Wi-Fi profile installation failed." >&2; exit 74; }
! grep -q '^interface-name=' "$target_profile" || { echo "Host interface lock remains." >&2; exit 74; }
[[ -L $ssh_link ]] || { echo "SSH enablement link is missing." >&2; exit 74; }
[[ -s $authorized_keys ]] || { echo "Authorized key installation failed." >&2; exit 74; }

sync
echo "Configured dArkOS for current host Wi-Fi and ark key-based SSH."
echo "Physical panel timing is intentionally unchanged; select it through a verified BOOT DTB profile."
echo "No Wi-Fi secret was printed. Boot the card, obtain its DHCP address, then use:"
echo "  ssh -i <public-key's-private-counterpart> ark@<Luna-DHCP-IP>"
