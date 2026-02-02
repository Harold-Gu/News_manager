# app/core/api.py
import requests
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from app.config.settings import IP_API_URL


def fetch_ip_address():
    """获取公网IP"""
    try:
        response = requests.get(IP_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception:
        return None


def translate_title(text):
    """
    如果文本包含中文字符，则直接返回。
    否则翻译成中文，并返回 '原文 / 译文' 格式。
    """
    # 简单判断是否包含中文
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return text  # 已经是中文，直接返回

    try:
        # 使用 Google 翻译源
        translator = GoogleTranslator(source='auto', target='zh-CN')
        translated = translator.translate(text)
        return f"{text} / {translated}"
    except Exception as e:
        print(f"Translation Error: {e}")
        return text  # 翻译失败返回原文


def fetch_news_data(rss_url, do_translate=False):
    """
    获取并解析新闻RSS
    do_translate: 是否开启翻译功能 (用于导出汇总时)
    """
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            news_items = []
            # 获取前 20 条 (为了速度，如果导出全球新闻，建议限制条数)
            for item in root.findall('./channel/item')[:20]:
                title = item.find('title').text
                clean_title = title.split(' - ')[0] if title else "无标题"
                source = title.split(' - ')[-1] if ' - ' in title else "未知"

                final_title = clean_title
                if do_translate:
                    final_title = translate_title(clean_title)

                news_items.append({
                    "title": final_title,
                    "source": source,
                })
            return news_items
    except Exception as e:
        print(f"News Fetch Error: {e}")
    return []