# app/core/api.py
import requests
import xml.etree.ElementTree as ET
from app.config.settings import IP_API_URL


def fetch_ip_address():
    """获取公网IP"""
    try:
        response = requests.get(IP_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json().get("ip")
    except Exception as e:
        print(f"IP Fetch Error: {e}")
    return None


def fetch_news_data(rss_url):
    """获取并解析新闻RSS"""
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            news_items = []
            # 提取前 10 条
            for item in root.findall('./channel/item')[:10]:
                title = item.find('title').text
                # 处理一下标题，去掉来源后缀
                clean_title = title.split(' - ')[0] if title else "无标题"
                source = title.split(' - ')[-1] if ' - ' in title else "未知"

                news_items.append({
                    "title": clean_title,
                    "source": source,
                })
            return news_items
    except Exception as e:
        print(f"News Fetch Error: {e}")
    return None