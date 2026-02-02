import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit,
                             QProgressBar, QGroupBox, QMessageBox, QFileDialog)
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker, BatchExportWorker
def init_ui(self):
    self.setWindowTitle("全球每日重点汇报助手 (Global Edition)")
    self.resize(900, 700)
    # ⚠️删除这行：self.setStyleSheet("font-family: ...") 因为样式表里已经统一写了

    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # 1. IP 和 保存设置
    top_group = QGroupBox("环境与设置")  # QSS会自动美化它
    # ... (中间代码不变) ...

    # 2. 汇报控制
    ctrl_group = QGroupBox("汇报操作")
    ctrl_layout = QHBoxLayout()

    # ... (中间代码不变) ...

    # 右侧：一键导出所有
    self.btn_export_all = QPushButton("💾 抓取全球并保存 (.txt)")

    # ⚠️关键修改：设置 ObjectName，对应 QSS 中的 #btn_accent
    self.btn_export_all.setObjectName("btn_accent")

    # ⚠️删除这行旧的行内样式：self.btn_export_all.setStyleSheet("...")

    self.btn_export_all.clicked.connect(self.export_all_countries)

    ctrl_layout.addWidget(QLabel("选择地区:"))
    # ... (后续代码不变) ...