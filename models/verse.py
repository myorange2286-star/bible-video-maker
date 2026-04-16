# -*- coding: utf-8 -*-
"""절(Verse) 데이터 모델"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Verse:
    """한 절의 데이터. 좌/우 컬럼 텍스트는 어떤 언어든 가능."""
    number: int
    left_text: str
    right_text: str
    # 수동 모드일 때 개별 표시 시간 (초). None이면 전역 설정 사용
    custom_duration: float | None = None
