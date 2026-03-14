#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 OUTPUT_DIR SEED [SCENE_TYPE] [EXTRA_GIN_OVERRIDES...]"
  echo "Example: $0 /home/wsl/outputs/map_0001 123 desert"
  exit 1
fi

OUTPUT_DIR="$1"
SEED="$2"
SCENE_TYPE="${3:-desert}"
shift 3 || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/../../infinigen" && pwd)"

SCENE_TYPE="${SCENE_TYPE%.gin}"

mkdir -p "${OUTPUT_DIR}"

cd "${REPO_DIR}"

python -m infinigen_examples.generate_nature \
  --seed "${SEED}" \
  --task coarse \
  --output_folder "${OUTPUT_DIR}" \
  -g "${SCENE_TYPE}.gin" simple.gin no_assets.gin \
  "$@"
