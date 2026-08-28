import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 关键词过滤（保持不变）
KEYWORD_FILTERS = ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道', '铁路', '站城', '高铁', '轨道交通', '上盖']

# 只保留最近多少天内的新闻（例如90天，约3个月）
KEEP_DAYS = 90

def parse_publish_date(html, url):
    """
    从新闻详情页的HTML中解析发布日期。
    这里用几种常见方式查找，如果找不到就返回None。
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 方法1：找 <time> 标签
    time_tag = soup.find('time')
    if time_tag and time_tag.get('datetime'):
        return time_tag.get('datetime')
    
    # 方法2：找 meta 标签
    meta_date = soup.find('meta', {'name': 'pubdate'}) or soup.find('meta', {'property': 'article:published_time'})
    if meta_date and meta_date.get('content'):
        return meta_date['content']
    
    # 方法3：在文本中搜索常见的日期格式（如 2026-08-28, 2026/08/28, 2026年8月28日）
    text = soup.get_text()
    # 匹配 yyyy-mm-dd 或 yyyy/mm/dd 或 yyyy年mm月dd日
    patterns = [
        r'(\d{4}-\d{1,2}-\d{1,2})',
        r'(\d{4}/\d{1,2}/\d{1,2})',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if pattern.endswith('日'):
                y, m, d = match.groups()
                return f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                return match.group(1)
    
    return None

def parse_date_string(date_str):
    """
    将各种日期字符串转换为 datetime 对象
    """
    if not date_str:
        return None
    # 尝试多种格式
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def fetch_news():
    logging.info("🤖 小机器人开始干活啦！（日期过滤版）")
    
    # 1. 读取旧数据（注意：旧数据可能日期不准，我们保留，但新抓的会严格过滤）
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        logging.info(f"📚 加载现有数据 {len(all_news)} 条")
    except FileNotFoundError:
        all_news = []
        logging.info("📚 从零开始")

    # 2. 建立去重索引（标题+链接前50字符）
    existing_keys = {item["标题"][:20] + item.get("链接", "")[:50] for item in all_news}
    
    # 3. 读取数据源配置
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
    except FileNotFoundError:
        logging.error("❌ 找不到 sources.json 文件，请先创建！")
        return

    new_count = 0
    skipped_old = 0
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })

    today = datetime.now().date()
    cutoff_date = today - timedelta(days=KEEP_DAYS)

    for src in sources:
        name = src['name']
        url = src['url']
        selector = src.get('select', 'a')
        limit = src.get('limit_per_page', 10)
        pages = src.get('pages', 1)
        
        logging.info(f"🔍 正在抓取: {name}")
        
        for page in range(1, pages + 1):
            page_url = url if page == 1 else (url + f'?page={page}' if '?' not in url else url + f'&page={page}')
            
            try:
                resp = session.get(page_url, timeout=15)
                resp.encoding = 'utf-8'
                if resp.status_code != 200:
                    logging.warning(f"⚠️ {name} 页面状态码 {resp.status_code}")
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
                    
                    # --- 关键：获取发布日期 ---
                    publish_date = None
                    try:
                        # 请求详情页（增加超时）
                        detail_resp = session.get(full_link, timeout=10)
                        detail_resp.encoding = 'utf-8'
                        if detail_resp.status_code == 200:
                            date_str = parse_publish_date(detail_resp.text, full_link)
                            publish_date = parse_date_string(date_str)
                            # 如果解析到的日期是未来时间（可能是错误），则忽略
                            if publish_date and publish_date.date() > today:
                                publish_date = None
                        else:
                            logging.debug(f"详情页访问失败: {full_link}")
                    except Exception as e:
                        logging.debug(f"获取详情页出错 {full_link}: {e}")
                    
                    # 如果获取到发布日期，检查是否在最近KEEP_DAYS天内
                    if publish_date:
                        if publish_date.date() < cutoff_date:
                            skipped_old += 1
                            logging.debug(f"跳过旧新闻: {title} ({publish_date.date()})")
                            continue
                    else:
                        # 如果没有获取到发布日期，保守起见，仍然保留（但记录为“未知日期”）
                        # 但为了数据准确性，我们可以选择跳过或保留，这里选择保留但记录日期为采集日期
                        logging.debug(f"未解析到发布日期: {title}，将使用采集日期")
                        publish_date = datetime.now()
                    
                    # 通过所有检查，添加新闻
                    existing_keys.add(key)
                    news_item = {
                        "日期": publish_date.strftime("%Y-%m-%d") if publish_date else datetime.now().strftime("%Y-%m-%d"),
                        "标题": title,
                        "链接": full_link,
                        "来源": name,
                        "范围": classify_scope(title),
                        "关键词": extract_keywords(title),
                        "摘要": title[:80],
                        "类型": classify_type(title)
                    }
                    all_news.append(news_item)
                    count += 1
                    new_count += 1
                    
                    # 适当延时，避免请求过快
                    time.sleep(random.uniform(0.3, 0.8))
                
                logging.info(f"✅ {name} 第 {page} 页新增 {count} 条")
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                logging.error(f"❌ {name} 第 {page} 页出错: {e}")

    # 按日期排序
    all_news.sort(key=lambda x: x["日期"], reverse=True)
    
    # 保存
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    logging.info(f"🎉 完成！本次新增 {new_count} 条，因日期太旧跳过 {skipped_old} 条，总新闻数 {len(all_news)} 条")

# --- 辅助函数（与之前相同）---
def classify_scope(title):
    if any(w in title for w in ["世界", "国际", "全球"]): return "世界"
    if any(w in title for w in ["广东", "深圳", "佛山", "东莞", "中山", "珠海"]): return "广东省"
    if "广州" in title: return "广州市"
    return "全国"

def classify_type(title):
    type_map = {
        "项目建设进展": ["封顶", "开工", "竣工", "通车", "开通", "投运", "动工", "建设", "进展", "完成", "交付", "贯通"],
        "规划公示/获批": ["规划", "公示", "获批", "审议", "通过", "方案", "批复", "可研", "立项"],
        "政策/行业观点": ["政策", "出台", "发布", "意见", "办法", "条例", "观点", "论坛", "会议"],
        "商业配套/招商": ["商业", "招商", "商场", "签约", "入驻", "开业"],
        "投融资": ["投资", "融资", "资本", "基金", "授信", "债券", "REITs", "PPP"],
        "可持续经营运营": ["可持续", "经营", "运营", "营收", "盈利", "客流"]
    }
    for t, kws in type_map.items():
        if any(kw in title for kw in kws): return t
    return "综合"

def extract_keywords(title):
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
    keywords = []
    for kw, words in kw_map.items():
        if any(w in title for w in words):
            keywords.append(kw)
    return keywords if keywords else ["轨道"]

if __name__ == "__main__":
    fetch_news()
