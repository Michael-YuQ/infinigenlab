#!/usr/bin/env bash
set -euo pipefail

LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${REPO_DIR:-$HOME/infinigen}"
CONDA_ROOT="${CONDA_ROOT:-$HOME/miniconda3}"
ENV_NAME="${ENV_NAME:-infinigen}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$HOME/infinigen_outputs/singleroom_coarse_x10_metrics}"
NUM_SCENES="${NUM_SCENES:-10}"
PARALLEL="${PARALLEL:-2}"
SEED_START="${SEED_START:-1}"

if [ ! -d "$REPO_DIR" ]; then
  echo "[error] Infinigen repo not found at $REPO_DIR"
  exit 1
fi

if [ ! -f "$CONDA_ROOT/etc/profile.d/conda.sh" ]; then
  echo "[error] conda.sh not found at $CONDA_ROOT/etc/profile.d/conda.sh"
  exit 1
fi

source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

cd "$REPO_DIR"

python "$LAB_ROOT/scripts/run_indoors_coarse_batch.py" \
  --repo "$REPO_DIR" \
  --output-root "$OUTPUT_ROOT" \
  --num-scenes "$NUM_SCENES" \
  --parallel "$PARALLEL" \
  --seed-start "$SEED_START"
