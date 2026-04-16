# -*- coding: utf-8 -*-
"""텍스트 파일 파싱 — 절번호|왼쪽텍스트|오른쪽텍스트 형식"""
from __future__ import annotations
from pathlib import Path
from models.verse import Verse


def parse_verses(file_path: str | Path) -> list[Verse]:
    """
    파이프(|) 구분 텍스트 파일을 파싱하여 Verse 리스트 반환.

    포맷: 절번호|왼쪽텍스트|오른쪽텍스트
    - '#'으로 시작하는 줄: 주석 (무시)
    - 빈 줄: 무시
    - 오른쪽 텍스트에 '|'가 포함될 수 있으므로 maxsplit=2 사용
    """
    verses: list[Verse] = []
    path = Path(file_path)

    # 인코딩 자동 감지: UTF-8 시도 → 실패 시 CP949 (한국어 Windows)
    text = _read_file(path)

    for line_num, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("|", 2)  # maxsplit=2
        if len(parts) != 3:
            raise ValueError(
                f"파싱 오류 (줄 {line_num}): "
                f"'절번호|왼쪽텍스트|오른쪽텍스트' 형식이어야 합니다.\n"
                f"문제 줄: {line[:80]}"
            )

        try:
            number = int(parts[0].strip())
        except ValueError:
            raise ValueError(
                f"파싱 오류 (줄 {line_num}): "
                f"절 번호가 숫자가 아닙니다: '{parts[0].strip()}'"
            )

        verses.append(Verse(
            number=number,
            left_text=parts[1].strip(),
            right_text=parts[2].strip(),
        ))

    if not verses:
        raise ValueError("파싱 오류: 파일에 유효한 절 데이터가 없습니다.")

    return verses


def _read_file(path: Path) -> str:
    """UTF-8 → CP949 폴백으로 텍스트 파일 읽기"""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp949")
