# Repo Layout

## scripts

- `run_indoors_coarse_batch.py`: parallel single-room coarse generation with CPU monitoring
- `run_single_coarse_map.sh`: one-shot nature coarse map generation
- `run_parallel_coarse_maps.sh`: simple parallel launcher for nature coarse maps
- `install_infinigen_cpu_home.sh`: home-directory CPU-first install helper
- `run_first_coarse_map_home.sh`: smoke test after installation

## notes

- `coarse_parallel_and_fineterrain.md`: findings from reading Infinigen scheduling and terrain code
- `run_10_singleroom_coarse_with_metrics.md`: recipe for the current main batch workflow

## configs

Reserved for custom gin files and local overrides.
