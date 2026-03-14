# infinigen-lab

Utilities, batch scripts, notes, and experiment helpers for running
[Infinigen](https://github.com/princeton-vl/infinigen) on CPU-first servers.

This repository does not vendor the main Infinigen source tree. Instead, it
assumes you have a separate Infinigen checkout and points scripts at it with a
`--repo` argument or a configurable path.

## What lives here

- `scripts/`: batch runners, install helpers, and simple automation
- `docs/`: setup and usage notes
- `notes/`: source-reading notes and experiment recipes
- `configs/`: custom gin configs and local overrides

## Current focus

- CPU-only setup for Ubuntu 22.04 style servers
- Parallel single-room `coarse` generation for indoors
- CPU usage curve capture during batch generation
- Per-stage timing extraction from Infinigen timer logs

## Quick start

1. Install Infinigen separately, for example at `~/infinigen`
2. Create and activate the `infinigen` conda environment
3. Run the batch helper:

```bash
cd "$HOME/infinigen"
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate infinigen

python "$HOME/infinigen-lab/scripts/run_indoors_coarse_batch.py" \
  --repo "$HOME/infinigen" \
  --output-root "$HOME/infinigen_outputs/singleroom_coarse_x10_metrics" \
  --num-scenes 10 \
  --parallel 2
```

## Outputs from the batch helper

- `cpu_usage.csv`
- `cpu_usage.png`
- `stage_times_detail.csv`
- `stage_times_summary.csv`
- `batch_summary.txt`

Each scene directory also contains:

- `run.log`
- `run.err`
- generated scene outputs on success
