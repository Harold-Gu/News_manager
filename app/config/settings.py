# app/config/settings.py

# 国家/地区配置 (Google News RSS 参数)
COUNTRY_CONFIGS = {
    "中国 (CN)": {"code": "CN", "url": "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-CN"},
    "美国 (US)": {"code": "US", "url": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"},
    "英国 (UK)": {"code": "GB", "url": "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en"},
    "日本 (JP)": {"code": "JP", "url": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"}
}

# API 服务地址
IP_API_URL = "https://api.ipify.org?format=json"