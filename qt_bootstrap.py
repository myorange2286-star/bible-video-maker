"""Local Qt runtime bootstrap for macOS PyQt6 launches.

Qt plugin scanning can fail inside a hidden or metadata-heavy virtualenv path on
macOS. This copies the plugin tree into a visible repo-local cache and points
Qt at that cache before QApplication is created.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def _copy_tree_without_macos_flags(src: Path, dst: Path) -> None:
    """Copy files without preserving macOS flags/xattrs that confuse Qt scans."""
    dst.mkdir(parents=True, exist_ok=True)

    for entry in src.iterdir():
        target = dst / entry.name
        if entry.is_dir():
            _copy_tree_without_macos_flags(entry, target)
            continue

        shutil.copyfile(entry, target)
        shutil.copymode(entry, target)


def _replace_symlink(target: Path, source: Path) -> None:
    if target.is_symlink() or target.exists():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.symlink_to(source)


def prepare_qt_runtime(project_root: Path | None = None) -> Path:
    """Create a visible Qt plugin cache and export paths before QApplication."""
    if project_root is None:
        project_root = Path(__file__).resolve().parent
    else:
        project_root = project_root.resolve()

    import PyQt6  # Imported lazily so callers can run before QtWidgets import.
    from PyQt6.QtCore import QCoreApplication

    pyqt_root = Path(PyQt6.__file__).resolve().parent / "Qt6"
    source_plugins = pyqt_root / "plugins"
    runtime_root = project_root / "qt_runtime"
    runtime_plugins = runtime_root / "plugins"

    marker = runtime_root / ".source-root"
    expected_marker = str(source_plugins)

    rebuild = not (runtime_plugins / "platforms").exists()
    if marker.exists():
        rebuild = rebuild or marker.read_text(encoding="utf-8").strip() != expected_marker
    else:
        rebuild = True

    if rebuild:
        if runtime_plugins.exists():
            shutil.rmtree(runtime_plugins)
        runtime_root.mkdir(parents=True, exist_ok=True)
        _copy_tree_without_macos_flags(source_plugins, runtime_plugins)
        marker.write_text(expected_marker, encoding="utf-8")

    for name in ("lib", "libexec", "qml", "translations"):
        source = pyqt_root / name
        target = runtime_root / name
        if not source.exists():
            continue
        if not target.is_symlink() or target.resolve() != source.resolve():
            _replace_symlink(target, source)

    os.environ["QT_PLUGIN_PATH"] = str(runtime_plugins)
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(runtime_plugins / "platforms")
    QCoreApplication.setLibraryPaths([str(runtime_plugins)])
    return runtime_root
