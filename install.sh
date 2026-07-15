#!/usr/bin/env bash
set -euo pipefail
# One-line installer for arch-map
# Usage: curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/arch-map/main/install.sh | bash

if command -v pipx &>/dev/null; then
  pipx install git+https://github.com/fabiocicerchia/arch-map
else
  pip install --user git+https://github.com/fabiocicerchia/arch-map
fi
echo "arch-map installed. Run: arch-map --help"
