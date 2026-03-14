#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 OUTPUT_ROOT MAX_PARALLEL SCENE_TYPE SEED [SEED ...]"
  echo "Example: $0 /home/wsl/outputs/maps 2 desert 101 102 103"
  exit 1
fi

OUTPUT_ROOT="$1"
MAX_PARALLEL="$2"
SCENE_TYPE="${3%.gin}"
shift 3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SINGLE_RUNNER="${SCRIPT_DIR}/run_single_coarse_map.sh"

mkdir -p "${OUTPUT_ROOT}"

running=0

for seed in "$@"; do
  out_dir="${OUTPUT_ROOT}/${seed}"
  echo "[launch] seed=${seed} -> ${out_dir}"
  "${SINGLE_RUNNER}" "${out_dir}" "${seed}" "${SCENE_TYPE}" &
  running=$((running + 1))

  if [ "${running}" -ge "${MAX_PARALLEL}" ]; then
    wait -n
    running=$((running - 1))
  fi
done

wait
