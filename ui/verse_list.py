# -*- coding: utf-8 -*-
"""절 리스트 위젯 — 좌측 패널"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QFileDialog, QLabel, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from models.verse import Verse


class VerseListWidget(QWidget):
    """절 목록 표시 및 선택. 파일 열기 버튼 포함."""

    # 시그널
    current_verse_changed = pyqtSignal(int)
    file_load_requested = pyqtSignal(str)           # 단일 파일 (파이프 형식)
    merge_load_requested = pyqtSignal(str, str)     # 두 파일 합치기 (왼쪽, 오른쪽)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._verses: list[Verse] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 파일 열기 버튼들
        self._open_btn = QPushButton("파일 1개 열기")
        self._open_btn.setToolTip("이미 두 언어가 합쳐진 파일\n(파이프/탭 구분 또는 한 언어만)")
        self._open_btn.setMinimumHeight(36)
        self._open_btn.clicked.connect(self._on_open_clicked)
        layout.addWidget(self._open_btn)

        self._merge_btn = QPushButton("두 파일 합치기 (왼쪽 + 오른쪽)")
        self._merge_btn.setToolTip("외국어 파일과 한국어 파일을 각각 선택하면\n자동으로 좌우 매칭합니다")
        self._merge_btn.setMinimumHeight(36)
        self._merge_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        self._merge_btn.clicked.connect(self._on_merge_clicked)
        layout.addWidget(self._merge_btn)

        # 파일명 라벨
        self._file_label = QLabel("파일을 선택해주세요")
        self._file_label.setWordWrap(True)
        self._file_label.setStyleSheet("color: #888; padding: 4px;")
        layout.addWidget(self._file_label)

        # 절 리스트
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_row_changed)
        layout.addWidget(self._list)

        # 절 수 표시
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("color: #888; padding: 2px;")
        layout.addWidget(self._count_label)

    def set_verses(self, verses: list[Verse], filename: str = ""):
        """절 리스트 갱신"""
        self._verses = verses
        self._list.clear()

        for v in verses:
            preview = v.left_text[:25] + ("..." if len(v.left_text) > 25 else "")
            if v.right_text:
                preview += " | " + v.right_text[:15] + ("..." if len(v.right_text) > 15 else "")
            item = QListWidgetItem(f"{v.number}. {preview}")
            self._list.addItem(item)

        self._count_label.setText(f"총 {len(verses)}절")
        if filename:
            self._file_label.setText(filename)

        if verses:
            self._list.setCurrentRow(0)

    def current_index(self) -> int:
        return self._list.currentRow()

    def _on_row_changed(self, row: int):
        if row >= 0:
            self.current_verse_changed.emit(row)

    def _on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "텍스트 파일 열기", "",
            "텍스트 파일 (*.txt);;모든 파일 (*)"
        )
        if path:
            self.file_load_requested.emit(path)

    def _on_merge_clicked(self):
        """두 파일 합치기: 왼쪽(외국어) → 오른쪽(한국어) 순서로 선택"""
        left_path, _ = QFileDialog.getOpenFileName(
            self, "① 왼쪽 언어 파일 선택 (예: 외국어)", "",
            "텍스트 파일 (*.txt);;모든 파일 (*)"
        )
        if not left_path:
            return

        right_path, _ = QFileDialog.getOpenFileName(
            self, "② 오른쪽 언어 파일 선택 (예: 한국어)", "",
            "텍스트 파일 (*.txt);;모든 파일 (*)"
        )
        if not right_path:
            return

        self.merge_load_requested.emit(left_path, right_path)
