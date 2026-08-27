import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_news():
    print("🤖 小机器人开始干活啦！（地基版）")

    all_news = []
    existing_titles = set()
    new_count = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # 只抓取一个最稳定的网站
    sources = [
        {"name": "中国TOD网", "url": "https://www.chinatod.com.cn/index.php?m=content&c=index&a=lists&catid=36", "select": "a[title]", "limit": 15},
    ]

    keyword_filters = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路']

    for src in sources:
        try:
            print(f"正在访问 {src['name']}...")
            r = requests.get(src['url'], headers=headers, timeout=15)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(src['select'])
            count = 0
            for item in items[:src['limit']]:
                title = item.text.strip()
                link = item.get('href')
                if not title or not link or len(title) < 6:
                    continue
                if "监测月报" in title:
                    continue
                if not any(k in title for k in keyword_filters):
                    continue
                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = 'https://www.chinatod.com.cn' + link
                    else:
                        link = src['url'].rstrip('/') + '/' + link.lstrip('/')
                # 去重
                key = title[:20]
                if key in existing_titles:
                    continue
                existing_titles.add(key)
                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title,
                    "链接": link,
                    "来源": src['name'],
                    "范围": "全国",
                    "关键词": ["综合开发"],
                    "摘要": title[:80],
                    "类型": "综合"
                })
                count += 1
                new_count += 1
            print(f"✅ {src['name']} 新增 {count} 条")
        except Exception as e:
            print(f"❌ {src['name']} 出错: {e}")

    all_news.sort(key=lambda x: x["日期"], reverse=True)

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

    print(f"🎉 共 {len(all_news)} 条新闻，新增 {new_count} 条")

if __name__ == "__main__":
    fetch_news()
