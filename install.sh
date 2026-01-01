#!/usr/bin/env bash
set -euo pipefail

# Change these if you want a different venv folder or requirements file
VENV_DIR=".venv"
REQ_FILE="requirements.txt"

echo "==> Installing system dependencies (Debian/Ubuntu)..."
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y \
    python3 python3-venv python3-pip \
    python3-gi python3-gi-cairo python3-cairo \
    gir1.2-gtk-3.0 gir1.2-pango-1.0 \
    libcairo2-dev pkg-config \
    gobject-introspection libgirepository1.0-dev
else
  echo "ERROR: This install.sh currently supports apt-based systems (Debian/Ubuntu)."
  echo "       You're missing apt-get; add a Fedora/Arch/macOS branch if needed."
  exit 1
fi

echo "==> Creating virtual environment (${VENV_DIR}) with system site packages..."
# If the venv already exists but was created WITHOUT system-site-packages, recreating is safest.
if [[ -d "${VENV_DIR}" ]]; then
  # Detect whether this venv includes system-site-packages (pyvenv.cfg has include-system-site-packages = true)
  if [[ -f "${VENV_DIR}/pyvenv.cfg" ]] && ! grep -qi '^include-system-site-packages\s*=\s*true' "${VENV_DIR}/pyvenv.cfg"; then
    echo "==> Existing venv does not include system site packages; recreating..."
    rm -rf "${VENV_DIR}"
  fi
fi

python3 -m venv "${VENV_DIR}" --system-site-packages

echo "==> Activating venv and installing Python dependencies..."
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip setuptools wheel

if [[ -f "${REQ_FILE}" ]]; then
  pip install -r "${REQ_FILE}"
else
  echo "WARNING: ${REQ_FILE} not found; skipping pip requirements install."
fi

# If your requirements.txt doesn't include Pillow yet, this guarantees PIL imports work:
pip install --upgrade Pillow

echo "==> Quick import test..."
python - <<'PY'
import gi
import cairo
from PIL import Image
print("OK: gi, cairo, PIL(Pillow) imports succeeded")
PY

echo "==> Done."
echo "Activate later with: source ${VENV_DIR}/bin/activate"
