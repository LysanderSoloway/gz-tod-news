import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KEYWORD_FILTERS = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路', '站城', '高铁', '轨道交通', '上盖']

# ============================================================
# 媒体域名到显示名称映射表（爬虫直接用）
# ============================================================
MEDIA_MAP = {
    'people.com.cn': '人民网',
    'xinhuanet.com': '新华网',
    'gmw.cn': '光明网',
    'cnr.cn': '央广网',
    'cctv.com': '央视网',
    'china.com.cn': '中国网',
    'zgjtb.com': '中国交通报',
    'peoplerail.com': '人民铁道报',
    'bjnews.com.cn': '新京报',
    'thepaper.cn': '澎湃新闻',
    'yicai.com': '第一财经',
    'leju.com': '乐居财经',
    'sohu.com': '搜狐新闻',
    '163.com': '网易新闻',
    'sina.com.cn': '新浪新闻',
    'ifeng.com': '凤凰网',
    'huanqiu.com': '环球网',
    'jiemian.com': '界面新闻',
    'caixin.com': '财新网',
    '21jingji.com': '21世纪经济报道',
    'nbd.com.cn': '每日经济新闻',
    'stcn.com': '证券时报',
    'eastmoney.com': '东方财富',
    'hexun.com': '和讯网',
    'gz.gov.cn': '广州市政府网',
    'gd.gov.cn': '广东省政府网',
    'gzmtr.com': '广州地铁官网',
    'szmc.net': '深圳地铁官网',
    'sznews.com': '深圳新闻网',
    'dayoo.com': '广州日报大洋网',
    'nfnews.com': '南方日报',
    'oeeee.com': '南方都市报',
    'ycwb.com': '羊城晚报',
    'gz-cmc.com': '广州日报新花城',
    'conghua.gov.cn': '从化区政府网',
    'bj.gov.cn': '北京市政府网',
    'beijing.gov.cn': '北京市政府网',
    'bjd.com.cn': '北京日报',
    'ynet.com': '北京青年报',
    'tj.gov.cn': '天津政务网',
    'sh.gov.cn': '上海市政府网',
    'shmetro.com': '上海申通地铁',
    'shobserver.com': '上观新闻',
    'cq.gov.cn': '重庆市政府网',
    'cql.gov.cn': '重庆日报',
    'scol.com.cn': '四川观察',
    'sctv.com': '四川广播电视台',
    'jinan.gov.cn': '济南市政府网',
    'jnnc.com': '济南日报',
    'sd.gov.cn': '山东省政府网',
    'sdjt.gov.cn': '山东省交通厅',
    'xian-metro.com': '西安地铁官网',
    'sx.chinanews.com': '中新网山西',
    'henan.gov.cn': '河南省政府网',
    'hubeidaily.net': '湖北日报',
    'hunan.gov.cn': '湖南省政府网',
    'icswb.com': '长沙晚报',
    'gxnews.com.cn': '广西新闻网',
    'xmnn.cn': '厦门网',
    'nbmetro.com': '宁波轨道交通官网',
    'hangzhou.com.cn': '杭州网',
    'hangzhou.gov.cn': '杭州市政府网',
    'suzhou.gov.cn': '苏州市政府网',
    'nj.gov.cn': '南京市政府网',
    'hebei.gov.cn': '河北省政府网',
    'hebnews.cn': '河北新闻网',
    'cnjiwang.com': '中国吉林网',
    'jlnews.cn': '吉林日报',
    'hljnews.cn': '黑龙江日报',
    'chinatod.com.cn': '中国TOD网',
    'rail-transit.com': '中国轨道交通网',
    'chinametro.net': '中国城市轨道交通网',
    'camet.org.cn': '中国城市轨道交通协会',
    'rail.ally.net.cn': '世界轨道交通资讯网',
    'rt-media.cn': 'RT轨道交通',
    'railworld.com.cn': '轨道世界',
    'gaotie.cn': '高铁网',
    'railjournal.com': 'International Railway Journal',
    'railwaygazette.com': 'Railway Gazette',
    'uitp.org': 'UITP',
    'tfl.gov.uk': '伦敦交通局',
    'lta.gov.sg': '新加坡LTA',
    'db.de': '德国铁路DB',
    'jr-east.co.jp': 'JR东日本',
    'fra.dot.gov': '美国联邦铁路管理局',
    'europa.eu': '欧盟委员会',
    'baidu.com': '百度新闻',
    'sogou.com': '搜狗新闻',
    'so.com': '360新闻',
    'toutiao.com': '今日头条',
    'news.qq.com': '腾讯新闻',
    'news.163.com': '网易新闻',
    'news.sina.com.cn': '新浪新闻',
    'news.sohu.com': '搜狐新闻',
}

def get_media_name_from_link(link):
    """从链接提取域名并查表获取媒体名称"""
    if not link:
        return None
    try:
        parsed = urlparse(link)
        hostname = parsed.hostname or ''
        hostname = hostname.replace('www.', '')
        if hostname in MEDIA_MAP:
            return MEDIA_MAP[hostname]
        for domain, name in MEDIA_MAP.items():
            if hostname.endswith('.' + domain):
                return name
        parts = hostname.split('.')
        if len(parts) >= 2 and parts[-2] not in ['com', 'org', 'net', 'gov', 'edu', 'cn']:
            return parts[-2].capitalize()
        return hostname
    except:
        return None

def clean_title(raw_title):
    """清理标题尾巴"""
    if not raw_title:
        return '无标题'
    title = raw_title
    title = title.replace('快资讯', '').replace('1天前', '').replace('2天前', '').replace('3天前', '').replace('4天前', '').replace('5天前', '').replace('6天前', '').replace('7天前', '')
    title = title.replace('搜狐', '').replace('新浪', '').replace('网易', '').replace('腾讯', '').replace('今日头条', '').replace('百家号', '').replace('一点资讯', '').replace('ZAKER', '').replace('大风号', '').replace('澎湃号', '').replace('媒体号', '')
    title = title.strip()
    if title.endswith('-'):
        title = title[:-1].strip()
    if len(title) > 35:
        title = title[:35] + '...'
    return title or '无标题'

def fetch_news():
    logging.info("🤖 小机器人开始干活啦！（媒体名优化版）")
    
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

                    full_link = urljoin(page_url, link)
                    title = clean_title(raw_title)

                    key = title[:20] + full_link[:50]
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)

                    # ===== 从链接解析真实媒体名称 =====
                    media_name = get_media_name_from_link(full_link)
                    if not media_name:
                        media_name = name  # 兜底：用原来的来源名

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
                        "来源": media_name,  # 这里存的是真实媒体名！
                        "范围": scope,
                        "关键词": keywords,
                        "摘要": title[:80],
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
