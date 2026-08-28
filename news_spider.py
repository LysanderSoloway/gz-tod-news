import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KEYWORD_FILTERS = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路', '站城', '高铁', '轨道交通', '上盖']

def fetch_news():
    logging.info("🤖 小机器人开始干活啦！（最终版）")
    
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        logging.info(f"📚 加载现有数据 {len(all_news)} 条")
    except FileNotFoundError:
        all_news = []
        logging.info("📚 从零开始")

    existing_keys = {item["标题"][:20] + item.get("链接", "")[:50] for item in all_news}

    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
    except FileNotFoundError:
        logging.error("❌ 找不到 sources.json")
        return

    new_count = 0
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })

    for src in sources:
        name = src['name']
        base_url = src['url']
        selector = src.get('select', 'a')
        limit = src.get('limit_per_page', 10)
        pages = src.get('pages', 1)
        encoding = src.get('encoding', 'utf-8')

        logging.info(f"🔍 正在抓取: {name}")

        for page in range(1, pages + 1):
            page_url = base_url if page == 1 else (base_url + f'&page={page}' if '?' in base_url else base_url + f'?page={page}')

            try:
                resp = session.get(page_url, timeout=20)
                resp.encoding = encoding
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select(selector)

                if not items:
                    continue

                count = 0
                for item in items[:limit]:
                    raw_title = item.text.strip()
                    link = item.get('href')
                    if not raw_title or not link or len(raw_title) < 6:
                        continue

                    if not any(k in raw_title for k in KEYWORD_FILTERS):
                        continue

                    # 清理标题：只取前15个字，保证绝对没有尾巴
                    title = raw_title[:15].strip()
                    if len(raw_title) > 15:
                        title += '...'

                    full_link = urljoin(page_url, link)

                    key = title[:20] + full_link[:50]
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)

                    publish_date = datetime.now().strftime("%Y-%m-%d")

                    scope = "全国"
                    if any(w in raw_title for w in ["世界", "国际", "全球"]):
                        scope = "世界"
                    elif "广州" in raw_title:
                        scope = "广州市"
                    elif any(w in raw_title for w in ["广东", "深圳", "佛山", "东莞", "中山", "珠海"]):
                        scope = "广东省"

                    news_type = "综合"
                    type_map = {
                        "项目建设进展": ["封顶", "开工", "竣工", "通车", "开通", "投运", "动工", "建设", "进展", "完成", "交付", "贯通"],
                        "规划公示/获批": ["规划", "公示", "获批", "审议", "通过", "方案", "批复", "可研", "立项"],
                        "政策/行业观点": ["政策", "出台", "发布", "意见", "办法", "条例", "观点", "论坛", "会议"],
                        "商业配套/招商": ["商业", "招商", "商场", "签约", "入驻", "开业"],
                        "投融资": ["投资", "融资", "资本", "基金", "授信", "债券", "REITs", "PPP"],
                        "可持续经营运营": ["可持续", "经营", "运营", "营收", "盈利", "客流"]
                    }
                    for t, kws in type_map.items():
                        if any(kw in raw_title for kw in kws):
                            news_type = t
                            break

                    keywords = []
                    kw_map = {
                        '国铁': ['高铁', '铁路', '国铁', '动车'],
                        '城际': ['城际'],
                        '地铁': ['地铁'],
                        '轨道': ['轨道', '轨交', '轻轨'],
                        '综合交通枢纽': ['枢纽'],
                        '综合开发': ['TOD', '综合开发', '上盖', '站城'],
                        '投融资': ['融资', '投资', '资本', '基金'],
                        '可持续经营运营': ['可持续', '经营', '运营']
                    }
                    for kw, words in kw_map.items():
                        if any(w in raw_title for w in words):
                            keywords.append(kw)
                    if not keywords:
                        keywords = ["轨道"]

                    all_news.append({
                        "日期": publish_date,
                        "标题": title,
                        "链接": full_link,
                        "来源": name,
                        "范围": scope,
                        "关键词": keywords,
                        "摘要": title,
                        "类型": news_type
                    })
                    count += 1
                    new_count += 1
                    time.sleep(random.uniform(0.2, 0.5))

                logging.info(f"✅ {name} 第 {page} 页新增 {count} 条")

            except Exception as e:
                logging.error(f"❌ {name} 第 {page} 页出错: {e}")

            time.sleep(random.uniform(0.5, 1.5))

        time.sleep(random.uniform(1.0, 2.0))

    all_news.sort(key=lambda x: x["日期"], reverse=True)

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

    logging.info(f"🎉 完成！新增 {new_count} 条，共 {len(all_news)} 条")

if __name__ == "__main__":
    fetch_news()
