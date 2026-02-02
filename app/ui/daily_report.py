import os
from PyQt6.QtCore import QSettings, QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextBrowser,
                             QProgressBar, QGroupBox, QMessageBox, QFileDialog,
                             QDateEdit)
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker, BatchExportWorker


class DailyReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("ReportTeam", "DailyReportAssistant")
        self.save_dir = self.settings.value("user_save_dir")
        self.init_ui()
        self.fetch_ip()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. 顶部：位置与设置
        top_group = QGroupBox("环境与设置")
        top_layout = QHBoxLayout()
        self.ip_label = QLabel("📍 属地: 定位中...")
        refresh_btn = QPushButton("刷新位置")
        refresh_btn.clicked.connect(self.fetch_ip)
        self.dir_label = QLabel()
        self.update_dir_label()
        self.btn_set_dir = QPushButton("📂 设置目录")
        self.btn_set_dir.clicked.connect(self.choose_directory)
        top_layout.addWidget(self.ip_label)
        top_layout.addWidget(refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.dir_label)
        top_layout.addWidget(self.btn_set_dir)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)

        # 2. 汇报操作
        ctrl_group = QGroupBox("日报生成")
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        ctrl_layout.addWidget(self.date_edit)

        ctrl_layout.addSpacing(10)
        ctrl_layout.addWidget(QLabel("地区:"))
        self.country_combo = QComboBox()
        self.country_combo.addItems(COUNTRY_CONFIGS.keys())
        ctrl_layout.addWidget(self.country_combo)

        self.btn_view = QPushButton("👀 查看日报")
        self.btn_view.clicked.connect(self.view_single_country)
        ctrl_layout.addWidget(self.btn_view)

        ctrl_layout.addStretch()
        self.btn_export_all = QPushButton("💾 导出全球日报 (.txt)")
        self.btn_export_all.setObjectName("btn_accent")
        self.btn_export_all.clicked.connect(self.export_all_countries)
        ctrl_layout.addWidget(self.btn_export_all)
        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # 3. 内容区
        self.pbar = QProgressBar()
        self.pbar.hide()
        layout.addWidget(self.pbar)
        self.text_area = QTextBrowser()
        self.text_area.setOpenExternalLinks(True)
        layout.addWidget(self.text_area)

    def update_dir_label(self):
        if self.save_dir:
            self.dir_label.setText(f"目录: {self.save_dir}")
        else:
            self.dir_label.setText("目录: (未设置)")

    def fetch_ip(self):
        self.worker = DataWorker("ip")
        self.worker.result_signal.connect(
            lambda res: self.ip_label.setText(f"📍 属地: {res['data']}" if res['success'] else "定位失败"))
        self.worker.start()

    def choose_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹", self.save_dir or "")
        if folder:
            self.save_dir = folder
            self.settings.setValue("user_save_dir", folder)
            self.update_dir_label()

    def view_single_country(self):
        url = COUNTRY_CONFIGS[self.country_combo.currentText()]["url"]
        self.pbar.show()
        self.pbar.setRange(0, 0)
        self.worker = DataWorker("news", url=url)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, res):
        self.pbar.hide()
        if res["success"]:
            self.display_markdown(res["data"])
        else:
            self.text_area.setText("获取失败")

    def display_markdown(self, news_list):
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        text = f"# 📅 每日汇报\n**日期**: {date_str} | **地区**: {self.country_combo.currentText()}\n\n---\n"
        for i, item in enumerate(news_list, 1):
            text += f"{i}. **[{item['title']}]({item['link']})**\n   *来源: {item['source']}*\n\n"
        self.text_area.setMarkdown(text)

    def export_all_countries(self):
        if not self.save_dir:
            QMessageBox.warning(self, "提示", "请先设置目录！")
            self.choose_directory()
            return
        self.pbar.show()
        self.pbar.setRange(0, 100)
        self.batch_worker = BatchExportWorker()
        self.batch_worker.progress_signal.connect(
            lambda msg, val: (self.pbar.setValue(val), self.text_area.append(msg)))
        self.batch_worker.finished_signal.connect(self.save_file)
        self.batch_worker.start()

    def save_file(self, content):
        self.pbar.hide()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        path = os.path.join(self.save_dir, f"{date_str}.txt")
        header = f"【全球重点新闻汇总】\n日期: {date_str}\n{self.ip_label.text()}\n{'=' * 50}\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(header + content)
        QMessageBox.information(self, "成功", f"文件已保存:\n{path}")