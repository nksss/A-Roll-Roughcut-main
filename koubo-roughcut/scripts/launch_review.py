#!/usr/bin/env python3
"""Prompt for a project directory and open its latest review run."""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    entered = input("请输入项目目录路径（目录下需有 runs 文件夹）: ").strip().strip('"')
    if not entered:
        print("Project directory cannot be empty.", file=sys.stderr)
        return 1

    project_dir = Path(entered).expanduser()
    if not project_dir.is_absolute():
        project_dir = repo_root / project_dir
    project_dir = project_dir.resolve()
    runs_dir = project_dir / "runs"
    if not runs_dir.is_dir():
        print(f"Runs directory not found: {runs_dir}", file=sys.stderr)
        return 1

    runs = sorted((path for path in runs_dir.iterdir() if path.is_dir()), key=lambda path: path.name, reverse=True)
    if not runs:
        print(f"No review run found under: {runs_dir}", file=sys.stderr)
        return 1

    run_dir = runs[0]
    print(f"Opening latest run: {run_dir}", flush=True)
    server = Path(__file__).with_name("review_server.py")
    return subprocess.call([sys.executable, str(server), "--run", str(run_dir)])


if __name__ == "__main__":
    raise SystemExit(main())
