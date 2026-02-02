# app/ui/main_window.py
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit,
                             QProgressBar, QGroupBox, QMessageBox, QFileDialog)
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker, BatchExportWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_dir = None  # 用于存储用户选择的目录
        self.init_ui()
        self.fetch_ip()

    def init_ui(self):
        self.setWindowTitle("全球每日重点汇报助手 (Global Edition)")
        self.resize(900, 700)
        self.setStyleSheet("font-family: 'Microsoft YaHei'; font-size: 10pt;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 1. IP 和 保存设置
        top_group = QGroupBox("环境与设置")
        top_layout = QHBoxLayout()
        self.ip_label = QLabel("IP: ---")
        refresh_btn = QPushButton("刷新IP")
        refresh_btn.clicked.connect(self.fetch_ip)

        self.dir_label = QLabel("保存目录: 未指定")
        self.btn_set_dir = QPushButton("📂 设置目录")
        self.btn_set_dir.clicked.connect(self.choose_directory)

        top_layout.addWidget(self.ip_label)
        top_layout.addWidget(refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.dir_label)
        top_layout.addWidget(self.btn_set_dir)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)

        # 2. 汇报控制
        ctrl_group = QGroupBox("汇报操作")
        ctrl_layout = QHBoxLayout()

        # 左侧：查看单个国家
        self.country_combo = QComboBox()
        self.country_combo.addItems(COUNTRY_CONFIGS.keys())
        self.btn_view = QPushButton("👀 查看该国日报")
        self.btn_view.clicked.connect(self.view_single_country)

        # 右侧：一键导出所有
        self.btn_export_all = QPushButton("💾 抓取全球并保存 (.txt)")
        self.btn_export_all.setStyleSheet("background-color: #d83b01; color: white; font-weight: bold;")
        self.btn_export_all.clicked.connect(self.export_all_countries)

        ctrl_layout.addWidget(QLabel("选择地区:"))
        ctrl_layout.addWidget(self.country_combo)
        ctrl_layout.addWidget(self.btn_view)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.btn_export_all)
        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # 3. 进度条 (初始隐藏)
        self.pbar = QProgressBar()
        self.pbar.hide()
        layout.addWidget(self.pbar)

        # 4. 文本显示区
        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

    def fetch_ip(self):
        self.ip_label.setText("IP: 查询中...")
        self.worker = DataWorker("ip")
        self.worker.result_signal.connect(self.handle_single_result)
        self.worker.start()

    def choose_directory(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择保存日报的文件夹")
        if folder:
            self.save_dir = folder
            self.dir_label.setText(f"保存目录: {folder}")
            return True
        return False

    def view_single_country(self):
        """查看单个国家新闻"""
        key = self.country_combo.currentText()
        url = COUNTRY_CONFIGS[key]["url"]

        self.btn_view.setEnabled(False)
        self.pbar.show()
        self.pbar.setFormat("正在获取中...")
        self.pbar.setRange(0, 0)  # 忙碌模式

        self.worker = DataWorker("news", url=url)
        self.worker.result_signal.connect(self.handle_single_result)
        self.worker.start()

    def export_all_countries(self):
        """导出所有国家"""
        # 1. 强制检查目录
        if not self.save_dir:
            QMessageBox.warning(self, "提示", "请先指定保存文件的目录！")
            if not self.choose_directory():  # 如果用户打开弹窗后点了取消
                return

        # 2. 锁定按钮，防止重复点击
        self.btn_export_all.setEnabled(False)
        self.btn_view.setEnabled(False)
        self.text_area.clear()
        self.pbar.show()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)

        # 3. 启动后台批量线程
        self.batch_worker = BatchExportWorker()
        self.batch_worker.progress_signal.connect(self.update_export_progress)
        self.batch_worker.finished_signal.connect(self.save_export_file)
        self.batch_worker.start()

    def update_export_progress(self, msg, val):
        self.pbar.setValue(val)
        self.pbar.setFormat(msg)
        self.text_area.append(msg)  # 在文本框实时打印日志

    def handle_single_result(self, res):
        """处理单次任务结果"""
        self.btn_view.setEnabled(True)
        self.pbar.hide()

        if res["type"] == "ip":
            if res["success"]:
                self.ip_label.setText(f"IP: {res['data']}")
            else:
                self.ip_label.setText("IP: 获取失败")

        elif res["type"] == "news":
            if res["success"]:
                self.display_markdown(res["data"])
            else:
                self.text_area.setText("获取失败，请检查网络连接。")

    def display_markdown(self, news_list):
        country = self.country_combo.currentText()
        date_str = datetime.now().strftime("%Y-%m-%d")
        text = f"# 📅 每日汇报\n**日期**: {date_str} | **地区**: {country}\n\n---\n"
        for i, item in enumerate(news_list, 1):
            text += f"{i}. **{item['title']}**\n"
        self.text_area.setMarkdown(text)

    def save_export_file(self, full_content):
        """保存批量抓取的结果"""
        self.btn_export_all.setEnabled(True)
        self.btn_view.setEnabled(True)
        self.pbar.hide()

        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{date_str}.txt"
        file_path = os.path.join(self.save_dir, file_name)

        header = f"【全球重点新闻汇总】\n日期: {date_str}\n生成的IP: {self.ip_label.text()}\n"
        final_text = header + ("=" * 50) + full_content

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)

            self.text_area.setMarkdown(f"# ✅ 导出成功\n\n文件已保存至:\n`{file_path}`\n\n---\n{full_content}")
            QMessageBox.information(self, "成功", f"全球新闻已保存至：\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))