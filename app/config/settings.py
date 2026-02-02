# app/config/settings.py
import os

# 全球主流国家/地区配置 (Google News RSS)
# 格式: "显示名称": {"code": "地区代码", "hl": "语言代码", "gl": "地理位置", "ceid": "参数"}
# 提示：Google News URL 结构通常为 https://news.google.com/rss?hl={hl}&gl={gl}&ceid={ceid}

COUNTRY_CONFIGS = {
    "中国 (CN)": {"url": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-CN"},
    "美国 (US)": {"url": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"},
    "英国 (UK)": {"url": "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en"},
    "日本 (JP)": {"url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"},
    "德国 (DE)": {"url": "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de"},
    "法国 (FR)": {"url": "https://news.google.com/rss?hl=fr&gl=FR&ceid=FR:fr"},
    "俄罗斯 (RU)": {"url": "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru"},
    "韩国 (KR)": {"url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"},
    "印度 (IN)": {"url": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"},
    "澳大利亚 (AU)": {"url": "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en"},
    "加拿大 (CA)": {"url": "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en"},
    "巴西 (BR)": {"url": "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"},
}

IP_API_URL = "https://api.ipify.org?format=json"

# 默认保存目录配置键名 (可扩展用于保存用户配置)
DEFAULT_SAVE_DIR = None