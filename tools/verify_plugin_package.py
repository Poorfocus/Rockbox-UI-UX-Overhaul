#!/usr/bin/env python3
"""Verify that built plugins were packaged into the runtime tree or zip."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_BUILD_DIR = Path("apps/plugins")
ROCKS_ROOT = "rocks"


def read_trimmed_lines(path: Path) -> list[str]:
    lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def parse_categories() -> dict[str, str]:
    categories_path = REPO_ROOT / "apps" / "plugins" / "CATEGORIES"
    mapping: dict[str, str] = {}
    for line in read_trimmed_lines(categories_path):
        plugin, category = line.split(",", 1)
        mapping[plugin.strip()] = category.strip()
    return mapping


def parse_viewers() -> dict[str, str]:
    viewers_path = REPO_ROOT / "apps" / "plugins" / "viewers.config"
    mapping: dict[str, str] = {}
    for line in read_trimmed_lines(viewers_path):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue
        plugin_path = parts[1]
        if "/" not in plugin_path:
            continue
        directory, plugin = plugin_path.rsplit("/", 1)
        mapping.setdefault(plugin, directory)
    return mapping


def expected_plugin_paths(build_dir: Path) -> tuple[dict[str, str], list[str]]:
    categories = parse_categories()
    viewers = parse_viewers()
    expected: dict[str, str] = {}
    unmapped: list[str] = []

    for plugin_path in sorted((build_dir / PLUGIN_BUILD_DIR).glob("*.rock")):
        plugin_name = plugin_path.stem
        if plugin_name in viewers:
            relative_path = f"{ROCKS_ROOT}/{viewers[plugin_name]}/{plugin_name}.rock"
        elif plugin_name in categories:
            category = categories[plugin_name]
            if category == "games" and plugin_name.startswith("sgt-"):
                relative_path = f"{ROCKS_ROOT}/games/sgt_puzzles/{plugin_name}.rock"
            else:
                relative_path = f"{ROCKS_ROOT}/{category}/{plugin_name}.rock"
        else:
            relative_path = f"{ROCKS_ROOT}/{plugin_name}.rock"
            unmapped.append(plugin_name)

        expected[plugin_name] = relative_path

    return expected, unmapped


def collect_package_files(package_root: Path | None, zip_artifact: Path | None) -> set[str]:
    if package_root is not None:
        files: set[str] = set()
        for path in package_root.rglob("*"):
            if path.is_file():
                files.add(path.relative_to(package_root).as_posix())
        return files

    if zip_artifact is None:
        raise ValueError("Either package_root or zip_artifact must be provided")

    files = set()
    with zipfile.ZipFile(zip_artifact) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            if not name.startswith(".rockbox/"):
                continue
            files.add(name[len(".rockbox/"):])
    return files


def expected_extra_files(packaged_plugins: set[str]) -> list[str]:
    extras: list[str] = []

    def has_plugin(relative_path: str) -> bool:
        return relative_path in packaged_plugins

    if has_plugin("rocks/apps/disktidy.rock"):
        extras.append("rocks/apps/disktidy.config")
    if has_plugin("rocks/viewers/open_plugins.rock"):
        extras.append("rocks/apps/open_plugins.opx")
    if has_plugin("rocks/demos/pictureflow.rock"):
        extras.extend(
            [
                "rocks/demos/pictureflow_emptyslide.bmp",
                "rocks/demos/pictureflow_splash.bmp",
            ]
        )
    if has_plugin("rocks/games/sokoban.rock"):
        extras.append("rocks/games/sokoban.levels")
    if has_plugin("rocks/games/snake2.rock"):
        extras.append("rocks/games/snake2.levels")
    if has_plugin("rocks/viewers/lua.rock"):
        extras.append("rocks/viewers/lua/actions.lua")
    if has_plugin("rocks/games/picross.rock"):
        extras.extend(
            [
                "rocks/games/.picross/picross_default.picross",
                "rocks/games/picross_numbers.bmp",
            ]
        )

    return extras


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, help="Configured build directory")
    parser.add_argument("--package-root", help="Installed .rockbox root to verify")
    parser.add_argument("--zip-artifact", help="rockbox.zip artifact to verify")
    args = parser.parse_args()

    if bool(args.package_root) == bool(args.zip_artifact):
        parser.error("Pass exactly one of --package-root or --zip-artifact")

    build_dir = Path(args.build_dir).resolve()
    package_root = Path(args.package_root).resolve() if args.package_root else None
    zip_artifact = Path(args.zip_artifact).resolve() if args.zip_artifact else None

    expected_plugins, unmapped_plugins = expected_plugin_paths(build_dir)
    packaged_files = collect_package_files(package_root, zip_artifact)
    packaged_plugins = {path for path in packaged_files if path.endswith(".rock")}
    packaged_plugin_names = {PurePosixPath(path).name for path in packaged_plugins}

    missing_paths: list[str] = []
    misplaced_paths: list[str] = []
    for plugin_name, expected_path in expected_plugins.items():
        plugin_file = f"{plugin_name}.rock"
        if expected_path in packaged_files:
            continue
        if plugin_file in packaged_plugin_names:
            actual_locations = sorted(
                path for path in packaged_plugins if PurePosixPath(path).name == plugin_file
            )
            misplaced_paths.append(f"{plugin_file} expected {expected_path} but found {', '.join(actual_locations)}")
        else:
            missing_paths.append(expected_path)

    missing_extras = [path for path in expected_extra_files(packaged_plugins) if path not in packaged_files]

    scope = f"package root {package_root}" if package_root is not None else f"zip {zip_artifact}"
    print(f"Plugin package audit: {scope}")
    print(f"  build dir      : {build_dir}")
    print(f"  built plugins  : {len(expected_plugins)}")
    print(f"  packaged rocks : {len(packaged_plugins)}")

    if unmapped_plugins:
        print("  [WARN] built plugins not mapped by viewers.config or CATEGORIES:")
        for plugin_name in unmapped_plugins:
            print(f"    - {plugin_name}.rock")

    failed = False
    if missing_paths:
        failed = True
        print("  [MISS] missing packaged plugins:")
        for path in missing_paths:
            print(f"    - {path}")

    if misplaced_paths:
        failed = True
        print("  [MISS] misplaced packaged plugins:")
        for message in misplaced_paths:
            print(f"    - {message}")

    if missing_extras:
        failed = True
        print("  [MISS] missing plugin sidecar files:")
        for path in missing_extras:
            print(f"    - {path}")

    if failed:
        print("Result: FAILED")
        return 1

    print("Result: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
