# -*- coding: utf-8 -*-
"""PyInstaller 패키징 시 리소스 경로 해결"""
from __future__ import annotations
import os
import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    개발 환경과 PyInstaller 패키징 환경 모두에서 리소스 경로를 올바르게 반환.

    PyInstaller --onedir 모드:
      실행 파일과 같은 디렉토리의 _internal/ 폴더에 리소스가 위치
    개발 환경:
      프로젝트 루트 기준 상대 경로
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 패키징된 앱
        base = sys._MEIPASS
    else:
        # 개발 환경
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def presets_dir() -> Path:
    """프리셋 디렉토리 경로"""
    return Path(resource_path("presets"))


def samples_dir() -> Path:
    """샘플 데이터 디렉토리 경로"""
    return Path(resource_path("samples"))
