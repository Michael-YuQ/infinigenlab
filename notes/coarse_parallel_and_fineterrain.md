# Coarse Parallelism and Fine Terrain Notes

Repo inspected:

- `../infinigen`
- commit `892947be71c4ff102c6a558d088ffe149561c11f`

## Coarse stage

- `queue_coarse()` submits `--task coarse` and always requests `gpus=0`.
- In the default `monocular.gin` and `monocular_video.gin` pipelines, `coarse` is a
  `global_task`, so it runs once per scene, not once per frame block.
- Parallelism for `coarse` is scene-level: multiple scenes may have their own
  coarse job queued at the same time if `manage_datagen_jobs.num_concurrent`
  allows it.
- `LocalScheduleHandler` does not enforce CPU or RAM limits for local jobs. For
  CPU-only servers, over-parallelizing can still cause host OOM.

## Fine terrain

- `queue_fine_terrain()` submits `--task fine_terrain`.
- GPU is optional. The queue code only injects `Terrain.device='cuda'` when
  `queue_fine_terrain.gpus > 0`.
- Without `cuda_terrain.gin`, the terrain object stays on `device='cpu'`.
- `fine_terrain()` is camera/view dependent and can run many times for different
  frame blocks in video or multiview settings.

## Map-only takeaway

- If the goal is just a terrain/map output, the cheapest path is usually to run
  only `coarse`.
- `fine_terrain` is mainly the high-detail meshing step for cameras/views; it is
  helpful for rendering and export quality, but not required just to get a basic
  terrain scene on a CPU-only server.
