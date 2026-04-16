# -*- coding: utf-8 -*-
"""미리보기 위젯 — QImage를 스케일링하여 표시"""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap


class PreviewWidget(QWidget):
    """슬라이드 미리보기 표시. QImage를 받아 위젯 크기에 맞게 스케일링."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_image: QImage | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 미리보기 라벨
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: #1a1a2e; border: 1px solid #333;")
        self._label.setMinimumSize(400, 225)
        layout.addWidget(self._label, 1)

        # PNG 내보내기 버튼
        self._export_btn = QPushButton("PNG로 내보내기")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._on_export)
        layout.addWidget(self._export_btn)

    def set_image(self, image: QImage):
        """QImage를 미리보기에 표시"""
        self._current_image = image
        self._export_btn.setEnabled(True)
        self._update_display()

    def clear(self):
        """미리보기 초기화"""
        self._current_image = None
        self._label.clear()
        self._label.setText("미리보기")
        self._export_btn.setEnabled(False)

    def resizeEvent(self, event):
        """위젯 크기 변경 시 이미지 리스케일"""
        super().resizeEvent(event)
        if self._current_image:
            self._update_display()

    def _update_display(self):
        """현재 이미지를 라벨 크기에 맞게 표시"""
        if not self._current_image:
            return
        pixmap = QPixmap.fromImage(self._current_image)
        scaled = pixmap.scaled(
            self._label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._label.setPixmap(scaled)

    def _on_export(self):
        """현재 슬라이드를 PNG로 내보내기"""
        if not self._current_image:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "PNG로 내보내기",
            "slide.png",
            "PNG 이미지 (*.png)"
        )
        if path:
            self._current_image.save(path, "PNG")
