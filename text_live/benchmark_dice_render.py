from __future__ import annotations

import csv
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_DICE_TYPES = ("D4", "D6", "D8", "D10", "D20")
DEFAULT_COUNTS = (1, 2, 3, 4, 5, 6)
SEED_BASES = {
    "D4": 410000,
    "D6": 610000,
    "D8": 810000,
    "D10": 1010000,
    "D20": 2010000,
}


def main() -> int:
    plugin_dir = Path(os.environ["DICE_PLUGIN_DIR"]).resolve()
    output_root = Path(
        os.environ.get("DICE_BENCH_OUTPUT_DIR", plugin_dir / "text_live" / "benchmarks")
    ).resolve()
    sys.path.insert(0, str(plugin_dir))

    from dice_sim import StyleOptions

    dice_types = _parse_csv_env("DICE_BENCH_DICE", DEFAULT_DICE_TYPES)
    counts = tuple(
        int(value) for value in _parse_csv_env("DICE_BENCH_COUNTS", DEFAULT_COUNTS)
    )
    width = _int_env("DICE_BENCH_WIDTH", 840)
    height = _int_env("DICE_BENCH_HEIGHT", 600)
    fps = _int_env("DICE_BENCH_FPS", 100)
    duration_ms = _int_env("DICE_BENCH_DURATION_MS", 5000)
    final_hold_ms = _int_env("DICE_BENCH_FINAL_HOLD_MS", 3000)
    save_gifs = _bool_env("DICE_BENCH_SAVE_GIFS", True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / f"render_benchmark_{timestamp}"
    gifs_dir = run_dir / "gifs"
    run_dir.mkdir(parents=True, exist_ok=True)
    if save_gifs:
        gifs_dir.mkdir(parents=True, exist_ok=True)

    style = StyleOptions(
        die_color="#ffffff",
        ink_color="#000000",
        edge_color="#000000",
        background_color="#f5f7fb",
    )
    config = {
        "plugin_dir": str(plugin_dir),
        "run_dir": str(run_dir),
        "dice_types": list(dice_types),
        "counts": list(counts),
        "width": width,
        "height": height,
        "fps": fps,
        "duration_ms": duration_ms,
        "final_hold_ms": final_hold_ms,
        "save_gifs": save_gifs,
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "processor": platform.processor(),
    }

    jobs = [(dice_type, count) for dice_type in dice_types for count in counts]
    print("Dice render benchmark")
    print(f"Output: {run_dir}")
    print(
        f"Matrix: {len(dice_types)} dice types x {len(counts)} counts = {len(jobs)} jobs"
    )
    print(
        f"Config: {width}x{height}, fps={fps}, duration_ms={duration_ms}, "
        f"final_hold_ms={final_hold_ms}, save_gifs={save_gifs}"
    )
    print()

    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for index, (dice_type, count) in enumerate(jobs, start=1):
        seed = _seed_for(dice_type, count)
        output_path = gifs_dir / f"{dice_type.lower()}_x{count}_{seed}.gif"
        print(f"[{index:02d}/{len(jobs):02d}] {dice_type} x{count} seed={seed}")
        try:
            row = _benchmark_one(
                dice_type=dice_type,
                count=count,
                seed=seed,
                width=width,
                height=height,
                fps=fps,
                duration_ms=duration_ms,
                final_hold_ms=final_hold_ms,
                style=style,
                output_path=output_path,
                save_gifs=save_gifs,
            )
            print(
                "  render={render_ms:.1f}ms "
                "({render_ms_per_frame:.2f}ms/frame), "
                "physics={physics_ms:.1f}ms, encode={encode_ms:.1f}ms, "
                "total={total_ms:.1f}ms, frames={frames}, settled={settled}".format(
                    **row
                )
            )
        except Exception as exc:
            row = _failure_row(dice_type, count, seed, width, height, fps, exc)
            traceback.print_exc()
            print(f"  FAILED: {exc}")
        rows.append(row)

    total_wall_ms = (time.perf_counter() - started) * 1000.0
    paths = _write_outputs(run_dir, config, rows, total_wall_ms)
    print()
    print(f"Finished in {total_wall_ms:.1f}ms")
    print(f"CSV: {paths['csv']}")
    print(f"JSON: {paths['json']}")
    print(f"Summary: {paths['summary']}")
    if save_gifs:
        print(f"GIFs: {gifs_dir}")
    return 1 if any(row["status"] != "ok" for row in rows) else 0


def _benchmark_one(
    *,
    dice_type: str,
    count: int,
    seed: int,
    width: int,
    height: int,
    fps: int,
    duration_ms: int,
    final_hold_ms: int,
    style: Any,
    output_path: Path,
    save_gifs: bool,
) -> dict[str, Any]:
    from dice_sim.geometry import create_mesh
    from dice_sim.gif import encode_gif
    from dice_sim.physics import simulate_roll
    from dice_sim.render import render_frames
    from dice_sim.result import detect_result

    total_start = time.perf_counter()
    mesh_start = time.perf_counter()
    mesh = create_mesh(dice_type)
    mesh_ms = _elapsed_ms(mesh_start)

    physics_start = time.perf_counter()
    simulation = simulate_roll(mesh, count, seed, duration_ms, fps, final_hold_ms)
    physics_ms = _elapsed_ms(physics_start)

    result_start = time.perf_counter()
    values = tuple(detect_result(mesh, pose) for pose in simulation.final_poses)
    result_ms = _elapsed_ms(result_start)

    render_start = time.perf_counter()
    frames = render_frames(
        mesh,
        simulation.frames,
        width,
        height,
        style,
        values,
        simulation.result_label_start_seconds,
    )
    render_ms = _elapsed_ms(render_start)

    encode_ms = 0.0
    gif_path = ""
    gif_size_bytes = 0
    if save_gifs:
        encode_start = time.perf_counter()
        encoded_path = encode_gif(frames, output_path, fps)
        encode_ms = _elapsed_ms(encode_start)
        gif_path = str(encoded_path)
        gif_size_bytes = encoded_path.stat().st_size

    total_ms = _elapsed_ms(total_start)
    frame_count = len(frames)
    actual_duration_ms = int(round(simulation.frames[-1].time_seconds * 1000))
    settle_time_ms = (
        None
        if simulation.settle_time_seconds is None
        else int(round(simulation.settle_time_seconds * 1000))
    )
    result_label_start_ms = (
        None
        if simulation.result_label_start_seconds is None
        else int(round(simulation.result_label_start_seconds * 1000))
    )
    megapixels = width * height / 1_000_000
    render_ms_per_frame = render_ms / max(1, frame_count)
    return {
        "status": "ok",
        "dice_type": dice_type,
        "count": count,
        "seed": seed,
        "width": width,
        "height": height,
        "fps": fps,
        "duration_ms": duration_ms,
        "final_hold_ms": final_hold_ms,
        "frames": frame_count,
        "settled": simulation.settled,
        "settle_time_ms": settle_time_ms,
        "result_label_start_ms": result_label_start_ms,
        "actual_duration_ms": actual_duration_ms,
        "result_visible_ms": (
            None
            if result_label_start_ms is None
            else actual_duration_ms - result_label_start_ms
        ),
        "results": "+".join(str(value) for value in values),
        "total_result": sum(values),
        "mesh_ms": mesh_ms,
        "physics_ms": physics_ms,
        "result_ms": result_ms,
        "render_ms": render_ms,
        "render_ms_per_frame": render_ms_per_frame,
        "render_ms_per_frame_per_mp": render_ms_per_frame / max(0.001, megapixels),
        "encode_ms": encode_ms,
        "total_ms": total_ms,
        "gif_path": gif_path,
        "gif_size_bytes": gif_size_bytes,
        "horizontal_travel": simulation.horizontal_travel,
        "max_height": simulation.max_height,
        "final_contact_vertices": "+".join(
            str(value) for value in simulation.final_contact_vertices
        ),
        "inter_body_contact_count": simulation.inter_body_contact_count,
        "inter_body_contact_steps": simulation.inter_body_contact_steps,
        "error": "",
    }


def _write_outputs(
    run_dir: Path,
    config: dict[str, Any],
    rows: list[dict[str, Any]],
    total_wall_ms: float,
) -> dict[str, Path]:
    csv_path = run_dir / "metrics.csv"
    json_path = run_dir / "metrics.json"
    summary_path = run_dir / "summary.md"
    fieldnames = list(rows[0].keys()) if rows else []

    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "config": config,
        "total_wall_ms": total_wall_ms,
        "rows": rows,
        "summary": _summary(rows),
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_path.write_text(
        _summary_markdown(config, rows, total_wall_ms),
        encoding="utf-8",
    )
    return {"csv": csv_path, "json": json_path, "summary": summary_path}


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    if not ok_rows:
        return {"ok_jobs": 0, "failed_jobs": len(rows)}
    return {
        "ok_jobs": len(ok_rows),
        "failed_jobs": len(rows) - len(ok_rows),
        "render_ms_total": sum(float(row["render_ms"]) for row in ok_rows),
        "render_ms_avg": _avg(ok_rows, "render_ms"),
        "render_ms_max": max(float(row["render_ms"]) for row in ok_rows),
        "render_ms_per_frame_avg": _avg(ok_rows, "render_ms_per_frame"),
        "physics_ms_avg": _avg(ok_rows, "physics_ms"),
        "encode_ms_avg": _avg(ok_rows, "encode_ms"),
        "total_ms_avg": _avg(ok_rows, "total_ms"),
    }


def _summary_markdown(
    config: dict[str, Any], rows: list[dict[str, Any]], total_wall_ms: float
) -> str:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    failed_rows = [row for row in rows if row["status"] != "ok"]
    lines = [
        "# Dice Render Benchmark",
        "",
        "## Config",
        "",
        f"- Size: {config['width']}x{config['height']}",
        f"- FPS: {config['fps']}",
        f"- Duration: {config['duration_ms']} ms",
        f"- Final hold after result label: {config['final_hold_ms']} ms",
        f"- Save GIFs: {config['save_gifs']}",
        f"- Dice: {', '.join(config['dice_types'])}",
        f"- Counts: {', '.join(str(value) for value in config['counts'])}",
        f"- Total wall time: {total_wall_ms:.1f} ms",
        "",
        "## Overall",
        "",
    ]
    summary = _summary(rows)
    for key, value in summary.items():
        if isinstance(value, float):
            lines.append(f"- {key}: {value:.2f}")
        else:
            lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Average By Dice",
            "",
            "| Dice | Jobs | Frames Avg | Physics Avg ms | Render Avg ms | Render ms/frame | Encode Avg ms | Total Avg ms |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for dice_type in config["dice_types"]:
        dice_rows = [row for row in ok_rows if row["dice_type"] == dice_type]
        if not dice_rows:
            continue
        lines.append(
            "| {dice} | {jobs} | {frames:.1f} | {physics:.1f} | {render:.1f} | {render_pf:.2f} | {encode:.1f} | {total:.1f} |".format(
                dice=dice_type,
                jobs=len(dice_rows),
                frames=_avg(dice_rows, "frames"),
                physics=_avg(dice_rows, "physics_ms"),
                render=_avg(dice_rows, "render_ms"),
                render_pf=_avg(dice_rows, "render_ms_per_frame"),
                encode=_avg(dice_rows, "encode_ms"),
                total=_avg(dice_rows, "total_ms"),
            )
        )

    lines.extend(
        [
            "",
            "## Slowest Render Jobs",
            "",
            "| Dice | Count | Frames | Render ms | Render ms/frame | Physics ms | Encode ms | Total ms | GIF |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    slow_rows = sorted(ok_rows, key=lambda row: float(row["render_ms"]), reverse=True)[:10]
    for row in slow_rows:
        gif_name = Path(str(row["gif_path"])).name if row["gif_path"] else ""
        lines.append(
            "| {dice} | {count} | {frames} | {render:.1f} | {render_pf:.2f} | {physics:.1f} | {encode:.1f} | {total:.1f} | {gif} |".format(
                dice=row["dice_type"],
                count=row["count"],
                frames=row["frames"],
                render=float(row["render_ms"]),
                render_pf=float(row["render_ms_per_frame"]),
                physics=float(row["physics_ms"]),
                encode=float(row["encode_ms"]),
                total=float(row["total_ms"]),
                gif=gif_name,
            )
        )

    if failed_rows:
        lines.extend(["", "## Failed Jobs", ""])
        for row in failed_rows:
            lines.append(
                f"- {row['dice_type']} x{row['count']} seed={row['seed']}: {row['error']}"
            )
    lines.append("")
    return "\n".join(lines)


def _failure_row(
    dice_type: str,
    count: int,
    seed: int,
    width: int,
    height: int,
    fps: int,
    exc: Exception,
) -> dict[str, Any]:
    return {
        "status": "failed",
        "dice_type": dice_type,
        "count": count,
        "seed": seed,
        "width": width,
        "height": height,
        "fps": fps,
        "duration_ms": "",
        "final_hold_ms": "",
        "frames": 0,
        "settled": False,
        "settle_time_ms": "",
        "result_label_start_ms": "",
        "actual_duration_ms": "",
        "result_visible_ms": "",
        "results": "",
        "total_result": "",
        "mesh_ms": 0.0,
        "physics_ms": 0.0,
        "result_ms": 0.0,
        "render_ms": 0.0,
        "render_ms_per_frame": 0.0,
        "render_ms_per_frame_per_mp": 0.0,
        "encode_ms": 0.0,
        "total_ms": 0.0,
        "gif_path": "",
        "gif_size_bytes": 0,
        "horizontal_travel": "",
        "max_height": "",
        "final_contact_vertices": "",
        "inter_body_contact_count": "",
        "inter_body_contact_steps": "",
        "error": str(exc),
    }


def _parse_csv_env(name: str, default: tuple[Any, ...]) -> tuple[str, ...]:
    raw = os.environ.get(name)
    if not raw:
        return tuple(str(value) for value in default)
    values = [part.strip().upper() for part in raw.split(",") if part.strip()]
    return tuple(values) if values else tuple(str(value) for value in default)


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _bool_env(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _seed_for(dice_type: str, count: int) -> int:
    return SEED_BASES.get(dice_type, 990000) + count * 137


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0


def _avg(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows]
    return sum(values) / max(1, len(values))


if __name__ == "__main__":
    raise SystemExit(main())
