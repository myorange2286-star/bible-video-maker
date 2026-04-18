# -*- coding: utf-8 -*-
"""슬라이드 설정 모델 — 원시 타입만 저장, Qt 객체는 렌더 시 생성"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class ColumnConfig:
    """좌 또는 우 컬럼의 텍스트 설정"""
    label: str = ""                    # 언어 라벨 (예: "KISWAHILI", "한국어")
    font_family: str = ""              # 빈 문자열이면 시스템 기본
    font_path: str = ""                # 폰트 파일 경로 (있으면 font_family보다 우선)
    font_size: int = 48                # pt
    font_weight: int = 400             # 300=Light, 400=Regular, 700=Bold
    letter_spacing: float = 0.0        # px (-5 ~ 20)
    line_spacing: float = 1.4          # 배수 (1.0 ~ 2.5)
    text_color: str = "#F0E6D2"        # 텍스트 색상
    label_visible: bool = True         # 언어 라벨 표시 여부
    label_font_size: int = 24          # 라벨 폰트 크기
    label_color: str = "#8C826E"       # 라벨 색상
    text_align: str = "left"           # "left" | "center" | "right"
    vertical_align: str = "center"     # "top" | "center" | "bottom"


@dataclass
class SlideSettings:
    """전체 슬라이드 설정 — JSON 직렬화 가능"""

    # === 해상도 ===
    width: int = 1920
    height: int = 1080

    # === 배경 ===
    bg_mode: str = "default_dark"      # "solid" | "gradient" | "image" | "default_dark"
    bg_color: str = "#0A0E1A"          # 단색 배경
    bg_gradient_start: str = "#0A0E1A" # 그라디언트 시작
    bg_gradient_end: str = "#1E3A5F"   # 그라디언트 끝
    bg_image_path: Optional[str] = None  # 배경 이미지 경로
    bg_image_opacity: float = 0.3      # 배경 이미지 어둡기 (0~1)

    # === 좌우 컬럼 ===
    left_column: ColumnConfig = field(default_factory=lambda: ColumnConfig(
        label="KISWAHILI",
        font_family="",
        font_size=48,
        font_weight=400,
        text_color="#F0E6D2",
        label_color="#8C826E",
    ))
    right_column: ColumnConfig = field(default_factory=lambda: ColumnConfig(
        label="한국어",
        font_family="",
        font_size=48,
        font_weight=400,
        text_color="#E6D7C3",
        label_color="#8C826E",
    ))

    # === 레이아웃 모드 ===
    layout_mode: str = "dual_horizontal"  # "single" | "dual_horizontal" | "dual_vertical"

    # === 컬럼 레이아웃 ===
    column_padding: int = 90           # 좌우 여백 (px)
    column_gap: int = 60               # 좌우 컬럼 사이 간격 (가로 모드) / 위아래 간격 (세로 모드)

    # === 절 번호 ===
    verse_number_color: str = "#C83C3C"  # 빨강
    verse_number_size: int = 76
    verse_number_position: str = "center"  # "center" | "left" | "right"

    # === 헤더 ===
    header_text: str = "MWANZO / 창세기"
    header_visible: bool = True
    header_color: str = "#D2B98C"      # 골드
    header_size: int = 28

    # === 구분선 ===
    divider_visible: bool = True
    divider_color: str = "#504B41"
    divider_thickness: int = 1

    # === 절 번호 아래 구분선 ===
    verse_divider_visible: bool = True
    verse_divider_color: str = "#504B41"

    # === 영상 설정 ===
    duration_mode: str = "auto"        # "auto" | "fixed" | "manual"
    fixed_duration: float = 5.0        # 고정 모드일 때 (초)
    auto_word_factor: float = 0.35     # 자동 모드: 단어수 × factor
    auto_base_time: float = 1.5        # 자동 모드: 기본 시간
    auto_min_duration: float = 3.0     # 자동 모드: 최소
    auto_max_duration: float = 20.0    # 자동 모드: 최대
    title_duration: float = 4.0        # 타이틀 슬라이드 시간
    fade_enabled: bool = False
    fade_duration: float = 0.5         # 페이드 전환 시간 (0~2초)
    fps: int = 30
    bgm_path: Optional[str] = None     # 배경음악 경로
    bgm_volume: float = 0.3           # 배경음악 볼륨 (0~1)

    def to_json(self) -> str:
        """설정을 JSON 문자열로 직렬화"""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> SlideSettings:
        """JSON 문자열에서 설정 복원"""
        data = json.loads(json_str)
        # 중첩 ColumnConfig 복원
        if "left_column" in data and isinstance(data["left_column"], dict):
            data["left_column"] = ColumnConfig(**data["left_column"])
        if "right_column" in data and isinstance(data["right_column"], dict):
            data["right_column"] = ColumnConfig(**data["right_column"])
        return cls(**data)

    def calculate_duration(self, verse: 'Verse') -> float:
        """절 표시 시간 계산"""
        if self.duration_mode == "manual" and verse.custom_duration is not None:
            return verse.custom_duration
        if self.duration_mode == "fixed":
            return self.fixed_duration
        # auto 모드: 왼쪽 컬럼 단어 수 기반
        word_count = len(verse.left_text.split())
        duration = word_count * self.auto_word_factor + self.auto_base_time
        return max(self.auto_min_duration, min(self.auto_max_duration, duration))
