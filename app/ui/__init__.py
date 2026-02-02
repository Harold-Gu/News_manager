import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit,
                             QProgressBar, QGroupBox, QMessageBox, QFileDialog)
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker, BatchExportWorker


def init_ui(self):
    self.setWindowTitle("全球每日重点汇报助手")
    self.resize(900, 700)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # ==========================================
    # 1. 顶部区域：IP检测 与 目录设置
    # ==========================================
    top_group = QGroupBox("环境与设置")
    top_layout = QHBoxLayout()
    # IP 部分
    self.ip_label = QLabel("IP: ---")
    refresh_btn = QPushButton("刷新IP")
    refresh_btn.clicked.connect(self.fetch_ip)
    # 目录部分 (修复了之前的报错)
    self.dir_label = QLabel()  # 必须先实例化
    if self.save_dir:
        self.dir_label.setText(f"保存目录: {self.save_dir}")
    else:
        self.dir_label.setText("保存目录: (未设置，默认当前目录)")
    self.btn_set_dir = QPushButton("📂 设置目录")
    self.btn_set_dir.clicked.connect(self.choose_directory)
    # 添加到布局
    top_layout.addWidget(self.ip_label)
    top_layout.addWidget(refresh_btn)
    top_layout.addStretch()  # 弹簧，把后面的控件顶到右边
    top_layout.addWidget(self.dir_label)
    top_layout.addWidget(self.btn_set_dir)
    top_group.setLayout(top_layout)
    layout.addWidget(top_group)
    # ==========================================
    # 2. 控制区域：选择国家 与 导出操作
    # ==========================================
    ctrl_group = QGroupBox("汇报操作")
    ctrl_layout = QHBoxLayout()
    # 左侧：下拉选框和查看按钮
    ctrl_layout.addWidget(QLabel("选择地区:"))
    self.country_combo = QComboBox()
    self.country_combo.addItems(COUNTRY_CONFIGS.keys())  # 读取配置文件里的国家列表
    self.btn_view = QPushButton("👀 查看该国日报")
    self.btn_view.clicked.connect(self.view_single_country)
    # 右侧：全量导出按钮
    self.btn_export_all = QPushButton("💾 抓取全球并保存 (.txt)")
    # 【关键】设置 objectName，以便 QSS 文件中的 #btn_accent 能识别并将其变成红色
    self.btn_export_all.setObjectName("btn_accent")
    self.btn_export_all.clicked.connect(self.export_all_countries)
    # 添加到布局
    ctrl_layout.addWidget(self.country_combo)
    ctrl_layout.addWidget(self.btn_view)
    ctrl_layout.addStretch()  # 弹簧
    ctrl_layout.addWidget(self.btn_export_all)
    ctrl_group.setLayout(ctrl_layout)
    layout.addWidget(ctrl_group)


    # 文本展示区
    self.text_area = QTextEdit()
    self.text_area.setPlaceholderText("等待操作...")
    layout.addWidget(self.text_area)
    self.pbar = QProgressBar()
    self.pbar.hide()
    layout.addWidget(self.pbar)

    self.text_area = QTextEdit()
    self.text_area.setPlaceholderText("等待操作...")

    self.text_area.setOpenExternalLinks(True)

    layout.addWidget(self.text_area)
