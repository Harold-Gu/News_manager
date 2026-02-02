# app/core/workers.py
from PyQt6.QtCore import QThread, pyqtSignal
from app.core.api import fetch_ip_address, fetch_news_data
from app.config.settings import COUNTRY_CONFIGS
import time


class DataWorker(QThread):
    """单次任务线程 (查IP 或 查单国新闻)"""
    result_signal = pyqtSignal(dict)

    def __init__(self, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.params = kwargs

    def run(self):
        result = {"type": self.task_type, "success": False, "data": None}

        if self.task_type == "ip":
            ip = fetch_ip_address()
            if ip:
                result["success"] = True
                result["data"] = ip
            else:
                result["error"] = "网络请求失败"

        elif self.task_type == "news":
            url = self.params.get("url")
            # 单次查看时，我们也可以选择开启翻译，这里暂时设为False提高速度，
            # 或者设为 True 让用户看单国时也有翻译
            news_list = fetch_news_data(url, do_translate=True)
            if news_list:
                result["success"] = True
                result["data"] = news_list
            else:
                result["error"] = "RSS解析失败或超时"

        self.result_signal.emit(result)


class BatchExportWorker(QThread):
    """
    批量导出线程
    循环抓取所有国家新闻 -> 翻译 -> 汇总
    """
    progress_signal = pyqtSignal(str, int)  # 发送当前状态文本和百分比
    finished_signal = pyqtSignal(str)  # 发送最终汇总文本

    def run(self):
        full_content = ""
        total_countries = len(COUNTRY_CONFIGS)

        for index, (name, config) in enumerate(COUNTRY_CONFIGS.items(), 1):
            # 发送进度信号
            percent = int((index / total_countries) * 100)
            self.progress_signal.emit(f"正在获取并翻译: {name} ...", percent)

            # 抓取并强制翻译
            news_list = fetch_news_data(config["url"], do_translate=True)

            # 拼接到大文本中
            full_content += f"\n## 🌍 {name}\n"
            if news_list:
                for i, item in enumerate(news_list, 1):
                    full_content += f"{i}. {item['title']}\n"
            else:
                full_content += "   (获取失败)\n"

            # 稍微休眠一下，防止请求过快被封IP
            time.sleep(0.5)

        self.finished_signal.emit(full_content)