from PyQt6.QtCore import QThread, pyqtSignal
from app.core.api import fetch_ip_address, fetch_news_data, fetch_news_titles, translate_text
from app.config.settings import COUNTRY_CONFIGS
import time
import jieba
import jieba.analyse
from wordcloud import WordCloud
import io


class DataWorker(QThread):
    """单次任务线程 (IP 或 日报新闻)"""
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
            news_list = fetch_news_data(url, do_translate=True)
            if news_list:
                result["success"] = True
                result["data"] = news_list
            else:
                result["error"] = "RSS解析失败或超时"

        self.result_signal.emit(result)


class BatchExportWorker(QThread):
    """批量导出全球日报线程"""
    progress_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(str)

    def run(self):
        full_content = ""
        total_countries = len(COUNTRY_CONFIGS)

        for index, (name, config) in enumerate(COUNTRY_CONFIGS.items(), 1):
            percent = int((index / total_countries) * 100)
            self.progress_signal.emit(f"正在获取并翻译: {name} ...", percent)
            news_list = fetch_news_data(config["url"], do_translate=True)

            full_content += f"\n## 🌍 {name}\n"
            if news_list:
                for i, item in enumerate(news_list, 1):
                    full_content += f"{i}. {item['title']}\n   [链接]: {item['link']}\n"
            else:
                full_content += "   (获取失败)\n"
            time.sleep(0.5)

        self.finished_signal.emit(full_content)


class WordCloudWorker(QThread):
    """
    词云生成线程
    1. 抓取标题
    2. 翻译 (根据用户选择 En/Cn)
    3. 提取关键词
    4. 生成图片对象
    """
    finished_signal = pyqtSignal(object, str)  # 返回 (Image对象, 关键词文本)

    def __init__(self, rss_url, target_lang):
        super().__init__()
        self.rss_url = rss_url
        self.target_lang = target_lang  # 'zh-CN' or 'en'

    def run(self):
        # 1. 抓取
        raw_titles = fetch_news_titles(self.rss_url)
        if not raw_titles:
            self.finished_signal.emit(None, "获取RSS失败")
            return

        # 2. 翻译与拼接
        full_text = ""
        for title in raw_titles:
            # 如果需要中文词云，就翻译成中文；英文同理
            trans = translate_text(title, self.target_lang)
            full_text += trans + " "

        # 3. 提取关键词 (使用 jieba)
        # topK=20: 提取前20个关键词
        keywords_list = jieba.analyse.extract_tags(full_text, topK=20, withWeight=True)
        # keywords_list 结构: [('Trump', 0.8), ('Economy', 0.5)...]

        # 转换成字典供 WordCloud 使用
        freq_dict = {word: weight for word, weight in keywords_list}

        # 生成关键词文本报告
        keywords_str = "【今日热词 Top 20】\n"
        for word, weight in keywords_list:
            keywords_str += f"- {word} (权重: {weight:.2f})\n"

        # 4. 生成词云图片

        try:
            # Windows下必须指定中文字体路径，否则中文会显示乱码
                # 微软雅黑 (msyh.ttc) 是 Windows 标配
            font_path = "C:/Windows/Fonts/msyh.ttc"

            wc = WordCloud(
                font_path=font_path,
                # 1. 增大画布尺寸，给文字更多空间
                width=1000,
                height=800,

                    # 2. 背景色
                background_color='white',

                    # 3. 减少显示的词数 (从50减到30)，少即是多，避免拥挤
                max_words=30,

                    # 4. 【关键】增加词与词之间的间距 (默认是0，改成 5 或 10)
                margin=5,

                    # 5. 最小字号，防止出现看不清的蚂蚁字
                min_font_size=15,

                    # 6. 词频关联度 (0-1)，越大则高频词越大，拉开视觉差距
                relative_scaling=0.6,

                    # 7. 尽量让文字水平排列 (0.9 表示 90% 的词是水平的)，垂直文字容易造成视觉混乱
                prefer_horizontal=0.9,

                    # 8. 颜色系 (可选，tab10 颜色对比度较高)
                colormap='tab10'
            )

            wc.generate_from_frequencies(freq_dict)
            image = wc.to_image()  # 转换为 PIL Image 对象

            self.finished_signal.emit(image, keywords_str)

        except Exception as e:
            self.finished_signal.emit(None, f"生成词云出错: {str(e)}")