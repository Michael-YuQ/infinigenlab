#!/usr/bin/env bash
set -euo pipefail

# CPU-only installation for Ubuntu 22.04/24.04 style systems.
# Installs everything under $HOME and avoids /inspire/hdd.

ENV_NAME="${ENV_NAME:-infinigen}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/infinigen}"
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda3}"

echo "[info] ENV_NAME=${ENV_NAME}"
echo "[info] INSTALL_ROOT=${INSTALL_ROOT}"
echo "[info] CONDA_ROOT=${CONDA_ROOT}"

if command -v sudo >/dev/null 2>&1; then
  APT_PREFIX=(sudo)
else
  APT_PREFIX=()
fi

echo "[step] Installing system dependencies"
"${APT_PREFIX[@]}" apt-get update
"${APT_PREFIX[@]}" apt-get install -y \
  wget \
  git \
  cmake \
  g++ \
  build-essential \
  libgles2-mesa-dev \
  libglew-dev \
  libglfw3-dev \
  libglm-dev \
  zlib1g-dev

if [ ! -x "${CONDA_ROOT}/bin/conda" ]; then
  echo "[step] Installing Miniconda to ${CONDA_ROOT}"
  TMP_SH="$(mktemp --suffix=.sh)"
  wget -O "${TMP_SH}" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash "${TMP_SH}" -b -p "${CONDA_ROOT}"
  rm -f "${TMP_SH}"
else
  echo "[step] Reusing existing Miniconda at ${CONDA_ROOT}"
fi

source "${CONDA_ROOT}/etc/profile.d/conda.sh"

if ! conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "[step] Creating conda environment ${ENV_NAME}"
  conda create -y -n "${ENV_NAME}" python=3.11
else
  echo "[step] Reusing existing conda environment ${ENV_NAME}"
fi

conda activate "${ENV_NAME}"

echo "[step] Preparing source checkout in ${INSTALL_ROOT}"
if [ ! -d "${INSTALL_ROOT}/.git" ]; then
  git clone https://github.com/princeton-vl/infinigen.git "${INSTALL_ROOT}"
else
  echo "[step] Existing git checkout found at ${INSTALL_ROOT}, leaving it in place"
fi

cd "${INSTALL_ROOT}"

echo "[step] Upgrading packaging tools"
pip install -U pip setuptools wheel

echo "[step] Installing Infinigen terrain build for CPU-only map generation"
pip install -e ".[terrain]"

echo "[step] Quick import check"
python -c "import infinigen; print('infinigen import ok')"

cat <<EOF

[done] Infinigen CPU install completed.

Activate environment:
  source "${CONDA_ROOT}/etc/profile.d/conda.sh"
  conda activate "${ENV_NAME}"

Repo path:
  cd "${INSTALL_ROOT}"

First coarse-map test:
  python -m infinigen_examples.generate_nature \\
    --seed 123 \\
    --task coarse \\
    --output_folder "\$HOME/infinigen_outputs/map_123" \\
    -g desert.gin simple.gin no_assets.gin

EOF
