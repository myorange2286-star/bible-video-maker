# -*- coding: utf-8 -*-
"""Bible Video Maker — 메인 진입점"""
import sys
import os
import subprocess
import platform

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _ensure_vcredist():
    """Windows에서 Visual C++ 런타임이 없으면 자동 설치 (패키징 환경 전용)"""
    if platform.system() != "Windows":
        return
    if not getattr(sys, 'frozen', False):
        return

    import ctypes
    try:
        ctypes.WinDLL('vcruntime140.dll')
        ctypes.WinDLL('msvcp140.dll')
        return  # 이미 설치됨
    except OSError:
        pass

    # 번들된 vc_redist.x64.exe로 자동 설치
    base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    redist = os.path.join(base, 'vc_redist.x64.exe')
    if os.path.exists(redist):
        subprocess.run([redist, '/install', '/quiet', '/norestart'], check=False)


# 1단계: VC++ 런타임 확인 (PyQt6 import 전에 실행해야 함)
_ensure_vcredist()

# 2단계: Qt 플러그인 부트스트랩 (macOS 개발환경 전용)
from qt_bootstrap import prepare_qt_runtime
prepare_qt_runtime()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Bible Video Maker")
    app.setOrganizationName("BibleVideoMaker")

    # 아이콘 설정 (있으면)
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
