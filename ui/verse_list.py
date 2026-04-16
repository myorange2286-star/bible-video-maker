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

    # 시그널: 선택된 절 인덱스 변경
    current_verse_changed = pyqtSignal(int)
    # 시그널: 파일 로드 요청
    file_load_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._verses: list[Verse] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 상단: 파일 열기 버튼
        btn_layout = QHBoxLayout()
        self._open_btn = QPushButton("텍스트 파일 열기")
        self._open_btn.setMinimumHeight(36)
        self._open_btn.clicked.connect(self._on_open_clicked)
        btn_layout.addWidget(self._open_btn)
        layout.addLayout(btn_layout)

        # 파일명 라벨
        self._file_label = QLabel("파일을 선택해주세요")
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
            # 왼쪽 텍스트 앞부분만 미리보기로 표시
            preview = v.left_text[:30] + ("..." if len(v.left_text) > 30 else "")
            item = QListWidgetItem(f"{v.number}. {preview}")
            self._list.addItem(item)

        self._count_label.setText(f"총 {len(verses)}절")
        if filename:
            self._file_label.setText(filename)

        # 첫 번째 절 자동 선택
        if verses:
            self._list.setCurrentRow(0)

    def current_index(self) -> int:
        """현재 선택된 절 인덱스 (-1이면 선택 없음)"""
        return self._list.currentRow()

    def _on_row_changed(self, row: int):
        if row >= 0:
            self.current_verse_changed.emit(row)

    def _on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "텍스트 파일 열기",
            "",
            "텍스트 파일 (*.txt);;모든 파일 (*)"
        )
        if path:
            self.file_load_requested.emit(path)
