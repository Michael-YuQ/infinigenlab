#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-$HOME/infinigen_outputs/singleroom_coarse_x10_metrics}"

if [ ! -d "$OUT_DIR" ]; then
  echo "[error] output directory not found: $OUT_DIR"
  exit 1
fi

echo "=== Batch Summary ==="
if [ -f "$OUT_DIR/batch_summary.txt" ]; then
  cat "$OUT_DIR/batch_summary.txt"
else
  echo "(missing batch_summary.txt)"
fi
echo

echo "=== Stage Summary CSV ==="
if [ -f "$OUT_DIR/stage_times_summary.csv" ]; then
  cat "$OUT_DIR/stage_times_summary.csv"
else
  echo "(missing stage_times_summary.csv)"
fi
echo

echo "=== Success Count ==="
find "$OUT_DIR" -name 'scene.blend' | wc -l
echo

echo "=== Scene Blend Paths ==="
find "$OUT_DIR" -name 'scene.blend' | sort
echo

echo "=== CPU Samples Head ==="
if [ -f "$OUT_DIR/cpu_usage.csv" ]; then
  head "$OUT_DIR/cpu_usage.csv"
else
  echo "(missing cpu_usage.csv)"
fi
