# app/ui/main_window.py
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit,
                             QProgressBar, QGroupBox, QMessageBox)
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.fetch_ip()  # 启动自动查IP

    def init_ui(self):
        self.setWindowTitle("每日重点汇报助手 (Modularized)")
        self.resize(800, 600)
        self.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 10pt;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. IP 区域
        ip_group = QGroupBox("网络环境")
        ip_layout = QHBoxLayout()
        self.ip_label = QLabel("IP: ---")
        refresh_btn = QPushButton("刷新 IP")
        refresh_btn.clicked.connect(self.fetch_ip)
        ip_layout.addWidget(self.ip_label)
        ip_layout.addWidget(refresh_btn)
        ip_group.setLayout(ip_layout)
        layout.addWidget(ip_group)

        # 2. 控制区域
        ctrl_group = QGroupBox("配置")
        ctrl_layout = QHBoxLayout()
        self.country_combo = QComboBox()
        self.country_combo.addItems(COUNTRY_CONFIGS.keys())
        self.btn_run = QPushButton("生成汇报")
        self.btn_run.clicked.connect(self.start_report)
        ctrl_layout.addWidget(QLabel("地区:"))
        ctrl_layout.addWidget(self.country_combo)
        ctrl_layout.addWidget(self.btn_run)
        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # 3. 文本区域
        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        # 4. 进度条
        self.pbar = QProgressBar()
        self.pbar.hide()
        layout.addWidget(self.pbar)

    def fetch_ip(self):
        self.ip_label.setText("IP: 查询中...")
        self.worker = DataWorker("ip")
        self.worker.result_signal.connect(self.handle_result)
        self.worker.start()

    def start_report(self):
        key = self.country_combo.currentText()
        url = COUNTRY_CONFIGS[key]["url"]

        self.btn_run.setEnabled(False)
        self.pbar.show()
        self.pbar.setRange(0, 0)  # 忙碌模式

        self.worker = DataWorker("news", url=url)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, res):
        if res["type"] == "ip":
            if res["success"]:
                self.ip_label.setText(f"IP: {res['data']}")
            else:
                self.ip_label.setText("IP: 获取失败")

        elif res["type"] == "news":
            self.btn_run.setEnabled(True)
            self.pbar.hide()
            if res["success"]:
                self.generate_markdown(res["data"])
            else:
                QMessageBox.warning(self, "错误", res.get("error", "未知错误"))

    def generate_markdown(self, news_list):
        country = self.country_combo.currentText()
        date_str = datetime.now().strftime("%Y-%m-%d")
        text = f"# 📅 每日汇报\n**日期**: {date_str} | **地区**: {country}\n\n---\n"

        for i, item in enumerate(news_list, 1):
            text += f"{i}. **{item['title']}**\n   *来源: {item['source']}*\n\n"

        self.text_area.setMarkdown(text)