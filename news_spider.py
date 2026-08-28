import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 关键词过滤
KEYWORD_FILTERS = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路', '站城', '高铁', '轨道交通', '上盖']

# 域名转网站名称（常见的媒体名称）
DOMAIN_TO_SITE = {
    '163.com': '网易',
    'news.163.com': '网易新闻',
    'sina.com.cn': '新浪',
    'news.sina.com.cn': '新浪新闻',
    'sohu.com': '搜狐',
    'news.sohu.com': '搜狐新闻',
    'qq.com': '腾讯',
    'news.qq.com': '腾讯新闻',
    'ifeng.com': '凤凰网',
    'news.ifeng.com': '凤凰网',
    'people.com.cn': '人民网',
    'xinhuanet.com': '新华网',
    'chinanews.com': '中新网',
    'cnr.cn': '央广网',
    'cctv.com': '央视网',
    'gmw.cn': '光明网',
    'thepaper.cn': '澎湃新闻',
    'guancha.cn': '观察者网',
    'caixin.com': '财新网',
    '21jingji.com': '21世纪经济报道',
    'yicai.com': '第一财经',
    'cls.cn': '财联社',
    'jrj.com.cn': '金融界',
    'stcn.com': '证券时报',
    'zqrb.cn': '证券日报',
    'ccb.com': '建设银行',
    'gzmtr.com': '广州地铁',
    'szmc.net': '深圳地铁',
    'shmetro.com': '上海地铁',
    'bjsubway.com': '北京地铁',
    'gz.gov.cn': '广州市政府',
    'gd.gov.cn': '广东省政府',
    'gov.cn': '中国政府网',
    'beijing.gov.cn': '北京市政府',
    'sh.gov.cn': '上海市政府',
    'sz.gov.cn': '深圳市政府',
    'chinatod.com.cn': '中国TOD网',
    'rail-transit.com': '中国轨道交通网',
    'peoplerail.com': '人民铁道网',
    'zgjtb.com': '中国交通新闻网',
    'railworld.com.cn': '轨道世界',
    'gaotie.cn': '高铁网',
    'chinametro.net': '中国城市轨道交通网',
    'rt-media.cn': 'RT轨道交通',
    'xmnn.cn': '厦门网',
    'sznews.com': '深圳新闻网',
    'dayoo.com': '广州日报大洋网',
    'sctv.com': '四川网络广播电视台',
    'syd.com.cn': '沈阳网',
    'guandian.cn': '观点网',
    'bii.com.cn': '北京京投公司',
}

def extract_domain(url):
    """从链接中提取域名"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # 去掉 www. 前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def get_source_name(url):
    """根据链接获取来源网站名称"""
    domain = extract_domain(url)
    if not domain:
        return '未知来源'
    # 先精确匹配
    if domain in DOMAIN_TO_SITE:
        return DOMAIN_TO_SITE[domain]
    # 再尝试模糊匹配（比如 xxx.163.com 匹配 163.com）
    for key, name in DOMAIN_TO_SITE.items():
        if domain.endswith(key) or key in domain:
            return name
    # 如果都不匹配，返回域名本身
    return domain

def fetch_news():
    logging.info("🤖 小机器人开始干活啦！（来源优化版）")
    
    # 1. 读取已有新闻
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        logging.info(f"📚 加载现有数据 {len(all_news)} 条")
    except FileNotFoundError:
        all_news = []
        logging.info("📚 从零开始")

    # 2. 去重索引
    existing_keys = {item["标题"][:20] + item.get("链接", "")[:50] for item in all_news}

    # 3. 读取数据源配置
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
    except FileNotFoundError:
        logging.error("❌ 找不到 sources.json，请先创建！")
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
            if page == 1:
                page_url = base_url
            else:
                if '?' in base_url:
                    page_url = base_url + f'&page={page}'
                else:
                    page_url = base_url + f'?page={page}'

            try:
                resp = session.get(page_url, timeout=20)
                resp.encoding = encoding
                if resp.status_code != 200:
                    logging.warning(f"⚠️ {name} 状态码 {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select(selector)

                if not items:
                    logging.warning(f"⚠️ {name} 第 {page} 页无匹配链接")
                    continue

                count = 0
                for item in items[:limit]:
                    title = item.text.strip()
                    link = item.get('href')
                    if not title or not link or len(title) < 6:
                        continue

                    if not any(k in title for k in KEYWORD_FILTERS):
                        continue

                    full_link = urljoin(page_url, link)

                    key = title[:20] + full_link[:50]
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)

                    # --- 关键改动：从链接提取来源网站 ---
                    source_name = get_source_name(full_link)

                    publish_date = datetime.now().strftime("%Y-%m-%d")

                    # 范围判断
                    scope = "全国"
                    if any(w in title for w in ["世界", "国际", "全球"]):
                        scope = "世界"
                    elif "广州" in title:
                        scope = "广州市"
                    elif any(w in title for w in ["广东", "深圳", "佛山", "东莞", "中山", "珠海"]):
                        scope = "广东省"

                    # 类型判断
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
                        if any(kw in title for kw in kws):
                            news_type = t
                            break

                    # 关键词标签
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
                        if any(w in title for w in words):
                            keywords.append(kw)
                    if not keywords:
                        keywords = ["轨道"]

                    summary = title[:80] + ("..." if len(title) > 80 else "")

                    news_item = {
                        "日期": publish_date,
                        "标题": title,
                        "链接": full_link,
                        "来源": source_name,      # <-- 这里是真正的来源网站
                        "范围": scope,
                        "关键词": keywords,
                        "摘要": summary,
                        "类型": news_type
                    }
                    all_news.append(news_item)
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

    logging.info(f"🎉 完成！本次新增 {new_count} 条，总新闻数 {len(all_news)} 条")

if __name__ == "__main__":
    fetch_news()
