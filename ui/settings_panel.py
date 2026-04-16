# -*- coding: utf-8 -*-
"""설정 패널 — QTabWidget으로 카테고리별 설정 UI"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QPushButton, QLineEdit, QSlider,
    QColorDialog, QFileDialog, QGroupBox, QFormLayout,
    QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFontDatabase
from models.settings import SlideSettings, ColumnConfig


class ColorButton(QPushButton):
    """색상 선택 버튼 — 클릭하면 QColorDialog 표시"""
    color_changed = pyqtSignal(str)

    def __init__(self, color: str = "#FFFFFF", parent=None):
        super().__init__(parent)
        self._color = color
        self._update_style()
        self.setFixedSize(60, 28)
        self.clicked.connect(self._pick_color)

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        self._color = value
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(
            f"background-color: {self._color}; border: 1px solid #555; border-radius: 3px;"
        )

    def _pick_color(self):
        c = QColorDialog.getColor(QColor(self._color), self, "색상 선택")
        if c.isValid():
            self._color = c.name()
            self._update_style()
            self.color_changed.emit(self._color)


class SettingsPanel(QWidget):
    """설정 패널 — 모든 슬라이드 설정을 탭으로 구성"""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._blocking_signals = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._tabs.addTab(self._create_font_tab(), "폰트")
        self._tabs.addTab(self._create_color_tab(), "색상")
        self._tabs.addTab(self._create_layout_tab(), "레이아웃")
        self._tabs.addTab(self._create_background_tab(), "배경")
        self._tabs.addTab(self._create_header_tab(), "헤더")
        self._tabs.addTab(self._create_video_tab(), "영상")

    def _emit_changed(self, *args):
        if not self._blocking_signals:
            self.settings_changed.emit()

    # === 폰트 탭 ===

    def _create_font_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QVBoxLayout(widget)

        fonts = sorted(QFontDatabase.families())

        # 왼쪽 컬럼 폰트
        left_group = QGroupBox("왼쪽 컬럼 (외국어)")
        left_form = QFormLayout()

        self._left_font = QComboBox()
        self._left_font.addItems(fonts)
        self._left_font.setEditable(True)
        self._left_font.currentTextChanged.connect(self._emit_changed)
        left_form.addRow("폰트:", self._left_font)

        self._left_size = QSpinBox()
        self._left_size.setRange(20, 120)
        self._left_size.setValue(48)
        self._left_size.valueChanged.connect(self._emit_changed)
        left_form.addRow("크기 (px):", self._left_size)

        self._left_weight = QComboBox()
        self._left_weight.addItems(["Light (300)", "Regular (400)", "Bold (700)"])
        self._left_weight.setCurrentIndex(1)
        self._left_weight.currentIndexChanged.connect(self._emit_changed)
        left_form.addRow("굵기:", self._left_weight)

        self._left_spacing = QDoubleSpinBox()
        self._left_spacing.setRange(-5.0, 20.0)
        self._left_spacing.setValue(0.0)
        self._left_spacing.setSingleStep(0.5)
        self._left_spacing.valueChanged.connect(self._emit_changed)
        left_form.addRow("자간 (px):", self._left_spacing)

        self._left_line_spacing = QDoubleSpinBox()
        self._left_line_spacing.setRange(1.0, 2.5)
        self._left_line_spacing.setValue(1.4)
        self._left_line_spacing.setSingleStep(0.1)
        self._left_line_spacing.valueChanged.connect(self._emit_changed)
        left_form.addRow("행간 (배수):", self._left_line_spacing)

        left_group.setLayout(left_form)
        form.addWidget(left_group)

        # 오른쪽 컬럼 폰트
        right_group = QGroupBox("오른쪽 컬럼 (한국어 등)")
        right_form = QFormLayout()

        self._right_font = QComboBox()
        self._right_font.addItems(fonts)
        self._right_font.setEditable(True)
        self._right_font.currentTextChanged.connect(self._emit_changed)
        right_form.addRow("폰트:", self._right_font)

        self._right_size = QSpinBox()
        self._right_size.setRange(20, 120)
        self._right_size.setValue(48)
        self._right_size.valueChanged.connect(self._emit_changed)
        right_form.addRow("크기 (px):", self._right_size)

        self._right_weight = QComboBox()
        self._right_weight.addItems(["Light (300)", "Regular (400)", "Bold (700)"])
        self._right_weight.setCurrentIndex(1)
        self._right_weight.currentIndexChanged.connect(self._emit_changed)
        right_form.addRow("굵기:", self._right_weight)

        self._right_spacing = QDoubleSpinBox()
        self._right_spacing.setRange(-5.0, 20.0)
        self._right_spacing.setValue(0.0)
        self._right_spacing.setSingleStep(0.5)
        self._right_spacing.valueChanged.connect(self._emit_changed)
        right_form.addRow("자간 (px):", self._right_spacing)

        self._right_line_spacing = QDoubleSpinBox()
        self._right_line_spacing.setRange(1.0, 2.5)
        self._right_line_spacing.setValue(1.4)
        self._right_line_spacing.setSingleStep(0.1)
        self._right_line_spacing.valueChanged.connect(self._emit_changed)
        right_form.addRow("행간 (배수):", self._right_line_spacing)

        right_group.setLayout(right_form)
        form.addWidget(right_group)

        form.addStretch()
        scroll.setWidget(widget)
        return scroll

    # === 색상 탭 ===

    def _create_color_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QFormLayout(widget)

        self._bg_color_btn = ColorButton("#0A0E1A")
        self._bg_color_btn.color_changed.connect(self._emit_changed)
        form.addRow("배경 색상:", self._bg_color_btn)

        self._left_text_color = ColorButton("#F0E6D2")
        self._left_text_color.color_changed.connect(self._emit_changed)
        form.addRow("왼쪽 텍스트:", self._left_text_color)

        self._right_text_color = ColorButton("#E6D7C3")
        self._right_text_color.color_changed.connect(self._emit_changed)
        form.addRow("오른쪽 텍스트:", self._right_text_color)

        self._verse_num_color = ColorButton("#C83C3C")
        self._verse_num_color.color_changed.connect(self._emit_changed)
        form.addRow("절 번호:", self._verse_num_color)

        self._header_color_btn = ColorButton("#D2B98C")
        self._header_color_btn.color_changed.connect(self._emit_changed)
        form.addRow("헤더:", self._header_color_btn)

        self._divider_color_btn = ColorButton("#504B41")
        self._divider_color_btn.color_changed.connect(self._emit_changed)
        form.addRow("구분선:", self._divider_color_btn)

        self._left_label_color = ColorButton("#8C826E")
        self._left_label_color.color_changed.connect(self._emit_changed)
        form.addRow("왼쪽 라벨:", self._left_label_color)

        self._right_label_color = ColorButton("#8C826E")
        self._right_label_color.color_changed.connect(self._emit_changed)
        form.addRow("오른쪽 라벨:", self._right_label_color)

        scroll.setWidget(widget)
        return scroll

    # === 레이아웃 탭 ===

    def _create_layout_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QFormLayout(widget)

        # 해상도
        self._resolution = QComboBox()
        self._resolution.addItems(["1920 x 1080", "2560 x 1440", "3840 x 2160"])
        self._resolution.currentIndexChanged.connect(self._emit_changed)
        form.addRow("해상도:", self._resolution)

        # 컬럼 패딩
        self._col_padding = QSpinBox()
        self._col_padding.setRange(20, 300)
        self._col_padding.setValue(90)
        self._col_padding.valueChanged.connect(self._emit_changed)
        form.addRow("좌우 여백 (px):", self._col_padding)

        # 컬럼 간격
        self._col_gap = QSpinBox()
        self._col_gap.setRange(10, 200)
        self._col_gap.setValue(60)
        self._col_gap.valueChanged.connect(self._emit_changed)
        form.addRow("컬럼 간격 (px):", self._col_gap)

        # 수직 구분선
        self._divider_visible = QCheckBox("수직 구분선 표시")
        self._divider_visible.setChecked(True)
        self._divider_visible.stateChanged.connect(self._emit_changed)
        form.addRow(self._divider_visible)

        self._divider_thickness = QSpinBox()
        self._divider_thickness.setRange(1, 5)
        self._divider_thickness.setValue(1)
        self._divider_thickness.valueChanged.connect(self._emit_changed)
        form.addRow("구분선 두께:", self._divider_thickness)

        # 절 번호 크기
        self._verse_num_size = QSpinBox()
        self._verse_num_size.setRange(20, 150)
        self._verse_num_size.setValue(76)
        self._verse_num_size.valueChanged.connect(self._emit_changed)
        form.addRow("절 번호 크기 (px):", self._verse_num_size)

        # 절 번호 위치
        self._verse_num_pos = QComboBox()
        self._verse_num_pos.addItems(["center", "left", "right"])
        self._verse_num_pos.currentIndexChanged.connect(self._emit_changed)
        form.addRow("절 번호 위치:", self._verse_num_pos)

        # 텍스트 수직 정렬
        self._left_valign = QComboBox()
        self._left_valign.addItems(["center", "top", "bottom"])
        self._left_valign.currentIndexChanged.connect(self._emit_changed)
        form.addRow("왼쪽 수직 정렬:", self._left_valign)

        self._right_valign = QComboBox()
        self._right_valign.addItems(["center", "top", "bottom"])
        self._right_valign.currentIndexChanged.connect(self._emit_changed)
        form.addRow("오른쪽 수직 정렬:", self._right_valign)

        scroll.setWidget(widget)
        return scroll

    # === 배경 탭 ===

    def _create_background_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QFormLayout(widget)

        self._bg_mode = QComboBox()
        self._bg_mode.addItems([
            "기본 (다크 네이비)", "단색", "그라디언트", "이미지"
        ])
        self._bg_mode.currentIndexChanged.connect(self._emit_changed)
        form.addRow("배경 모드:", self._bg_mode)

        self._bg_grad_start = ColorButton("#0A0E1A")
        self._bg_grad_start.color_changed.connect(self._emit_changed)
        form.addRow("그라디언트 시작:", self._bg_grad_start)

        self._bg_grad_end = ColorButton("#1E3A5F")
        self._bg_grad_end.color_changed.connect(self._emit_changed)
        form.addRow("그라디언트 끝:", self._bg_grad_end)

        # 배경 이미지
        img_layout = QHBoxLayout()
        self._bg_image_path = QLineEdit()
        self._bg_image_path.setPlaceholderText("이미지 파일 경로")
        self._bg_image_path.textChanged.connect(self._emit_changed)
        img_layout.addWidget(self._bg_image_path)
        browse_btn = QPushButton("찾아보기")
        browse_btn.clicked.connect(self._browse_bg_image)
        img_layout.addWidget(browse_btn)
        form.addRow("배경 이미지:", img_layout)

        self._bg_opacity = QDoubleSpinBox()
        self._bg_opacity.setRange(0.0, 1.0)
        self._bg_opacity.setValue(0.3)
        self._bg_opacity.setSingleStep(0.1)
        self._bg_opacity.valueChanged.connect(self._emit_changed)
        form.addRow("이미지 밝기:", self._bg_opacity)

        scroll.setWidget(widget)
        return scroll

    # === 헤더 탭 ===

    def _create_header_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QFormLayout(widget)

        self._header_visible = QCheckBox("헤더 표시")
        self._header_visible.setChecked(True)
        self._header_visible.stateChanged.connect(self._emit_changed)
        form.addRow(self._header_visible)

        self._header_text = QLineEdit("MWANZO / 창세기")
        self._header_text.textChanged.connect(self._emit_changed)
        form.addRow("헤더 텍스트:", self._header_text)

        self._header_size = QSpinBox()
        self._header_size.setRange(12, 60)
        self._header_size.setValue(28)
        self._header_size.valueChanged.connect(self._emit_changed)
        form.addRow("헤더 크기 (px):", self._header_size)

        # 절 번호 아래 구분선
        self._verse_divider = QCheckBox("절 번호 아래 구분선")
        self._verse_divider.setChecked(True)
        self._verse_divider.stateChanged.connect(self._emit_changed)
        form.addRow(self._verse_divider)

        # 언어 라벨
        label_group = QGroupBox("언어 라벨")
        label_form = QFormLayout()

        self._left_label_visible = QCheckBox("왼쪽 라벨 표시")
        self._left_label_visible.setChecked(True)
        self._left_label_visible.stateChanged.connect(self._emit_changed)
        label_form.addRow(self._left_label_visible)

        self._left_label_text = QLineEdit("KISWAHILI")
        self._left_label_text.textChanged.connect(self._emit_changed)
        label_form.addRow("왼쪽 라벨:", self._left_label_text)

        self._right_label_visible = QCheckBox("오른쪽 라벨 표시")
        self._right_label_visible.setChecked(True)
        self._right_label_visible.stateChanged.connect(self._emit_changed)
        label_form.addRow(self._right_label_visible)

        self._right_label_text = QLineEdit("한국어")
        self._right_label_text.textChanged.connect(self._emit_changed)
        label_form.addRow("오른쪽 라벨:", self._right_label_text)

        self._label_size = QSpinBox()
        self._label_size.setRange(10, 40)
        self._label_size.setValue(24)
        self._label_size.valueChanged.connect(self._emit_changed)
        label_form.addRow("라벨 크기 (px):", self._label_size)

        label_group.setLayout(label_form)
        form.addRow(label_group)

        scroll.setWidget(widget)
        return scroll

    # === 영상 탭 ===

    def _create_video_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        form = QFormLayout(widget)

        # 시간 모드
        self._duration_mode = QComboBox()
        self._duration_mode.addItems(["자동 (단어 수 기반)", "고정 시간", "수동 (절별 개별)"])
        self._duration_mode.currentIndexChanged.connect(self._emit_changed)
        form.addRow("절 표시 시간:", self._duration_mode)

        self._fixed_duration = QDoubleSpinBox()
        self._fixed_duration.setRange(1.0, 60.0)
        self._fixed_duration.setValue(5.0)
        self._fixed_duration.setSuffix(" 초")
        self._fixed_duration.valueChanged.connect(self._emit_changed)
        form.addRow("고정 시간:", self._fixed_duration)

        self._title_duration = QDoubleSpinBox()
        self._title_duration.setRange(1.0, 20.0)
        self._title_duration.setValue(4.0)
        self._title_duration.setSuffix(" 초")
        self._title_duration.valueChanged.connect(self._emit_changed)
        form.addRow("타이틀 시간:", self._title_duration)

        # 페이드
        self._fade_enabled = QCheckBox("페이드 전환 효과")
        self._fade_enabled.stateChanged.connect(self._emit_changed)
        form.addRow(self._fade_enabled)

        self._fade_duration = QDoubleSpinBox()
        self._fade_duration.setRange(0.0, 2.0)
        self._fade_duration.setValue(0.5)
        self._fade_duration.setSuffix(" 초")
        self._fade_duration.valueChanged.connect(self._emit_changed)
        form.addRow("전환 시간:", self._fade_duration)

        # FPS
        self._fps = QComboBox()
        self._fps.addItems(["24", "30", "60"])
        self._fps.setCurrentIndex(1)
        self._fps.currentIndexChanged.connect(self._emit_changed)
        form.addRow("FPS:", self._fps)

        # 배경음악
        bgm_layout = QHBoxLayout()
        self._bgm_path = QLineEdit()
        self._bgm_path.setPlaceholderText("배경음악 파일 (선택)")
        self._bgm_path.textChanged.connect(self._emit_changed)
        bgm_layout.addWidget(self._bgm_path)
        bgm_btn = QPushButton("찾아보기")
        bgm_btn.clicked.connect(self._browse_bgm)
        bgm_layout.addWidget(bgm_btn)
        form.addRow("배경음악:", bgm_layout)

        self._bgm_volume = QDoubleSpinBox()
        self._bgm_volume.setRange(0.0, 1.0)
        self._bgm_volume.setValue(0.3)
        self._bgm_volume.setSingleStep(0.1)
        self._bgm_volume.valueChanged.connect(self._emit_changed)
        form.addRow("음악 볼륨:", self._bgm_volume)

        scroll.setWidget(widget)
        return scroll

    # === 파일 브라우저 ===

    def _browse_bg_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "배경 이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self._bg_image_path.setText(path)

    def _browse_bgm(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "배경음악 선택", "",
            "오디오 파일 (*.mp3 *.wav *.m4a)"
        )
        if path:
            self._bgm_path.setText(path)

    # === 설정 읽기/쓰기 ===

    def get_settings(self) -> SlideSettings:
        """현재 위젯 값들로 SlideSettings 생성"""
        # 해상도 파싱
        res_text = self._resolution.currentText()
        parts = res_text.split(" x ")
        width = int(parts[0].strip()) if len(parts) == 2 else 1920
        height = int(parts[1].strip()) if len(parts) == 2 else 1080

        # 폰트 굵기 파싱
        weight_map = {0: 300, 1: 400, 2: 700}

        # 배경 모드 파싱
        bg_modes = ["default_dark", "solid", "gradient", "image"]
        bg_mode = bg_modes[self._bg_mode.currentIndex()]

        # 시간 모드 파싱
        dur_modes = ["auto", "fixed", "manual"]
        dur_mode = dur_modes[self._duration_mode.currentIndex()]

        # FPS 파싱
        fps = int(self._fps.currentText())

        return SlideSettings(
            width=width,
            height=height,
            bg_mode=bg_mode,
            bg_color=self._bg_color_btn.color,
            bg_gradient_start=self._bg_grad_start.color,
            bg_gradient_end=self._bg_grad_end.color,
            bg_image_path=self._bg_image_path.text() or None,
            bg_image_opacity=self._bg_opacity.value(),
            left_column=ColumnConfig(
                label=self._left_label_text.text(),
                font_family=self._left_font.currentText(),
                font_size=self._left_size.value(),
                font_weight=weight_map.get(self._left_weight.currentIndex(), 400),
                letter_spacing=self._left_spacing.value(),
                line_spacing=self._left_line_spacing.value(),
                text_color=self._left_text_color.color,
                label_visible=self._left_label_visible.isChecked(),
                label_font_size=self._label_size.value(),
                label_color=self._left_label_color.color,
                text_align="left",
                vertical_align=self._left_valign.currentText(),
            ),
            right_column=ColumnConfig(
                label=self._right_label_text.text(),
                font_family=self._right_font.currentText(),
                font_size=self._right_size.value(),
                font_weight=weight_map.get(self._right_weight.currentIndex(), 400),
                letter_spacing=self._right_spacing.value(),
                line_spacing=self._right_line_spacing.value(),
                text_color=self._right_text_color.color,
                label_visible=self._right_label_visible.isChecked(),
                label_font_size=self._label_size.value(),
                label_color=self._right_label_color.color,
                text_align="left",
                vertical_align=self._right_valign.currentText(),
            ),
            column_padding=self._col_padding.value(),
            column_gap=self._col_gap.value(),
            verse_number_color=self._verse_num_color.color,
            verse_number_size=self._verse_num_size.value(),
            verse_number_position=self._verse_num_pos.currentText(),
            header_text=self._header_text.text(),
            header_visible=self._header_visible.isChecked(),
            header_color=self._header_color_btn.color,
            header_size=self._header_size.value(),
            divider_visible=self._divider_visible.isChecked(),
            divider_color=self._divider_color_btn.color,
            divider_thickness=self._divider_thickness.value(),
            verse_divider_visible=self._verse_divider.isChecked(),
            duration_mode=dur_mode,
            fixed_duration=self._fixed_duration.value(),
            title_duration=self._title_duration.value(),
            fade_enabled=self._fade_enabled.isChecked(),
            fade_duration=self._fade_duration.value(),
            fps=fps,
            bgm_path=self._bgm_path.text() or None,
            bgm_volume=self._bgm_volume.value(),
        )

    def set_settings(self, s: SlideSettings):
        """SlideSettings 값을 위젯에 반영 (시그널 차단)"""
        self._blocking_signals = True
        try:
            # 해상도
            res_map = {"1920x1080": 0, "2560x1440": 1, "3840x2160": 2}
            res_key = f"{s.width}x{s.height}"
            self._resolution.setCurrentIndex(res_map.get(res_key, 0))

            # 왼쪽 컬럼
            idx = self._left_font.findText(s.left_column.font_family)
            if idx >= 0:
                self._left_font.setCurrentIndex(idx)
            self._left_size.setValue(s.left_column.font_size)
            weight_idx = {300: 0, 400: 1, 700: 2}.get(s.left_column.font_weight, 1)
            self._left_weight.setCurrentIndex(weight_idx)
            self._left_spacing.setValue(s.left_column.letter_spacing)
            self._left_line_spacing.setValue(s.left_column.line_spacing)
            self._left_text_color.color = s.left_column.text_color
            self._left_label_visible.setChecked(s.left_column.label_visible)
            self._left_label_color.color = s.left_column.label_color

            # 오른쪽 컬럼
            idx = self._right_font.findText(s.right_column.font_family)
            if idx >= 0:
                self._right_font.setCurrentIndex(idx)
            self._right_size.setValue(s.right_column.font_size)
            weight_idx = {300: 0, 400: 1, 700: 2}.get(s.right_column.font_weight, 1)
            self._right_weight.setCurrentIndex(weight_idx)
            self._right_spacing.setValue(s.right_column.letter_spacing)
            self._right_line_spacing.setValue(s.right_column.line_spacing)
            self._right_text_color.color = s.right_column.text_color
            self._right_label_visible.setChecked(s.right_column.label_visible)
            self._right_label_color.color = s.right_column.label_color

            # 색상
            self._bg_color_btn.color = s.bg_color
            self._verse_num_color.color = s.verse_number_color
            self._header_color_btn.color = s.header_color
            self._divider_color_btn.color = s.divider_color

            # 레이아웃
            self._col_padding.setValue(s.column_padding)
            self._col_gap.setValue(s.column_gap)
            self._divider_visible.setChecked(s.divider_visible)
            self._divider_thickness.setValue(s.divider_thickness)
            self._verse_num_size.setValue(s.verse_number_size)
            pos_idx = ["center", "left", "right"].index(s.verse_number_position)
            self._verse_num_pos.setCurrentIndex(pos_idx)

            # 배경
            bg_idx = ["default_dark", "solid", "gradient", "image"].index(s.bg_mode)
            self._bg_mode.setCurrentIndex(bg_idx)
            self._bg_grad_start.color = s.bg_gradient_start
            self._bg_grad_end.color = s.bg_gradient_end
            self._bg_image_path.setText(s.bg_image_path or "")
            self._bg_opacity.setValue(s.bg_image_opacity)

            # 헤더
            self._header_visible.setChecked(s.header_visible)
            self._header_text.setText(s.header_text)
            self._header_size.setValue(s.header_size)
            self._verse_divider.setChecked(s.verse_divider_visible)

            # 라벨
            self._left_label_text.setText(s.left_column.label)
            self._right_label_text.setText(s.right_column.label)
            self._label_size.setValue(s.left_column.label_font_size)

            # 수직 정렬
            valign_idx = ["center", "top", "bottom"]
            self._left_valign.setCurrentIndex(valign_idx.index(s.left_column.vertical_align))
            self._right_valign.setCurrentIndex(valign_idx.index(s.right_column.vertical_align))

            # 영상
            dur_idx = ["auto", "fixed", "manual"].index(s.duration_mode)
            self._duration_mode.setCurrentIndex(dur_idx)
            self._fixed_duration.setValue(s.fixed_duration)
            self._title_duration.setValue(s.title_duration)
            self._fade_enabled.setChecked(s.fade_enabled)
            self._fade_duration.setValue(s.fade_duration)
            fps_idx = ["24", "30", "60"].index(str(s.fps))
            self._fps.setCurrentIndex(fps_idx)
            self._bgm_path.setText(s.bgm_path or "")
            self._bgm_volume.setValue(s.bgm_volume)
        finally:
            self._blocking_signals = False
