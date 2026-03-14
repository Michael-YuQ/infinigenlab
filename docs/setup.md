# Setup

## Assumptions

- Ubuntu 22.04 style Linux environment
- Infinigen installed separately, typically at `~/infinigen`
- Conda environment named `infinigen`

## Recommended layout

```text
~/infinigen
~/infinigen-lab
~/infinigen_outputs
~/miniconda3
```

## Typical activation

```bash
cd "$HOME/infinigen"
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate infinigen
```

## First batch run

```bash
bash "$HOME/infinigenlab/scripts/launch_10_singleroom_coarse_cpu.sh"
```

Equivalent direct command:

```bash
python "$HOME/infinigenlab/scripts/run_indoors_coarse_batch.py" \
  --repo "$HOME/infinigen" \
  --output-root "$HOME/infinigen_outputs/singleroom_coarse_x10_metrics" \
  --num-scenes 10 \
  --parallel 2
```

## Inspecting results

```bash
bash "$HOME/infinigenlab/scripts/check_batch_results.sh"
```
