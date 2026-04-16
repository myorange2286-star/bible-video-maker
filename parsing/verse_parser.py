# -*- coding: utf-8 -*-
"""텍스트 파일 파싱 — 여러 형식 자동 감지"""
from __future__ import annotations
import re
from pathlib import Path
from models.verse import Verse


def parse_verses(file_path: str | Path) -> list[Verse]:
    """
    텍스트 파일을 파싱하여 Verse 리스트 반환.
    형식을 자동 감지합니다.

    지원 형식:
      1) 파이프 3칸:  1|왼쪽텍스트|오른쪽텍스트
      2) 파이프 2칸:  1|텍스트만 (오른쪽 비움)
      3) 탭 3칸:     1\t왼쪽텍스트\t오른쪽텍스트
      4) 탭 2칸:     1\t텍스트만
      5) 장:절 형식:  1:1 텍스트... (절 번호 자동 추출)
      6) 숫자 시작:   1 텍스트... 또는 1. 텍스트...
      7) 그냥 텍스트:  번호 없이 텍스트만 (자동 번호 부여)
    """
    path = Path(file_path)
    text = _read_file(path)
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]

    if not lines:
        raise ValueError("파싱 오류: 파일에 유효한 텍스트가 없습니다.")

    # 형식 자동 감지
    format_type = _detect_format(lines)
    verses = _parse_by_format(lines, format_type)

    if not verses:
        raise ValueError("파싱 오류: 파일에서 절 데이터를 찾을 수 없습니다.")

    return verses


def parse_text(text: str) -> list[Verse]:
    """문자열을 직접 파싱 (GUI 붙여넣기용)"""
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and not l.startswith("#")]

    if not lines:
        raise ValueError("유효한 텍스트가 없습니다.")

    format_type = _detect_format(lines)
    return _parse_by_format(lines, format_type)


def _detect_format(lines: list[str]) -> str:
    """첫 몇 줄을 보고 형식 판별"""
    sample = lines[:min(5, len(lines))]

    # 파이프(|) 포함 여부
    pipe_counts = [l.count("|") for l in sample]
    if all(c >= 2 for c in pipe_counts):
        return "pipe3"  # 1|왼쪽|오른쪽
    if all(c >= 1 for c in pipe_counts):
        return "pipe2"  # 1|텍스트

    # 탭 포함 여부
    tab_counts = [l.count("\t") for l in sample]
    if all(c >= 2 for c in tab_counts):
        return "tab3"
    if all(c >= 1 for c in tab_counts):
        return "tab2"

    # 장:절 형식 (1:1, 2:3 등)
    chapter_verse = re.compile(r"^\d+:\d+\s")
    if all(chapter_verse.match(l) for l in sample):
        return "chapter_verse"

    # 숫자로 시작 (1 텍스트, 1. 텍스트)
    num_start = re.compile(r"^\d+\.?\s")
    if all(num_start.match(l) for l in sample):
        return "numbered"

    # 그 외: 번호 없는 일반 텍스트
    return "plain"


def _parse_by_format(lines: list[str], fmt: str) -> list[Verse]:
    """형식에 맞게 파싱"""
    verses: list[Verse] = []

    for i, line in enumerate(lines):
        if fmt == "pipe3":
            parts = line.split("|", 2)
            num = _parse_number(parts[0].strip(), i)
            verses.append(Verse(num, parts[1].strip(), parts[2].strip()))

        elif fmt == "pipe2":
            parts = line.split("|", 1)
            num = _parse_number(parts[0].strip(), i)
            verses.append(Verse(num, parts[1].strip(), ""))

        elif fmt == "tab3":
            parts = line.split("\t", 2)
            num = _parse_number(parts[0].strip(), i)
            verses.append(Verse(num, parts[1].strip(), parts[2].strip()))

        elif fmt == "tab2":
            parts = line.split("\t", 1)
            num = _parse_number(parts[0].strip(), i)
            verses.append(Verse(num, parts[1].strip(), ""))

        elif fmt == "chapter_verse":
            # "1:3 텍스트" → 절 번호 = 3
            m = re.match(r"(\d+):(\d+)\s+(.*)", line)
            if m:
                verse_num = int(m.group(2))
                verses.append(Verse(verse_num, m.group(3).strip(), ""))

        elif fmt == "numbered":
            # "1 텍스트" 또는 "1. 텍스트"
            m = re.match(r"(\d+)\.?\s+(.*)", line)
            if m:
                verses.append(Verse(int(m.group(1)), m.group(2).strip(), ""))

        else:  # plain
            verses.append(Verse(i + 1, line, ""))

    return verses


def _parse_number(s: str, fallback_index: int) -> int:
    """문자열에서 숫자 추출. 실패 시 인덱스+1 사용."""
    try:
        return int(s)
    except ValueError:
        # "1:3" 같은 경우 → 마지막 숫자 사용
        nums = re.findall(r"\d+", s)
        if nums:
            return int(nums[-1])
        return fallback_index + 1


def merge_two_files(left_path: str | Path, right_path: str | Path) -> list[Verse]:
    """
    두 개의 단일 언어 파일을 합쳐서 좌우 2컬럼 Verse 리스트 생성.

    절 번호로 매칭:
      - 양쪽 다 있으면 → 좌우 합침
      - 한쪽만 있으면 → 있는 쪽만 표시, 나머지 빈칸
      - 줄 수가 다르면 → 순서대로 매칭 (절 번호 무시)
    """
    left_verses = parse_verses(left_path)
    right_verses = parse_verses(right_path)

    # 절 번호 기반 매칭 시도
    left_by_num = {v.number: v for v in left_verses}
    right_by_num = {v.number: v for v in right_verses}
    all_nums = sorted(set(left_by_num.keys()) | set(right_by_num.keys()))

    # 절 번호가 의미 있는지 확인 (겹치는 번호가 있으면 번호 기반 매칭)
    common_nums = set(left_by_num.keys()) & set(right_by_num.keys())

    if common_nums:
        # 절 번호 기반 매칭
        merged = []
        for num in all_nums:
            left_text = left_by_num[num].left_text if num in left_by_num else ""
            right_text = right_by_num[num].left_text if num in right_by_num else ""
            merged.append(Verse(num, left_text, right_text))
        return merged
    else:
        # 절 번호 매칭 안 되면 순서대로 매칭
        max_len = max(len(left_verses), len(right_verses))
        merged = []
        for i in range(max_len):
            left_text = left_verses[i].left_text if i < len(left_verses) else ""
            right_text = right_verses[i].left_text if i < len(right_verses) else ""
            num = left_verses[i].number if i < len(left_verses) else i + 1
            merged.append(Verse(num, left_text, right_text))
        return merged


def _read_file(path: Path) -> str:
    """UTF-8 → CP949 → Latin-1 폴백으로 텍스트 파일 읽기"""
    for enc in ["utf-8", "cp949", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")
