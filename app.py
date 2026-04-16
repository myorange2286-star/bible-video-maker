# -*- coding: utf-8 -*-
"""Bible Video Maker — 메인 진입점"""
import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Qt 플러그인 부트스트랩 (QApplication 생성 전에 호출)
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
