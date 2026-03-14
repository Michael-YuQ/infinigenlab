#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${ENV_NAME:-infinigen}"
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda3}"
INSTALL_ROOT="${INSTALL_ROOT:-$HOME/infinigen}"
SEED="${1:-123}"
SCENE_TYPE="${2:-desert}"
OUTPUT_DIR="${3:-$HOME/infinigen_outputs/map_${SEED}}"

source "${CONDA_ROOT}/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"
cd "${INSTALL_ROOT}"

python -m infinigen_examples.generate_nature \
  --seed "${SEED}" \
  --task coarse \
  --output_folder "${OUTPUT_DIR}" \
  -g "${SCENE_TYPE%.gin}.gin" simple.gin no_assets.gin
