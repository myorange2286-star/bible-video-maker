# -*- coding: utf-8 -*-
"""영상 생성 — QThread + ffmpeg concat demuxer"""
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from models.verse import Verse
from models.settings import SlideSettings
from rendering.slide_renderer import SlideRenderer


def find_ffmpeg() -> str | None:
    """ffmpeg 실행 파일 경로 탐색. 앱 내장 → 시스템 순서로 검색."""
    import sys

    # 1. 앱에 내장된 ffmpeg (PyInstaller 패키징 시)
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.dirname(base)  # 프로젝트 루트

    # Windows: ffmpeg.exe, Mac/Linux: ffmpeg
    for name in ["ffmpeg.exe", "ffmpeg"]:
        bundled = os.path.join(base, name)
        if os.path.isfile(bundled):
            return bundled

    # 2. 시스템 PATH
    path = shutil.which("ffmpeg")
    if path:
        return path

    # 3. macOS Homebrew 기본 경로
    for p in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.isfile(p):
            return p

    return None


class VideoExporter(QThread):
    """백그라운드 스레드에서 슬라이드 PNG 생성 → ffmpeg MP4 인코딩"""

    # 시그널
    progress = pyqtSignal(int, int, str)   # (현재, 전체, 상태 메시지)
    finished_ok = pyqtSignal(str)          # 출력 파일 경로
    error = pyqtSignal(str)                # 에러 메시지

    def __init__(
        self,
        verses: list[Verse],
        settings: SlideSettings,
        output_path: str,
        ffmpeg_path: str | None = None,
    ):
        super().__init__()
        self.verses = verses
        self.settings = settings
        self.output_path = output_path
        self.ffmpeg_path = ffmpeg_path or find_ffmpeg()
        self._cancelled = False

    def cancel(self):
        """영상 생성 취소"""
        self._cancelled = True

    def run(self):
        if not self.ffmpeg_path:
            self.error.emit(
                "영상 생성 도구(ffmpeg)를 찾을 수 없습니다.\n"
                "설치 방법:\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html"
            )
            return

        tmpdir = None
        try:
            tmpdir = tempfile.mkdtemp(prefix="bible_video_")
            renderer = SlideRenderer()
            total = len(self.verses) + 1  # +1 타이틀 슬라이드

            # 1. 타이틀 슬라이드 렌더링
            self.progress.emit(0, total, "타이틀 슬라이드 생성 중...")
            title_img = renderer.render_title(self.settings.header_text, self.settings)
            title_img.save(os.path.join(tmpdir, "slide_0000.png"), "PNG")

            if self._cancelled:
                return

            # 2. 각 절 슬라이드 렌더링
            for i, verse in enumerate(self.verses):
                if self._cancelled:
                    return
                self.progress.emit(i + 1, total, f"슬라이드 생성 중... ({i+1}/{len(self.verses)})")
                img = renderer.render(verse, self.settings)
                img.save(os.path.join(tmpdir, f"slide_{i+1:04d}.png"), "PNG")

            if self._cancelled:
                return

            # 3. concat 파일 생성
            self.progress.emit(total, total, "영상 인코딩 중...")
            concat_path = os.path.join(tmpdir, "concat.txt")
            with open(concat_path, "w", encoding="utf-8") as f:
                # 타이틀
                f.write(f"file 'slide_0000.png'\n")
                f.write(f"duration {self.settings.title_duration}\n")
                # 각 절
                for i, verse in enumerate(self.verses):
                    f.write(f"file 'slide_{i+1:04d}.png'\n")
                    duration = self.settings.calculate_duration(verse)
                    f.write(f"duration {duration}\n")
                # ffmpeg concat 마지막 프레임 유지를 위해 마지막 파일 반복
                last_idx = len(self.verses)
                f.write(f"file 'slide_{last_idx:04d}.png'\n")

            # 4. ffmpeg 실행
            cmd = [
                self.ffmpeg_path, "-y",
                "-f", "concat", "-safe", "0",
                "-i", concat_path,
                "-fps_mode", "vfr",
                "-pix_fmt", "yuv420p",
                "-vf", f"fps={self.settings.fps}",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "20",
            ]

            # 배경음악 처리
            if self.settings.bgm_path and os.path.isfile(self.settings.bgm_path):
                cmd.extend([
                    "-i", self.settings.bgm_path,
                    "-filter_complex",
                    f"[1:a]volume={self.settings.bgm_volume}[bgm]",
                    "-map", "0:v", "-map", "[bgm]",
                    "-shortest",
                    "-c:a", "aac", "-b:a", "128k",
                ])

            cmd.append(self.output_path)

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )

            if self._cancelled:
                return

            if proc.returncode != 0:
                self.error.emit(f"ffmpeg 오류:\n{proc.stderr[-500:]}")
            else:
                self.finished_ok.emit(self.output_path)

        except Exception as e:
            self.error.emit(f"영상 생성 중 오류가 발생했습니다:\n{e}")
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
