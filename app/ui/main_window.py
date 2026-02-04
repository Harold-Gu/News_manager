import os
from datetime import datetime
from PyQt6.QtCore import QSettings, QDate, Qt
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextBrowser,
                             QProgressBar, QGroupBox, QMessageBox, QFileDialog,
                             QDateEdit, QSystemTrayIcon, QMenu, QApplication, QStyle)
from PyQt6.QtGui import QAction, QIcon
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import DataWorker, BatchExportWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化配置管理器
        self.settings = QSettings("ReportTeam", "DailyReportAssistant")
        self.save_dir = self.settings.value("user_save_dir")

        self.init_ui()
        self.init_system_tray()  # <--- 1. 初始化系统托盘

        # 启动时自动查询地理位置
        self.fetch_ip()

    def init_ui(self):
        self.setWindowTitle("全球每日重点汇报助手 (System Tray Edition)")
        self.resize(950, 750)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # === 顶部区域 ===
        top_group = QGroupBox("环境与设置")
        top_layout = QHBoxLayout()

        self.ip_label = QLabel("📍 属地: 定位中...")
        refresh_btn = QPushButton("刷新位置")
        refresh_btn.clicked.connect(self.fetch_ip)

        self.dir_label = QLabel()
        if self.save_dir:
            self.dir_label.setText(f"保存目录: {self.save_dir}")
        else:
            self.dir_label.setText("保存目录: (未设置)")

        self.btn_set_dir = QPushButton("📂 设置目录")
        self.btn_set_dir.clicked.connect(self.choose_directory)

        top_layout.addWidget(self.ip_label)
        top_layout.addWidget(refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.dir_label)
        top_layout.addWidget(self.btn_set_dir)
        top_group.setLayout(top_layout)
        layout.addWidget(top_group)

        # === 中部操作区域 ===
        ctrl_group = QGroupBox("汇报操作")
        ctrl_layout = QHBoxLayout()

        ctrl_layout.addWidget(QLabel("日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedWidth(120)
        ctrl_layout.addWidget(self.date_edit)

        ctrl_layout.addSpacing(20)
        ctrl_layout.addWidget(QLabel("地区:"))
        self.country_combo = QComboBox()
        self.country_combo.addItems(COUNTRY_CONFIGS.keys())
        ctrl_layout.addWidget(self.country_combo)

        self.btn_view = QPushButton("👀 查看该国日报")
        self.btn_view.clicked.connect(self.view_single_country)
        ctrl_layout.addWidget(self.btn_view)

        ctrl_layout.addStretch()
        self.btn_export_all = QPushButton("💾 按日期保存全球日报 (.txt)")
        self.btn_export_all.setObjectName("btn_accent")
        self.btn_export_all.clicked.connect(self.export_all_countries)
        ctrl_layout.addWidget(self.btn_export_all)

        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # === 底部显示区域 ===
        self.pbar = QProgressBar()
        self.pbar.hide()
        layout.addWidget(self.pbar)

        self.text_area = QTextBrowser()
        self.text_area.setPlaceholderText("等待操作...")
        self.text_area.setOpenExternalLinks(True)
        layout.addWidget(self.text_area)

    # =======================================================
    # 👇 新增功能：系统托盘初始化
    # =======================================================
    def init_system_tray(self):
        """配置系统托盘图标和菜单"""
        self.tray_icon = QSystemTrayIcon(self)

        # 使用系统自带的电脑图标（为了防止你没有图标文件报错）
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("日报助手 (运行中)")

        # --- 创建右键菜单 ---
        tray_menu = QMenu()

        # 1. 显示主界面
        show_action = QAction("显示主界面", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        # 2. 真正退出程序
        quit_action = QAction("退出程序", self)
        # 注意：这里连接的是 QApplication 的 quit，用于彻底杀死进程
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # --- 处理左键点击 (点击图标恢复窗口) ---
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    # =======================================================
    # 👇 核心修改：拦截关闭事件
    # =======================================================
    def closeEvent(self, event):
        """当用户点击窗口右上角的 X 时触发"""
        if self.tray_icon.isVisible():
            # 不真正退出，而是隐藏窗口
            self.hide()

            # 告诉系统“忽略”这次关闭请求
            event.ignore()

            # 可选：弹个气泡提示一下用户（防止用户以为真关了）
            self.tray_icon.showMessage(
                "日报助手已最小化",
                "程序仍在后台运行，右键托盘图标可彻底退出。",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            # 如果托盘图标没显示（异常情况），则允许关闭
            event.accept()

    def on_tray_icon_activated(self, reason):
        """处理托盘图标的点击事件"""
        # 如果是单击 (Trigger) 或 双击 (DoubleClick)
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()  # 恢复显示
            self.activateWindow()  # 将窗口置顶拿到焦点

    # =======================================================
    # 👇 原有业务逻辑 (保持不变)
    # =======================================================
    def fetch_ip(self):
        self.ip_label.setText("📍 属地: 定位中...")
        self.worker = DataWorker("ip")
        self.worker.result_signal.connect(self.handle_single_result)
        self.worker.start()

    def choose_directory(self):
        default_open = self.save_dir if self.save_dir else ""
        folder = QFileDialog.getExistingDirectory(self, "选择保存日报的文件夹", default_open)
        if folder:
            self.save_dir = folder
            self.dir_label.setText(f"保存目录: {folder}")
            self.settings.setValue("user_save_dir", folder)
            return True
        return False

    def view_single_country(self):
        key = self.country_combo.currentText()
        url = COUNTRY_CONFIGS[key]["url"]
        self.btn_view.setEnabled(False)
        self.pbar.show()
        self.pbar.setRange(0, 0)
        self.worker = DataWorker("news", url=url)
        self.worker.result_signal.connect(self.handle_single_result)
        self.worker.start()

    def export_all_countries(self):
        if not self.save_dir:
            QMessageBox.warning(self, "提示", "请先指定保存文件的目录！")
            if not self.choose_directory():
                return
        self.btn_export_all.setEnabled(False)
        self.btn_view.setEnabled(False)
        self.text_area.clear()
        self.pbar.show()
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.batch_worker = BatchExportWorker()
        self.batch_worker.progress_signal.connect(self.update_export_progress)
        self.batch_worker.finished_signal.connect(self.save_export_file)
        self.batch_worker.start()

    def handle_single_result(self, res):
        self.btn_view.setEnabled(True)
        self.pbar.hide()
        if res["type"] == "ip":
            self.ip_label.setText(f"📍 属地: {res['data']}" if res['success'] else "📍 属地: 获取失败")
        elif res["type"] == "news":
            if res["success"]:
                self.display_markdown(res["data"])
            else:
                self.text_area.setText("获取失败，请检查网络连接。")

    def update_export_progress(self, msg, val):
        self.pbar.setValue(val)
        self.pbar.setFormat(msg)
        self.text_area.append(msg)

    def display_markdown(self, news_list):
        country = self.country_combo.currentText()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        text = f"# 📅 每日汇报\n**日期**: {date_str} | **地区**: {country}\n\n---\n"
        for i, item in enumerate(news_list, 1):
            text += f"{i}. **[{item['title']}]({item['link']})**\n   *来源: {item['source']}*\n\n"
        self.text_area.setMarkdown(text)

    def save_export_file(self, full_content):
        self.btn_export_all.setEnabled(True)
        self.btn_view.setEnabled(True)
        self.pbar.hide()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        file_name = f"{date_str}.txt"
        file_path = os.path.join(self.save_dir, file_name)
        header = f"【全球重点新闻汇总】\n日期: {date_str}\n{self.ip_label.text()}\n"
        final_text = header + ("=" * 50) + full_content
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            self.text_area.setMarkdown(f"# ✅ 导出成功\n\n文件已保存至:\n`{file_path}`\n\n---\n{full_content}")
            QMessageBox.information(self, "成功", f"全球新闻已保存至：\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))