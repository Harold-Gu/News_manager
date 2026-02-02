import os
from PyQt6.QtCore import QSettings, Qt, QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QTextEdit, QGroupBox,
                             QMessageBox, QFileDialog, QDateEdit, QSplitter)
from PyQt6.QtGui import QPixmap, QImage
from app.config.settings import COUNTRY_CONFIGS
from app.core.workers import WordCloudWorker


class WordCloudWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("ReportTeam", "DailyReportAssistant")
        self.current_image = None  # 存储生成的 PIL Image 对象
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 1. 控制区
        ctrl_group = QGroupBox("热点分析配置")
        ctrl_layout = QHBoxLayout()

        ctrl_layout.addWidget(QLabel("地区:"))
        self.country_combo = QComboBox()
        self.country_combo.addItems(COUNTRY_CONFIGS.keys())
        ctrl_layout.addWidget(self.country_combo)

        ctrl_layout.addWidget(QLabel("热词语言:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("中文 (Chinese)", "zh-CN")
        self.lang_combo.addItem("英文 (English)", "en")
        ctrl_layout.addWidget(self.lang_combo)

        self.btn_gen = QPushButton("🔥 生成热词图")
        self.btn_gen.clicked.connect(self.generate_cloud)
        ctrl_layout.addWidget(self.btn_gen)

        self.btn_save = QPushButton("💾 保存结果")
        self.btn_save.setObjectName("btn_accent")
        self.btn_save.clicked.connect(self.save_results)
        self.btn_save.setEnabled(False)
        ctrl_layout.addWidget(self.btn_save)

        ctrl_layout.addStretch()
        ctrl_group.setLayout(ctrl_layout)
        layout.addWidget(ctrl_group)

        # 2. 展示区 (左边图片，右边文字)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 图片展示
        self.img_label = QLabel("等待生成...")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet("border: 2px dashed #45475A; background-color: #181825;")
        self.img_label.setMinimumSize(400, 300)
        splitter.addWidget(self.img_label)

        # 文字列表
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("关键词列表将显示在这里...")
        splitter.addWidget(self.text_area)

        splitter.setStretchFactor(0, 3)  # 图片占大头
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def generate_cloud(self):
        country = self.country_combo.currentText()
        url = COUNTRY_CONFIGS[country]["url"]
        target_lang = self.lang_combo.currentData()

        self.btn_gen.setEnabled(False)
        self.img_label.setText(f"正在分析 {country} 的热点数据...\n可能需要几秒钟...")

        self.worker = WordCloudWorker(url, target_lang)
        self.worker.finished_signal.connect(self.handle_result)
        self.worker.start()

    def handle_result(self, image, text_result):
        self.btn_gen.setEnabled(True)
        if image:
            self.current_image = image
            self.current_text = text_result

            # 显示文本
            self.text_area.setText(text_result)

            # 显示图片 (PIL Image -> QPixmap)
            data = image.tobytes("raw", "RGB")
            qim = QImage(data, image.width, image.height, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)
            self.img_label.setPixmap(pixmap.scaled(
                self.img_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.img_label.setText("")  # 清除文字
            self.btn_save.setEnabled(True)
        else:
            self.img_label.setText(f"失败: {text_result}")

    def save_results(self):
        save_dir = self.settings.value("user_save_dir")
        if not save_dir:
            QMessageBox.warning(self, "提示", "请先在【日报界面】设置保存目录！")
            return

        date_str = QDate.currentDate().toString("yyyy-MM-dd")
        country = self.country_combo.currentText().split(' ')[0]  # 取"中国"

        # 文件名
        txt_name = f"{date_str}_{country}_热词.txt"
        img_name = f"{date_str}_{country}_词云.png"

        txt_path = os.path.join(save_dir, txt_name)
        img_path = os.path.join(save_dir, img_name)

        try:
            # 保存图片
            self.current_image.save(img_path)
            # 保存文本
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.current_text)

            QMessageBox.information(self, "保存成功", f"已保存到目录:\n图片: {img_name}\n文本: {txt_name}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))