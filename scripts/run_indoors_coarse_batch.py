#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import threading
import time
from collections import defaultdict
from pathlib import Path


TIMER_START_RE = re.compile(r"\[(?P<ts>[0-9:\.]+)\] \[[^\]]+\] \[INFO\] \| \[(?P<name>.+)\]$")
TIMER_END_RE = re.compile(
    r"\[(?P<ts>[0-9:\.]+)\] \[[^\]]+\] \[INFO\] \| \[(?P<name>.+)\] finished in (?P<dur>.+)$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run many Infinigen single-room coarse jobs in parallel and record CPU usage."
    )
    parser.add_argument("--repo", type=Path, default=Path.home() / "infinigen")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path.home() / "infinigen_outputs" / "singleroom_coarse_x10_cpu",
    )
    parser.add_argument("--num-scenes", type=int, default=10)
    parser.add_argument("--parallel", type=int, default=2)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--sample-sec", type=float, default=1.0)
    parser.add_argument(
        "--extra-override",
        action="append",
        default=[],
        help="Extra gin overrides to append to each job.",
    )
    return parser.parse_args()


def read_cpu_times() -> tuple[int, int]:
    with open("/proc/stat", "r", encoding="utf-8") as f:
        first = f.readline().strip()
    parts = first.split()
    if parts[0] != "cpu":
        raise ValueError(f"Unexpected /proc/stat line: {first}")
    values = list(map(int, parts[1:]))
    idle = values[3] + values[4]
    total = sum(values)
    return total, idle


def cpu_monitor(stop_event: threading.Event, out_csv: Path, sample_sec: float) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    prev_total, prev_idle = read_cpu_times()

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["elapsed_sec", "cpu_percent"])

        while not stop_event.is_set():
            time.sleep(sample_sec)
            total, idle = read_cpu_times()
            delta_total = total - prev_total
            delta_idle = idle - prev_idle
            prev_total, prev_idle = total, idle

            if delta_total <= 0:
                cpu_percent = 0.0
            else:
                cpu_percent = 100.0 * (1.0 - (delta_idle / delta_total))

            writer.writerow([round(time.time() - start_time, 3), round(cpu_percent, 3)])
            f.flush()


def make_cpu_plot(csv_path: Path, png_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"[warn] Could not import matplotlib for CPU plot: {exc}")
        return

    xs: list[float] = []
    ys: list[float] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            xs.append(float(row["elapsed_sec"]))
            ys.append(float(row["cpu_percent"]))

    if not xs:
        print("[warn] No CPU samples captured, skipping plot")
        return

    plt.figure(figsize=(10, 4))
    plt.plot(xs, ys, linewidth=1.5)
    plt.xlabel("Elapsed Time (s)")
    plt.ylabel("CPU Utilization (%)")
    plt.title("Infinigen Batch CPU Usage")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()


def parse_timer_log(log_path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not log_path.exists():
        return rows

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = TIMER_END_RE.search(line.strip())
            if match:
                rows.append((match.group("name"), match.group("dur")))
    return rows


def write_stage_reports(scene_dirs: list[Path], summary_csv: Path, detail_csv: Path) -> None:
    detail_rows: list[tuple[str, str, str]] = []
    aggregate: dict[str, list[float]] = defaultdict(list)

    for scene_dir in scene_dirs:
        seed = scene_dir.name
        log_path = scene_dir / "run.log"
        for stage_name, dur_text in parse_timer_log(log_path):
            detail_rows.append((seed, stage_name, dur_text))
            try:
                h, m, s = dur_text.split(":")
                seconds = int(h) * 3600 + int(m) * 60 + float(s)
                aggregate[stage_name].append(seconds)
            except Exception:
                continue

    detail_csv.parent.mkdir(parents=True, exist_ok=True)
    with detail_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["seed", "stage", "duration_text"])
        writer.writerows(detail_rows)

    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["stage", "count", "avg_sec", "min_sec", "max_sec"])
        for stage_name in sorted(aggregate):
            vals = aggregate[stage_name]
            writer.writerow(
                [
                    stage_name,
                    len(vals),
                    round(sum(vals) / len(vals), 3),
                    round(min(vals), 3),
                    round(max(vals), 3),
                ]
            )


def launch_job(repo: Path, output_dir: Path, seed: int, extra_overrides: list[str]) -> subprocess.Popen:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "run.log"
    err_path = output_dir / "run.err"

    cmd = [
        "python",
        "-m",
        "infinigen_examples.generate_indoors",
        "--seed",
        str(seed),
        "--task",
        "coarse",
        "--output_folder",
        str(output_dir),
        "-g",
        "fast_solve.gin",
        "singleroom.gin",
        "-p",
        "compose_indoors.terrain_enabled=False",
        *extra_overrides,
    ]

    stdout_f = log_path.open("w", encoding="utf-8")
    stderr_f = err_path.open("w", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=repo, stdout=stdout_f, stderr=stderr_f)


def main() -> None:
    args = parse_args()
    args.output_root.mkdir(parents=True, exist_ok=True)

    cpu_csv = args.output_root / "cpu_usage.csv"
    cpu_png = args.output_root / "cpu_usage.png"
    stage_summary_csv = args.output_root / "stage_times_summary.csv"
    stage_detail_csv = args.output_root / "stage_times_detail.csv"
    batch_summary_txt = args.output_root / "batch_summary.txt"

    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=cpu_monitor,
        args=(stop_event, cpu_csv, args.sample_sec),
        daemon=True,
    )
    monitor_thread.start()

    running: list[tuple[int, Path, subprocess.Popen]] = []
    scene_dirs: list[Path] = []
    seed_values = list(range(args.seed_start, args.seed_start + args.num_scenes))
    results: list[tuple[int, int]] = []
    batch_start = time.time()

    try:
        for seed in seed_values:
            while len(running) >= args.parallel:
                next_running: list[tuple[int, Path, subprocess.Popen]] = []
                for r_seed, r_dir, proc in running:
                    code = proc.poll()
                    if code is None:
                        next_running.append((r_seed, r_dir, proc))
                    else:
                        results.append((r_seed, code))
                        print(f"[done] seed={r_seed} exit={code} dir={r_dir}")
                running = next_running
                if len(running) >= args.parallel:
                    time.sleep(2)

            scene_dir = args.output_root / str(seed)
            proc = launch_job(args.repo, scene_dir, seed, args.extra_override)
            scene_dirs.append(scene_dir)
            running.append((seed, scene_dir, proc))
            print(f"[launch] seed={seed} pid={proc.pid} dir={scene_dir}")

        while running:
            next_running = []
            for r_seed, r_dir, proc in running:
                code = proc.poll()
                if code is None:
                    next_running.append((r_seed, r_dir, proc))
                else:
                    results.append((r_seed, code))
                    print(f"[done] seed={r_seed} exit={code} dir={r_dir}")
            running = next_running
            if running:
                time.sleep(2)
    finally:
        stop_event.set()
        monitor_thread.join(timeout=5)

    write_stage_reports(scene_dirs, stage_summary_csv, stage_detail_csv)
    make_cpu_plot(cpu_csv, cpu_png)

    total_elapsed = time.time() - batch_start
    ok = sum(1 for _, code in results if code == 0)
    failed = sum(1 for _, code in results if code != 0)

    with batch_summary_txt.open("w", encoding="utf-8") as f:
        f.write(f"output_root: {args.output_root}\n")
        f.write(f"num_scenes: {args.num_scenes}\n")
        f.write(f"parallel: {args.parallel}\n")
        f.write(f"elapsed_sec: {round(total_elapsed, 3)}\n")
        f.write(f"succeeded: {ok}\n")
        f.write(f"failed: {failed}\n")
        for seed, code in sorted(results):
            f.write(f"seed {seed}: exit {code}\n")

    print(f"[summary] output_root={args.output_root}")
    print(f"[summary] succeeded={ok} failed={failed} elapsed_sec={round(total_elapsed, 3)}")
    print(f"[summary] cpu_csv={cpu_csv}")
    print(f"[summary] cpu_png={cpu_png}")
    print(f"[summary] stage_summary_csv={stage_summary_csv}")
    print(f"[summary] stage_detail_csv={stage_detail_csv}")


if __name__ == "__main__":
    main()
