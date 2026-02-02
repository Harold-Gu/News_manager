# app/core/workers.py
from PyQt6.QtCore import QThread, pyqtSignal
from app.core.api import fetch_ip_address, fetch_news_data


class DataWorker(QThread):
    """
    通用工作线程
    task_type: 'ip' or 'news'
    params: 字典参数
    """
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
            news_list = fetch_news_data(url)
            if news_list:
                result["success"] = True
                result["data"] = news_list
            else:
                result["error"] = "RSS解析失败或超时"

        self.result_signal.emit(result)
