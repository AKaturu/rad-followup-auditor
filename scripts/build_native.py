from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a PyInstaller native CLI artifact.")
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--package", required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    repo = Path.cwd()
    build_dir = repo / "build" / "native"
    dist_dir = repo / "dist"
    native_dir = dist_dir / "native"
    entrypoint = build_dir / f"{args.app_name.replace('-', '_')}_entry.py"

    build_dir.mkdir(parents=True, exist_ok=True)
    native_dir.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text(
        f"from {args.module} import app\n\n"
        "if __name__ == '__main__':\n"
        "    app()\n",
        encoding="utf-8",
    )

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--name",
        args.app_name,
        "--collect-all",
        args.package,
    ]
    excluded_modules = [
        "_pytest",
        "coverage",
        "hypothesis",
        "matplotlib",
        "mypy",
        "pytest",
        "ruff",
        "scipy",
        "sklearn",
        "tensorflow",
    ]
    for module in excluded_modules:
        command.extend(["--exclude-module", module])
    command.append(str(entrypoint))
    subprocess.run(command, check=True)

    executable = dist_dir / (f"{args.app_name}.exe" if platform.system() == "Windows" else args.app_name)
    subprocess.run([str(executable), "--help"], check=True, timeout=60)

    version = importlib.metadata.version(args.project_name)
    system = platform.system().lower()
    machine = platform.machine().lower() or "unknown"
    stem = f"{args.app_name}-{version}-{system}-{machine}"
    staging = build_dir / stem
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    packaged_exe = staging / executable.name
    shutil.copy2(executable, packaged_exe)
    manifest = {
        "app": args.app_name,
        "project": args.project_name,
        "version": version,
        "platform": system,
        "architecture": machine,
        "executable": executable.name,
        "sha256": sha256(packaged_exe),
    }
    (staging / "BUILD-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (staging / "README.txt").write_text(
        f"{args.app_name} {version}\n\n"
        f"Run ./{executable.name} --help to see available commands.\n"
        "Use synthetic or de-identified radiology report CSVs only.\n",
        encoding="utf-8",
    )

    archive_format = "zip" if platform.system() == "Windows" else "gztar"
    archive_path = shutil.make_archive(str(native_dir / stem), archive_format, staging)
    archive = Path(archive_path)
    checksum = sha256(archive)
    (native_dir / f"{archive.name}.sha256").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    print(f"Built {archive}")


if __name__ == "__main__":
    main()
