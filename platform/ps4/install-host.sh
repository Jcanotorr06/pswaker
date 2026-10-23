#!/usr/bin/env bash
# Provision exact recorded build packages on Ubuntu 24.04/WSL2. Run as root.
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'Run through wsl -d Ubuntu -u root --exec bash <this file>'; exit 1; }
source /etc/os-release
[[ $ID == ubuntu && $VERSION_ID == 24.04 ]] || { echo 'Expected Ubuntu 24.04'; exit 1; }
stage=$(mktemp -d /tmp/pswaker-host-key.XXXXXX)
curl -fLSs --connect-timeout 20 --max-time 60 https://apt.llvm.org/llvm-snapshot.gpg.key -o "$stage/key.asc"
gpg --batch --show-keys --with-colons "$stage/key.asc" > "$stage/key-info"
grep -q '^fpr:::::::::6084F3CF814B57C1CF12EFD515CF4D18AF4F7421:' "$stage/key-info"
gpg --batch --dearmor --output "$stage/key.gpg" "$stage/key.asc"
install -m 0644 "$stage/key.gpg" /usr/share/keyrings/pswaker-llvm-21.gpg
printf '%s\n' 'deb [arch=amd64 signed-by=/usr/share/keyrings/pswaker-llvm-21.gpg] https://apt.llvm.org/noble/ llvm-toolchain-noble-21 main' > /etc/apt/sources.list.d/pswaker-llvm-21.list
apt-get update
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
mapfile -t packages < <(python3 - "$HERE/host.lock.json" <<'PY'
import json
import sys
for name, version in json.load(open(sys.argv[1]))['required_packages'].items():
    print(name + '=' + version)
PY
)
apt-get install --yes --no-install-recommends "${packages[@]}"
echo 'Installed recorded build package versions. Run inputs.py host to check the recorded host identity.'
