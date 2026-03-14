# Run 10 Single-Room Coarse Jobs With Metrics

Use this script for CPU-only batch generation:

```bash
cd "$HOME/infinigen"
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate infinigen

python /home/wsl/infinigen-current-work/infinigen_mods/scripts/run_indoors_coarse_batch.py \
  --repo "$HOME/infinigen" \
  --output-root "$HOME/infinigen_outputs/singleroom_coarse_x10_metrics" \
  --num-scenes 10 \
  --parallel 2
```

Outputs:

- `cpu_usage.csv`: sampled CPU utilization over time
- `cpu_usage.png`: CPU utilization curve
- `stage_times_detail.csv`: per-seed timer records parsed from logs
- `stage_times_summary.csv`: average/min/max stage durations across scenes
- `batch_summary.txt`: job exit codes and overall elapsed time

Each scene also gets:

- `SEED/run.log`
- `SEED/run.err`
- `SEED/scene.blend` on success
