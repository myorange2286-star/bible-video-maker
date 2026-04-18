# -*- coding: utf-8 -*-
"""메인 윈도우 — 3패널 레이아웃, 시그널/슬롯 오케스트레이션"""
from __future__ import annotations
import os
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QMessageBox, QStatusBar,
    QToolBar, QFileDialog, QProgressDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from models.verse import Verse
from models.settings import SlideSettings
from parsing.verse_parser import parse_verses, merge_two_files
from rendering.slide_renderer import SlideRenderer
from rendering.video_exporter import VideoExporter, find_ffmpeg
from ui.verse_list import VerseListWidget
from ui.preview_widget import PreviewWidget
from ui.settings_panel import SettingsPanel


class MainWindow(QMainWindow):
    """Bible Video Maker 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bible Video Maker")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)

        self._verses: list[Verse] = []
        self._renderer = SlideRenderer()
        self._settings = SlideSettings()

        # 디바운스 타이머 (300ms)
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._do_preview_update)

        self._setup_ui()
        self._setup_toolbar()
        self._connect_signals()

        # 상태 바
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("파일을 열어 시작하세요")

    def _setup_ui(self):
        """3패널 레이아웃 구성"""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 좌측: 절 리스트
        self._verse_list = VerseListWidget()
        splitter.addWidget(self._verse_list)

        # 중앙: 미리보기
        self._preview = PreviewWidget()
        splitter.addWidget(self._preview)

        # 우측: 설정 패널
        self._settings_panel = SettingsPanel()
        splitter.addWidget(self._settings_panel)

        # 패널 비율: 1:3:1.5
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 2)
        splitter.setSizes([250, 650, 400])

        self.setCentralWidget(splitter)

    def _setup_toolbar(self):
        """툴바 구성"""
        toolbar = QToolBar("메인 도구")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 파일 열기
        open_action = QAction("텍스트 열기", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # 프리셋 저장/불러오기
        save_preset_action = QAction("프리셋 저장", self)
        save_preset_action.setShortcut("Ctrl+S")
        save_preset_action.triggered.connect(self._on_save_preset)
        toolbar.addAction(save_preset_action)

        load_preset_action = QAction("프리셋 불러오기", self)
        load_preset_action.triggered.connect(self._on_load_preset)
        toolbar.addAction(load_preset_action)

        toolbar.addSeparator()

        # 영상 생성
        export_action = QAction("영상 생성 (MP4)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_video)
        toolbar.addAction(export_action)

        # PNG 일괄 내보내기
        export_png_action = QAction("이미지 내보내기 (PNG)", self)
        export_png_action.setShortcut("Ctrl+Shift+E")
        export_png_action.triggered.connect(self._on_export_png)
        toolbar.addAction(export_png_action)

    def _connect_signals(self):
        """시그널/슬롯 연결"""
        # 절 리스트에서 파일 로드 요청
        self._verse_list.file_load_requested.connect(self._load_file)
        # 두 파일 합치기 요청
        self._verse_list.merge_load_requested.connect(self._merge_files)
        # 절 선택 변경 → 즉시 미리보기
        self._verse_list.current_verse_changed.connect(self._on_verse_selected)
        # 설정 변경 → 디바운스 미리보기
        self._settings_panel.settings_changed.connect(self._schedule_preview_update)

    # === 파일 로드 ===

    def _on_open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "텍스트 파일 열기", "",
            "텍스트 파일 (*.txt);;모든 파일 (*)"
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        try:
            self._verses = parse_verses(path)
            filename = os.path.basename(path)
            self._verse_list.set_verses(self._verses, filename)
            self._status.showMessage(f"{filename} — {len(self._verses)}절 로드됨")
        except ValueError as e:
            QMessageBox.warning(self, "파일 오류", str(e))
        except FileNotFoundError:
            QMessageBox.warning(self, "파일 오류", f"파일을 찾을 수 없습니다:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일을 읽는 중 오류가 발생했습니다:\n{e}")

    def _merge_files(self, left_path: str, right_path: str):
        """두 파일을 합쳐서 로드"""
        try:
            self._verses = merge_two_files(left_path, right_path)
            left_name = os.path.basename(left_path)
            right_name = os.path.basename(right_path)
            label = f"왼쪽: {left_name}\n오른쪽: {right_name}"
            self._verse_list.set_verses(self._verses, label)
            self._status.showMessage(
                f"{left_name} + {right_name} — {len(self._verses)}절 합침 완료"
            )
        except ValueError as e:
            QMessageBox.warning(self, "파일 오류", str(e))
        except FileNotFoundError as e:
            QMessageBox.warning(self, "파일 오류", f"파일을 찾을 수 없습니다:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 합치기 중 오류가 발생했습니다:\n{e}")

    # === 미리보기 ===

    def _on_verse_selected(self, index: int):
        """절 선택 시 즉시 미리보기 (디바운스 없음)"""
        self._do_preview_update()

    def _schedule_preview_update(self):
        """설정 변경 시 디바운스 미리보기"""
        self._preview_timer.start()

    def _do_preview_update(self):
        """실제 미리보기 렌더링 실행"""
        idx = self._verse_list.current_index()
        if idx < 0 or idx >= len(self._verses):
            return

        self._settings = self._settings_panel.get_settings()
        verse = self._verses[idx]

        try:
            img = self._renderer.render(verse, self._settings)
            self._preview.set_image(img)
        except Exception as e:
            self._status.showMessage(f"렌더링 오류: {e}")

    # === 프리셋 ===

    def _on_save_preset(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "프리셋 저장", "preset.json",
            "JSON 파일 (*.json)"
        )
        if path:
            try:
                settings = self._settings_panel.get_settings()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(settings.to_json())
                self._status.showMessage(f"프리셋 저장됨: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "저장 오류", str(e))

    def _on_load_preset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "프리셋 불러오기", "",
            "JSON 파일 (*.json)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    settings = SlideSettings.from_json(f.read())
                self._settings_panel.set_settings(settings)
                self._settings = settings
                self._do_preview_update()
                self._status.showMessage(f"프리셋 로드됨: {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "불러오기 오류", str(e))

    # === 영상 생성 ===

    def _on_export_video(self):
        if not self._verses:
            QMessageBox.information(self, "안내", "먼저 텍스트 파일을 열어주세요.")
            return

        # ffmpeg 확인
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            QMessageBox.warning(
                self, "ffmpeg 미설치",
                "영상 생성 도구(ffmpeg)가 설치되어 있지 않습니다.\n\n"
                "설치 방법:\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: https://ffmpeg.org/download.html\n\n"
                "설치 후 다시 시도해주세요.",
                QMessageBox.StandardButton.Ok
            )
            return

        # 1. 모드 선택: 한 파일 / 절별 분리
        mode, ok = QInputDialog.getItem(
            self, "영상 출력 모드", "어떻게 저장할까요?",
            ["한 개 파일로 합치기", "절마다 별도 파일로 분리"],
            0, False,
        )
        if not ok:
            return
        per_verse = (mode == "절마다 별도 파일로 분리")

        self._settings = self._settings_panel.get_settings()

        if per_verse:
            # 2a. 접두사 입력
            prefix, ok = QInputDialog.getText(
                self, "파일명 접두사",
                "파일명 앞부분을 입력하세요 (예: 창세기 → 창세기_001.mp4)",
                text="verse",
            )
            if not ok or not prefix.strip():
                return
            prefix = prefix.strip()

            # 2b. 저장 폴더 선택
            folder = QFileDialog.getExistingDirectory(
                self, "저장 폴더 선택", os.path.expanduser("~/Desktop")
            )
            if not folder:
                return
            output_path = folder
        else:
            # 2. 단일 파일 저장 경로
            path, _ = QFileDialog.getSaveFileName(
                self, "영상 저장 위치", "output.mp4",
                "MP4 영상 (*.mp4)"
            )
            if not path:
                return
            output_path = path
            prefix = ""

        # 프로그레스 다이얼로그
        self._progress = QProgressDialog("영상 생성 준비 중...", "취소", 0, len(self._verses) + 1, self)
        self._progress.setWindowTitle("영상 생성")
        self._progress.setMinimumDuration(0)
        self._progress.setAutoClose(False)
        self._progress.setAutoReset(False)

        # VideoExporter 스레드
        self._exporter = VideoExporter(
            self._verses, self._settings, output_path, ffmpeg,
            per_verse=per_verse, filename_prefix=prefix,
        )
        self._exporter.progress.connect(self._on_export_progress)
        self._exporter.finished_ok.connect(self._on_export_done)
        self._exporter.error.connect(self._on_export_error)
        self._progress.canceled.connect(self._exporter.cancel)
        self._exporter.start()

    def _on_export_progress(self, current: int, total: int, message: str):
        self._progress.setMaximum(total)
        self._progress.setValue(current)
        self._progress.setLabelText(message)

    def _on_export_done(self, output_path: str):
        self._progress.close()
        if os.path.isdir(output_path):
            msg = f"절별 영상이 모두 생성되었습니다!\n\n저장 폴더:\n{output_path}"
        else:
            msg = f"영상이 생성되었습니다!\n\n{output_path}"
        QMessageBox.information(self, "완료", msg)
        self._status.showMessage(f"영상 생성 완료: {os.path.basename(output_path)}")

    def _on_export_error(self, error_msg: str):
        self._progress.close()
        QMessageBox.critical(self, "영상 생성 오류", error_msg)

    # === PNG 일괄 내보내기 ===

    def _on_export_png(self):
        if not self._verses:
            QMessageBox.information(self, "안내", "먼저 텍스트 파일을 열어주세요.")
            return

        # 1. 접두사 입력
        prefix, ok = QInputDialog.getText(
            self, "파일명 접두사",
            "파일명 앞부분을 입력하세요 (예: 창세기 → 창세기_001.png)",
            text="verse",
        )
        if not ok or not prefix.strip():
            return
        prefix = prefix.strip()

        # 2. 저장 폴더 선택
        folder = QFileDialog.getExistingDirectory(
            self, "PNG 저장 폴더 선택", os.path.expanduser("~/Desktop")
        )
        if not folder:
            return

        self._settings = self._settings_panel.get_settings()
        total = len(self._verses)

        progress = QProgressDialog("이미지 내보내는 중...", "취소", 0, total, self)
        progress.setWindowTitle("PNG 내보내기")
        progress.setMinimumDuration(0)

        digits = max(3, len(str(total)))
        saved = 0
        try:
            for i, verse in enumerate(self._verses):
                if progress.wasCanceled():
                    break
                progress.setValue(i)
                progress.setLabelText(f"{i+1}/{total} — 절 {verse.number} 렌더링 중...")
                img = self._renderer.render(verse, self._settings)
                filename = f"{prefix}_{str(verse.number).zfill(digits)}.png"
                img.save(os.path.join(folder, filename), "PNG")
                saved += 1
            progress.setValue(total)
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "PNG 내보내기 오류", f"오류 발생:\n{e}")
            return

        QMessageBox.information(
            self, "완료",
            f"이미지 {saved}개 저장 완료!\n\n저장 위치:\n{folder}"
        )
        self._status.showMessage(f"PNG {saved}개 저장됨: {folder}")

    # === 종료 확인 ===

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "종료 확인",
            "프로그램을 종료하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
