# -*- coding: utf-8 -*-
"""Phase 1 검증 스크립트 — 샘플 데이터를 파싱하고 슬라이드 1장을 PNG로 렌더링"""
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_bootstrap import prepare_qt_runtime
from PyQt6.QtWidgets import QApplication
from parsing.verse_parser import parse_verses
from rendering.slide_renderer import SlideRenderer
from models.settings import SlideSettings


def main():
    prepare_qt_runtime()

    # QPainter 사용을 위해 QApplication 필요
    app = QApplication(sys.argv)

    # 1. 샘플 파일 파싱
    sample_path = os.path.join(os.path.dirname(__file__), "samples", "genesis1.txt")
    verses = parse_verses(sample_path)
    print(f"파싱 완료: {len(verses)}절 로드됨")

    # 2. 3가지 레이아웃 모드 모두 렌더링
    renderer = SlideRenderer()
    out_dir = os.path.dirname(__file__)

    for mode in ("dual_horizontal", "single", "dual_vertical"):
        s = SlideSettings()
        s.layout_mode = mode
        img = renderer.render(verses[0], s)
        path = os.path.join(out_dir, f"output_test_{mode}.png")
        img.save(path, "PNG")
        print(f"렌더링 완료 [{mode}]: {path}")

    # 기존 출력 호환
    settings = SlideSettings()
    img = renderer.render(verses[0], settings)
    img.save(os.path.join(out_dir, "output_test.png"), "PNG")

    # 타이틀 슬라이드도 테스트
    title_img = renderer.render_title(settings.header_text, settings)
    title_path = os.path.join(os.path.dirname(__file__), "output_title.png")
    title_img.save(title_path, "PNG")
    print(f"타이틀 렌더링 완료: {title_path}")

    # 시간 계산 테스트
    for v in verses[:5]:
        dur = settings.calculate_duration(v)
        print(f"  절 {v.number}: {dur:.1f}초 (단어 {len(v.left_text.split())}개)")


if __name__ == "__main__":
    main()
