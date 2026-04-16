@echo off
REM Bible Video Maker — Windows 빌드 스크립트
REM 사용법: build_win.bat
REM 요구사항: Python 3.10+, pip install -r requirements.txt pyinstaller

echo === Bible Video Maker Windows 빌드 ===

REM 가상환경 활성화
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo 오류: .venv 가상환경이 없습니다.
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt pyinstaller
    exit /b 1
)

REM PyInstaller 확인
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 설치 중...
    pip install pyinstaller
)

echo 빌드 시작...

pyinstaller ^
    --name "BibleVideoMaker" ^
    --windowed ^
    --onedir ^
    --noconfirm ^
    --clean ^
    --add-data "presets;presets" ^
    --add-data "samples;samples" ^
    --add-data "qt_bootstrap.py;." ^
    --add-data "resource_path.py;." ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --collect-all "PyQt6" ^
    app.py

echo.
echo === 빌드 완료 ===
echo 앱 위치: dist\BibleVideoMaker\BibleVideoMaker.exe
echo.
echo 실행 테스트:
echo   dist\BibleVideoMaker\BibleVideoMaker.exe
