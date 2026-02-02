import sys
import os
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def load_stylesheet(app):
    """加载 QSS 样式表"""
    # 获取当前文件所在目录的绝对路径，确保打包后也能找到文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(base_dir, 'app', 'assets', 'style.qss')

    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at {qss_path}")


def main():
    app = QApplication(sys.argv)

    # 加载样式
    load_stylesheet(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()