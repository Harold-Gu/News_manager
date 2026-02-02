import requests
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator
from app.config.settings import IP_API_URL


def fetch_ip_address():
    """获取IP及地理位置"""
    try:
        response = requests.get(IP_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                country = data.get("country", "")
                region = data.get("regionName", "")
                city = data.get("city", "")
                location = f"{country}"
                if region and region != country:
                    location += f" {region}"
                if city and city != region:
                    location += f" {city}"
                return location
            else:
                return "位置未知"
    except Exception as e:
        print(f"Location Fetch Error: {e}")
        return None


def translate_text(text, target_lang='zh-CN'):
    """
    通用翻译函数
    target_lang: 'zh-CN' (中文) 或 'en' (英文)
    """
    # 简单优化：如果是中文且目标也是中文，直接返回
    is_chinese = any('\u4e00' <= ch <= '\u9fff' for ch in text)
    if target_lang == 'zh-CN' and is_chinese:
        return text

    # 如果目标是英文，且原文看起来像英文(简单判断)，也可以直接返回(视情况而定)

    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text


def fetch_news_titles(rss_url):
    """
    只获取新闻标题，用于词云分析
    """
    titles = []
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # 获取前 20 条以增加词云丰富度
            for item in root.findall('./channel/item')[:20]:
                title = item.find('title').text
                # 去掉来源后缀 (例如 " - CNN")
                clean_title = title.split(' - ')[0] if title else ""
                if clean_title:
                    titles.append(clean_title)
    except Exception as e:
        print(f"RSS Fetch Error: {e}")
    return titles


def fetch_news_data(rss_url, do_translate=False):
    """
    保留原有逻辑，用于日报展示
    """
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            news_items = []
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text
                link = item.find('link').text
                clean_title = title.split(' - ')[0] if title else "无标题"
                source = title.split(' - ')[-1] if ' - ' in title else "未知"

                final_title = clean_title
                if do_translate:
                    # 日报默认翻译成中文
                    final_title = f"{clean_title} / {translate_text(clean_title, 'zh-CN')}"

                news_items.append({
                    "title": final_title,
                    "source": source,
                    "link": link
                })
            return news_items
    except Exception as e:
        print(f"News Fetch Error: {e}")
    return []