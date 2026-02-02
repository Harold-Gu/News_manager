from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QMenuBar)
from PyQt6.QtGui import QAction
from app.ui.daily_report import DailyReportWidget
from app.ui.word_cloud_window import WordCloudWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("全球每日重点汇报助手 (Pro Max)")
        self.resize(1000, 800)

        # 1. 创建堆叠窗口 (用于切换界面)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 2. 初始化两个子界面
        self.report_widget = DailyReportWidget()
        self.cloud_widget = WordCloudWidget()

        self.stack.addWidget(self.report_widget)  # Index 0
        self.stack.addWidget(self.cloud_widget)  # Index 1

        # 3. 创建顶部菜单栏
        menu_bar = self.menuBar()

        # 视图菜单
        view_menu = menu_bar.addMenu("📺 切换视图")

        # 动作：切换到日报
        action_report = QAction("📋 每日汇报界面", self)
        action_report.triggered.connect(lambda: self.switch_view(0))
        view_menu.addAction(action_report)

        # 动作：切换到热词
        action_cloud = QAction("🔥 热点词云分析", self)
        action_cloud.triggered.connect(lambda: self.switch_view(1))
        view_menu.addAction(action_cloud)

        # 默认显示第一个界面
        self.switch_view(0)

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)