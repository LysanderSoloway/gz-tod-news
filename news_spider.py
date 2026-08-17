import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

# ============================================================
# 第一部分：新闻抓取规则（您以后只需在这里增删网站）
# ============================================================
def fetch_news():
    print("🤖 小机器人开始干活啦！")
    all_news = []
    two_years_ago = datetime.now() - timedelta(days=730)

    # 1. 从中国TOD网抓取（最稳定）
    try:
        print("正在访问中国TOD网...")
        url = "https://www.chinatod.com.cn/index.php?m=content&c=index&a=lists&catid=36"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for item in soup.select('a[title]')[:15]:  # 找带标题的链接
            title = item.text.strip()
            link = item.get('href')
            if title and link and ('TOD' in title or '综合开发' in title or '枢纽' in title):
                if not link.startswith('http'):
                    link = 'https://www.chinatod.com.cn' + link
                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title,
                    "链接": link,
                    "来源": "中国TOD网",
                    "范围": "全国",  # 稍后自动判断
                    "摘要": ""
                })
        print(f"✅ 中国TOD网抓到了 {len(all_news)} 条")
    except Exception as e:
        print(f"❌ 中国TOD网出错了：{e}")

    # 2. 从广州市规划和自然资源局抓取（规划公示很权威）
    try:
        print("正在访问广州规划局...")
        url = "https://ghzyj.gz.gov.cn/ywpd/cxgh/ghxkgsgb/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for item in soup.select('ul.list li a')[:10]:
            title = item.text.strip()
            link = item.get('href')
            if title and link:
                if not link.startswith('http'):
                    link = 'https://ghzyj.gz.gov.cn' + link
                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title,
                    "链接": link,
                    "来源": "广州市规划和自然资源局",
                    "范围": "广州市",
                    "摘要": ""
                })
        print(f"✅ 广州规划局抓到了 若干 条")
    except Exception as e:
        print(f"❌ 广州规划局出错了：{e}")

    # ============================================================
    # 核心功能：自动判断“范围”（世界/全国/广东省/广州市）
    # ============================================================
    final_list = []
    for item in all_news:
        text = item["标题"] + item.get("摘要", "")
        
        # 判断范围
        if "世界" in text or "国际" in text or "全球" in text or "越南" in text or "马来西亚" in text:
            item["范围"] = "世界"
        elif "广东" in text or "深圳" in text or "佛山" in text or "东莞" in text:
            item["范围"] = "广东省"
        elif "广州" in text:
            item["范围"] = "广州市"
        else:
            item["范围"] = "全国"
        
        # 提取关键词（国铁、城际、地铁等）
        keywords = []
        kw_map = {
            '国铁': ['高铁', '铁路', '国铁'],
            '城际': ['城际'],
            '地铁': ['地铁'],
            '轨道': ['轨道', '轨交'],
            '综合交通枢纽': ['枢纽'],
            '综合开发': ['TOD', '综合开发', '上盖', '站城']
        }
        for kw, words in kw_map.items():
            for w in words:
                if w in text:
                    keywords.append(kw)
                    break
        if not keywords:
            keywords.append("轨道")
        item["关键词"] = keywords
        
        final_list.append(item)

    # 去重（防止同一条新闻抓两次）
    seen_titles = set()
    unique_list = []
    for item in final_list:
        if item["标题"] not in seen_titles:
            seen_titles.add(item["标题"])
            unique_list.append(item)

    # 保存结果
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(unique_list, f, ensure_ascii=False, indent=2)

    print(f"🎉 大功告成！总共抓取了 {len(unique_list)} 条新闻！")
    return unique_list

# 让机器人开始工作
if __name__ == "__main__":
    fetch_news()
