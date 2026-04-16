# -*- coding: utf-8 -*-
"""QPainter 기반 슬라이드 렌더러 — 미리보기와 영상 출력 모두 동일한 렌더링 경로 사용"""
from __future__ import annotations
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QImage, QPainter, QFont, QColor, QPen, QLinearGradient,
    QFontMetrics, QRadialGradient, QBrush, QPixmap, QFontDatabase
)
import os
from models.verse import Verse
from models.settings import SlideSettings, ColumnConfig


class SlideRenderer:
    """순수 함수형 렌더러: (Verse, SlideSettings) → QImage"""

    # 폰트 파일 로드 캐시: {경로: 폰트 패밀리 이름}
    _font_file_cache: dict[str, str] = {}

    def render(self, verse: Verse, settings: SlideSettings) -> QImage:
        """한 절의 슬라이드를 QImage로 렌더링"""
        w, h = settings.width, settings.height
        img = QImage(w, h, QImage.Format.Format_ARGB32)
        img.fill(QColor(settings.bg_color))

        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 1. 배경
        self._draw_background(p, w, h, settings)

        # 2. 헤더
        y_offset = self._draw_header(p, w, settings)

        # 3. 절 번호
        y_offset = self._draw_verse_number(p, w, verse.number, y_offset, settings)

        # 4. 수직 구분선
        if settings.divider_visible:
            self._draw_vertical_divider(p, w, h, y_offset, settings)

        # 5. 좌우 컬럼 텍스트
        col_padding = settings.column_padding
        col_gap = settings.column_gap
        col_width = (w - 2 * col_padding - col_gap) // 2

        # 왼쪽 컬럼 영역
        left_x = col_padding
        # 오른쪽 컬럼 영역
        right_x = col_padding + col_width + col_gap

        text_area_top = y_offset + 20
        text_area_bottom = h - 40

        self._draw_column_text(
            p, verse.left_text, settings.left_column,
            left_x, text_area_top, col_width, text_area_bottom
        )
        self._draw_column_text(
            p, verse.right_text, settings.right_column,
            right_x, text_area_top, col_width, text_area_bottom
        )

        # 6. 언어 라벨
        if settings.left_column.label_visible and settings.left_column.label:
            self._draw_label(p, settings.left_column, left_x, col_width, h)
        if settings.right_column.label_visible and settings.right_column.label:
            self._draw_label(p, settings.right_column, right_x, col_width, h)

        p.end()
        return img

    def render_title(self, title_text: str, settings: SlideSettings) -> QImage:
        """타이틀 슬라이드 렌더링"""
        w, h = settings.width, settings.height
        img = QImage(w, h, QImage.Format.Format_ARGB32)
        img.fill(QColor(settings.bg_color))

        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self._draw_background(p, w, h, settings)

        # 타이틀 텍스트를 화면 중앙에 표시
        font = QFont(settings.header_text and "Arial" or "Arial", 64)
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor(settings.header_color))

        rect = QRectF(0, 0, w, h)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, title_text)

        p.end()
        return img

    # === 내부 렌더링 메서드 ===

    def _draw_background(self, p: QPainter, w: int, h: int, s: SlideSettings):
        """배경 그리기 (4가지 모드)"""
        if s.bg_mode == "solid":
            p.fillRect(0, 0, w, h, QColor(s.bg_color))

        elif s.bg_mode == "gradient":
            gradient = QLinearGradient(0, 0, 0, h)
            gradient.setColorAt(0.0, QColor(s.bg_gradient_start))
            gradient.setColorAt(1.0, QColor(s.bg_gradient_end))
            p.fillRect(0, 0, w, h, QBrush(gradient))

        elif s.bg_mode == "image" and s.bg_image_path:
            pixmap = QPixmap(s.bg_image_path)
            if not pixmap.isNull():
                # 중앙 크롭으로 비율 맞추기
                scaled = pixmap.scaled(
                    w, h,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                x_off = (scaled.width() - w) // 2
                y_off = (scaled.height() - h) // 2
                cropped = scaled.copy(x_off, y_off, w, h)
                p.drawPixmap(0, 0, cropped)
                # 어둡게 오버레이
                overlay_alpha = int(255 * (1.0 - s.bg_image_opacity))
                p.fillRect(0, 0, w, h, QColor(0, 0, 0, overlay_alpha))

        else:  # default_dark — 다크 네이비 + 은은한 라디얼 그라디언트
            p.fillRect(0, 0, w, h, QColor(s.bg_color))
            # 좌상단 은은한 푸른 빛
            grad1 = QRadialGradient(QPointF(w * 0.2, h * 0.2), w * 0.5)
            grad1.setColorAt(0.0, QColor(30, 58, 95, 35))
            grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(0, 0, w, h, QBrush(grad1))
            # 우하단 은은한 빛
            grad2 = QRadialGradient(QPointF(w * 0.8, h * 0.8), w * 0.4)
            grad2.setColorAt(0.0, QColor(44, 62, 80, 30))
            grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.fillRect(0, 0, w, h, QBrush(grad2))

    def _draw_header(self, p: QPainter, w: int, s: SlideSettings) -> int:
        """상단 헤더 그리기. 반환값: 헤더 아래 y 좌표"""
        if not s.header_visible or not s.header_text:
            return 30

        font = self._make_font("", s.header_size, 400)
        p.setFont(font)
        p.setPen(QColor(s.header_color))

        fm = QFontMetrics(font)
        text_rect = QRectF(0, 20, w, fm.height() + 10)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, s.header_text)

        return int(text_rect.bottom()) + 10

    def _draw_verse_number(self, p: QPainter, w: int, number: int, y: int, s: SlideSettings) -> int:
        """절 번호 그리기. 반환값: 번호 영역 아래 y 좌표"""
        font = self._make_font("", s.verse_number_size, 700)
        p.setFont(font)
        p.setPen(QColor(s.verse_number_color))

        fm = QFontMetrics(font)
        num_text = str(number)
        text_rect = QRectF(0, y, w, fm.height() + 20)

        align = Qt.AlignmentFlag.AlignVCenter
        if s.verse_number_position == "center":
            align |= Qt.AlignmentFlag.AlignHCenter
        elif s.verse_number_position == "left":
            align |= Qt.AlignmentFlag.AlignLeft
        else:
            align |= Qt.AlignmentFlag.AlignRight

        p.drawText(text_rect, align, num_text)

        y_after = int(text_rect.bottom()) + 5

        # 절 번호 아래 구분선
        if s.verse_divider_visible:
            p.setPen(QPen(QColor(s.verse_divider_color), 1))
            margin = w // 4
            p.drawLine(margin, y_after, w - margin, y_after)
            y_after += 15

        return y_after

    def _draw_vertical_divider(self, p: QPainter, w: int, h: int, y_top: int, s: SlideSettings):
        """좌우 컬럼 사이 수직 구분선"""
        center_x = w // 2
        pen = QPen(QColor(s.divider_color), s.divider_thickness)
        p.setPen(pen)
        p.drawLine(center_x, y_top + 10, center_x, h - 50)

    def _draw_column_text(
        self, p: QPainter, text: str, config: ColumnConfig,
        x: int, y_top: int, col_width: int, y_bottom: int
    ):
        """한 컬럼의 텍스트를 워드랩하여 그리기"""
        font = self._make_font_from_config(config)
        p.setFont(font)
        p.setPen(QColor(config.text_color))

        fm = QFontMetrics(font)
        line_height = int(fm.height() * config.line_spacing)

        # 워드랩
        lines = self._word_wrap(text, fm, col_width)

        # 전체 텍스트 블록 높이
        total_height = len(lines) * line_height
        available_height = y_bottom - y_top

        # 수직 정렬
        if config.vertical_align == "top":
            y = y_top
        elif config.vertical_align == "bottom":
            y = y_bottom - total_height
        else:  # center
            y = y_top + (available_height - total_height) // 2

        # 각 줄 그리기
        for line in lines:
            line_width = fm.horizontalAdvance(line)

            if config.text_align == "center":
                lx = x + (col_width - line_width) // 2
            elif config.text_align == "right":
                lx = x + col_width - line_width
            else:  # left
                lx = x

            p.drawText(lx, y + fm.ascent(), line)
            y += line_height

    def _draw_label(self, p: QPainter, config: ColumnConfig, x: int, col_width: int, h: int):
        """컬럼 하단에 언어 라벨 표시"""
        font = self._make_font("", config.label_font_size, 400)
        p.setFont(font)
        p.setPen(QColor(config.label_color))

        fm = QFontMetrics(font)
        label_rect = QRectF(x, h - fm.height() - 20, col_width, fm.height() + 10)
        p.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, config.label)

    # === 유틸리티 ===

    def _make_font_from_config(self, config: ColumnConfig) -> QFont:
        """ColumnConfig에서 QFont 생성. font_path가 있으면 파일에서 로드."""
        family = config.font_family
        if config.font_path and os.path.isfile(config.font_path):
            family = self._load_font_file(config.font_path)
        return self._make_font(family, config.font_size, config.font_weight, config.letter_spacing)

    @classmethod
    def _load_font_file(cls, path: str) -> str:
        """폰트 파일을 Qt에 등록하고 패밀리 이름 반환. 캐시 사용."""
        if path in cls._font_file_cache:
            return cls._font_file_cache[path]

        font_id = QFontDatabase.addApplicationFont(path)
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                cls._font_file_cache[path] = families[0]
                return families[0]
        # 로드 실패 시 빈 문자열 (시스템 기본 사용)
        return ""

    @staticmethod
    def _make_font(family: str, size: int, weight: int, letter_spacing: float = 0.0) -> QFont:
        """설정값에서 QFont 객체 생성"""
        font = QFont()
        if family:
            font.setFamily(family)
        font.setPixelSize(size)
        font.setWeight(QFont.Weight(weight))
        if letter_spacing != 0.0:
            font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, letter_spacing)
        return font

    @staticmethod
    def _word_wrap(text: str, fm: QFontMetrics, max_width: int) -> list[str]:
        """텍스트를 최대 폭에 맞게 워드랩. 공백 기반 + CJK 글자 단위 폴백"""
        if not text:
            return []

        words = text.split()
        if not words:
            return []

        # 공백이 없는 경우 (일부 CJK 텍스트) → 글자 단위 분할
        if len(words) == 1 and fm.horizontalAdvance(text) > max_width:
            return SlideRenderer._char_wrap(text, fm, max_width)

        lines: list[str] = []
        current = words[0]

        for word in words[1:]:
            test = current + " " + word
            if fm.horizontalAdvance(test) <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        # 각 줄이 여전히 넘치면 글자 단위로 한번 더 분할
        result: list[str] = []
        for line in lines:
            if fm.horizontalAdvance(line) > max_width:
                result.extend(SlideRenderer._char_wrap(line, fm, max_width))
            else:
                result.append(line)

        return result

    @staticmethod
    def _char_wrap(text: str, fm: QFontMetrics, max_width: int) -> list[str]:
        """글자 단위 워드랩 (CJK 등 공백 없는 텍스트용)"""
        lines: list[str] = []
        current = ""
        for ch in text:
            test = current + ch
            if fm.horizontalAdvance(test) > max_width and current:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
        return lines
