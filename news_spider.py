import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# ============================================================
# 分类规则
# ============================================================
TYPE_RULES = {
    "项目建设进展": ["封顶", "开工", "竣工", "通车", "开通", "投运", "动工", "推进", "建设", "进展", "完成", "交付", "贯通", "合龙", "施工"],
    "规划公示/获批": ["规划", "公示", "获批", "审议", "通过", "方案", "批复", "可研", "立项", "选址"],
    "政策/行业观点": ["政策", "出台", "发布", "意见", "办法", "条例", "观点", "论坛", "会议", "座谈", "解读", "建议"],
    "商业配套/招商": ["商业", "招商", "商场", "商业配套", "签约", "入驻", "开业", "品牌", "零售"],
    "投融资": ["投资", "融资", "资本", "基金", "授信", "债券", "REITs", "PPP", "资金", "亿元", "万亿", "贷款"],
    "可持续经营运营": ["可持续", "经营", "运营", "营收", "盈利", "客流", "票务", "多元化", "造血"]
}

# ============================================================
# 自动生成摘要函数
# ============================================================
def generate_summary(title, source=""):
    if not title:
        return ""
    clean_title = re.sub(r'^.*?[：:]', '', title)
    if len(clean_title) < 10:
        return clean_title
    keywords = []
    if "高铁" in clean_title or "铁路" in clean_title:
        keywords.append("国铁")
    if "城际" in clean_title:
        keywords.append("城际")
    if "地铁" in clean_title:
        keywords.append("地铁")
    if "TOD" in clean_title or "综合开发" in clean_title:
        keywords.append("综合开发")
    if "枢纽" in clean_title:
        keywords.append("枢纽")
    if keywords:
        return f"{clean_title[:60]}（涉及{'、'.join(keywords[:3])}）"
    else:
        return clean_title[:80] + ("..." if len(clean_title) > 80 else "")

def classify_news(title, summary=""):
    text = title + summary
    for cat, keywords in TYPE_RULES.items():
        for kw in keywords:
            if kw in text:
                return cat
    return "综合"

def extract_scope(title, content=""):
    text = title + content
    if "世界" in text or "国际" in text or "全球" in text:
        return "世界"
    elif "广东" in text or "深圳" in text or "佛山" in text or "东莞" in text or "珠海" in text:
        if "广州" in text:
            return "广州市"
        return "广东省"
    elif "广州" in text:
        return "广州市"
    return "全国"

def extract_keywords(title, content=""):
    text = title + content
    kw_map = {
        '国铁': ['高铁', '铁路', '国铁'],
        '城际': ['城际'],
        '地铁': ['地铁'],
        '轨道': ['轨道', '轨交'],
        '综合交通枢纽': ['枢纽'],
        '综合开发': ['TOD', '综合开发', '上盖', '站城'],
        '投融资': ['融资', '投资', '资本', '基金'],
        '可持续经营运营': ['可持续', '经营', '运营']
    }
    keywords = []
    for kw, words in kw_map.items():
        for w in words:
            if w in text:
                keywords.append(kw)
                break
    return keywords if keywords else ["轨道"]

# ============================================================
# 爬虫主函数
# ============================================================
def fetch_news():
    print("🤖 超级小机器人开始干活啦！（已过滤监测月报）")
    all_news = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # ============================================================
    # 国内新闻源
    # ============================================================
    sources = [
        # ---- 行业媒体 ----
        {"name": "中国TOD网", "url": "https://www.chinatod.com.cn/index.php?m=content&c=index&a=lists&catid=36", "scope": "全国", "select": "a[title]", "limit": 15},
        {"name": "中国轨道交通网", "url": "https://www.rail-transit.com/news/", "scope": "全国", "select": "a", "limit": 12},
        {"name": "中国城市轨道交通协会", "url": "https://www.camet.org.cn/news/", "scope": "全国", "select": "a", "limit": 10},
        {"name": "世界轨道交通资讯网", "url": "https://rail.ally.net.cn/news/", "scope": "全国", "select": "a", "limit": 10},
        {"name": "中国交通报", "url": "https://www.zgjtb.com/", "scope": "全国", "select": "a", "limit": 10},
        {"name": "中国经济新闻网", "url": "https://www.cet.com.cn/", "scope": "全国", "select": "a", "limit": 8},
        # ---- 财经/综合媒体 ----
        {"name": "21世纪经济报道", "url": "https://www.21jingji.com/", "scope": "全国", "select": "a", "limit": 8},
        {"name": "每日经济新闻", "url": "https://www.nbd.com.cn/", "scope": "全国", "select": "a", "limit": 8},
        {"name": "中国经营报", "url": "https://dianzibao.cb.com.cn/", "scope": "全国", "select": "a", "limit": 6},
        {"name": "新浪财经", "url": "https://finance.sina.com.cn/", "scope": "全国", "select": "a", "limit": 8},
        {"name": "网易新闻", "url": "https://news.163.com/", "scope": "全国", "select": "a", "limit": 8},
        {"name": "搜狐财经", "url": "https://business.sohu.com/", "scope": "全国", "select": "a", "limit": 8},
        # ---- 地方媒体 ----
        {"name": "南方日报", "url": "https://news.nfnews.com/guangdong/", "scope": "广东省", "select": "a", "limit": 10},
        {"name": "广州日报（大洋网）", "url": "https://news.dayoo.com/guangzhou/", "scope": "广州市", "select": "a", "limit": 10},
        {"name": "深圳新闻网", "url": "https://www.sznews.com/news/", "scope": "广东省", "select": "a", "limit": 8},
        {"name": "华龙网", "url": "https://www.cqnews.net/news/", "scope": "全国", "select": "a", "limit": 8},
        # ---- 政务/官方平台 ----
        {"name": "广州市政府网", "url": "https://www.gz.gov.cn/zwgk/", "scope": "广州市", "select": "a", "limit": 10},
        {"name": "广州市规划局", "url": "https://ghzyj.gz.gov.cn/ywpd/cxgh/ghxkgsgb/", "scope": "广州市", "select": "ul.list li a", "limit": 10},
        {"name": "广州市发改委", "url": "https://fgw.gz.gov.cn/zwgk/", "scope": "广州市", "select": "a", "limit": 8},
        {"name": "广东省交通运输厅", "url": "https://td.gd.gov.cn/", "scope": "广东省", "select": "a", "limit": 8},
        {"name": "广东省发改委", "url": "https://drc.gd.gov.cn/", "scope": "广东省", "select": "a", "limit": 8},
        {"name": "广州市交通运输局", "url": "https://jtj.gz.gov.cn/", "scope": "广州市", "select": "a", "limit": 8},
    ]

    # 关键词过滤
    keyword_filters = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路', '站城', '高铁', '轨道交通', '场站', '上盖']

    for src in sources:
        try:
            print(f"正在访问 {src['name']}...")
            r = requests.get(src['url'], headers=headers, timeout=12)
            soup = BeautifulSoup(r.text, 'html.parser')
            count = 0
            for item in soup.select(src['select'])[:src['limit']]:
                title = item.text.strip()
                link = item.get('href')
                if not title or not link or len(title) < 8:
                    continue

                # ===== 删除监测月报 =====
                if "监测月报" in title or "监测报告" in title:
                    continue

                if not any(k in title for k in keyword_filters):
                    continue

                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = src['url'].split('/')[0] + '//' + src['url'].split('/')[2] + link
                    else:
                        link = src['url'].rstrip('/') + '/' + link.lstrip('/')

                scope = extract_scope(title)
                if scope == "全国" and src['scope'] != "全国":
                    scope = src['scope']
                keywords = extract_keywords(title)
                news_type = classify_news(title)
                summary = generate_summary(title, src['name'])
                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title[:200],
                    "链接": link,
                    "来源": src['name'],
                    "范围": scope,
                    "关键词": keywords,
                    "摘要": summary,
                    "类型": news_type
                })
                count += 1
            print(f"✅ {src['name']} 抓取 {count} 条")
        except Exception as e:
            print(f"❌ {src['name']} 出错: {e}")

    # ============================================================
    # 国际新闻源
    # ============================================================
    international_sources = [
        {"name": "Railway Gazette", "url": "https://www.railwaygazette.com/", "select": "a", "limit": 6},
        {"name": "International Railway Journal", "url": "https://www.railjournal.com/", "select": "a", "limit": 6},
        {"name": "Global Railway Review", "url": "https://www.globalrailwayreview.com/", "select": "a", "limit": 6},
    ]

    for src in international_sources:
        try:
            print(f"正在访问国际源 {src['name']}...")
            r = requests.get(src['url'], headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            count = 0
            for item in soup.select(src['select'])[:src['limit']]:
                title = item.text.strip()
                link = item.get('href')
                if not title or not link or len(title) < 10:
                    continue
                if "监测月报" in title or "监测报告" in title:
                    continue
                if not any(k in title.lower() for k in ['rail', 'transit', 'metro', 'station', 'hub', 'TOD', 'infrastructure']):
                    continue
                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = src['url'].split('/')[0] + '//' + src['url'].split('/')[2] + link
                    else:
                        link = src['url'].rstrip('/') + '/' + link.lstrip('/')
                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title[:150],
                    "链接": link,
                    "来源": src['name'],
                    "范围": "世界",
                    "关键词": extract_keywords(title),
                    "摘要": generate_summary(title, src['name']),
                    "类型": classify_news(title)
                })
                count += 1
            print(f"✅ 国际源 {src['name']} 抓取 {count} 条")
        except Exception as e:
            print(f"❌ 国际源 {src['name']} 出错: {e}")

    # ============================================================
    # 去重
    # ============================================================
    seen = set()
    unique_news = []
    for item in all_news:
        key = item["标题"][:30] + item["链接"][:50]
        if key not in seen:
            seen.add(key)
            unique_news.append(item)

    # ============================================================
    # 排序
    # ============================================================
    unique_news.sort(key=lambda x: x["日期"], reverse=True)

    # ============================================================
    # 保存
    # ============================================================
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=2)

    print(f"🎉 大功告成！共抓取 {len(unique_news)} 条新闻（去重后）")

if __name__ == "__main__":
    fetch_news()
