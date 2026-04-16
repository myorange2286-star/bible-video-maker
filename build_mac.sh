#!/bin/bash
# Bible Video Maker — macOS 빌드 스크립트
# 사용법: ./build_mac.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Bible Video Maker macOS 빌드 ==="

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "오류: .venv 가상환경이 없습니다. 먼저 설치를 진행해주세요."
    echo "  python3.10 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt pyinstaller"
    exit 1
fi

# PyInstaller 확인
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller 설치 중..."
    pip install pyinstaller
fi

echo "빌드 시작..."

pyinstaller \
    --name "BibleVideoMaker" \
    --windowed \
    --onedir \
    --noconfirm \
    --clean \
    --add-data "presets:presets" \
    --add-data "samples:samples" \
    --add-data "qt_bootstrap.py:." \
    --add-data "resource_path.py:." \
    --hidden-import "PyQt6.QtCore" \
    --hidden-import "PyQt6.QtGui" \
    --hidden-import "PyQt6.QtWidgets" \
    --collect-all "PyQt6" \
    app.py

echo ""
echo "=== 빌드 완료 ==="
echo "앱 위치: dist/BibleVideoMaker/BibleVideoMaker.app"
echo ""
echo "실행 테스트:"
echo "  open dist/BibleVideoMaker/BibleVideoMaker.app"
