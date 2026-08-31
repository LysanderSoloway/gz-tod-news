import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===== 关键词拆分：主体词 + 领域词 =====
SUBJECTS = ['国铁', '铁路', '城际', '地铁']
AREAS = ['规划', '城市设计', '建筑', '交通', '产业', '投融资', '招商', '运营', '站城融合', 'TOD', '获奖']

MEDIA_MAP = {
    'people.com.cn': '人民网', 'xinhuanet.com': '新华网', 'gmw.cn': '光明网',
    'cnr.cn': '央广网', 'cctv.com': '央视网', 'china.com.cn': '中国网',
    'zgjtb.com': '中国交通报', 'peoplerail.com': '人民铁道报',
    'bjnews.com.cn': '新京报', 'thepaper.cn': '澎湃新闻',
    'yicai.com': '第一财经', 'leju.com': '乐居财经',
    'sohu.com': '搜狐新闻', '163.com': '网易新闻', 'sina.com.cn': '新浪新闻',
    'ifeng.com': '凤凰网', 'huanqiu.com': '环球网',
    'jiemian.com': '界面新闻', 'caixin.com': '财新网',
    '21jingji.com': '21世纪经济报道', 'nbd.com.cn': '每日经济新闻',
    'stcn.com': '证券时报', 'eastmoney.com': '东方财富', 'hexun.com': '和讯网',
    'gz.gov.cn': '广州市政府网', 'gd.gov.cn': '广东省政府网',
    'gzmtr.com': '广州地铁官网', 'szmc.net': '深圳地铁官网',
    'sznews.com': '深圳新闻网', 'dayoo.com': '广州日报大洋网',
    'nfnews.com': '南方日报', 'oeeee.com': '南方都市报',
    'ycwb.com': '羊城晚报', 'gz-cmc.com': '广州日报新花城',
    'conghua.gov.cn': '从化区政府网',
    'bj.gov.cn': '北京市政府网', 'beijing.gov.cn': '北京市政府网',
    'bjd.com.cn': '北京日报', 'ynet.com': '北京青年报',
    'tj.gov.cn': '天津政务网', 'sh.gov.cn': '上海市政府网',
    'shmetro.com': '上海申通地铁', 'shobserver.com': '上观新闻',
    'cq.gov.cn': '重庆市政府网', 'cql.gov.cn': '重庆日报',
    'scol.com.cn': '四川观察', 'sctv.com': '四川广播电视台',
    'jinan.gov.cn': '济南市政府网', 'jnnc.com': '济南日报',
    'sd.gov.cn': '山东省政府网', 'sdjt.gov.cn': '山东省交通厅',
    'xian-metro.com': '西安地铁官网', 'sx.chinanews.com': '中新网山西',
    'henan.gov.cn': '河南省政府网', 'hubeidaily.net': '湖北日报',
    'hunan.gov.cn': '湖南省政府网', 'icswb.com': '长沙晚报',
    'gxnews.com.cn': '广西新闻网', 'xmnn.cn': '厦门网',
    'nbmetro.com': '宁波轨道交通官网', 'hangzhou.com.cn': '杭州网',
    'hangzhou.gov.cn': '杭州市政府网', 'suzhou.gov.cn': '苏州市政府网',
    'nj.gov.cn': '南京市政府网', 'hebei.gov.cn': '河北省政府网',
    'hebnews.cn': '河北新闻网', 'cnjiwang.com': '中国吉林网',
    'jlnews.cn': '吉林日报', 'hljnews.cn': '黑龙江日报',
    'chinatod.com.cn': '中国TOD网', 'rail-transit.com': '中国轨道交通网',
    'chinametro.net': '中国城市轨道交通网', 'camet.org.cn': '中国城市轨道交通协会',
    'rail.ally.net.cn': '世界轨道交通资讯网', 'rt-media.cn': 'RT轨道交通',
    'railworld.com.cn': '轨道世界', 'gaotie.cn': '高铁网',
    'railjournal.com': 'International Railway Journal',
    'railwaygazette.com': 'Railway Gazette', 'uitp.org': 'UITP',
    'tfl.gov.uk': '伦敦交通局', 'lta.gov.sg': '新加坡LTA',
    'db.de': '德国铁路DB', 'jr-east.co.jp': 'JR东日本',
    'fra.dot.gov': '美国联邦铁路管理局', 'europa.eu': '欧盟委员会',
    'baidu.com': '百度新闻', 'sogou.com': '搜狗新闻', 'so.com': '360新闻',
    'toutiao.com': '今日头条', 'news.qq.com': '腾讯新闻',
    'news.163.com': '网易新闻', 'news.sina.com.cn': '新浪新闻',
    'news.sohu.com': '搜狐新闻',
}

def get_media_name(link):
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

def clean_text(text):
    if not text:
        return ''
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_title_and_summary(item, soup):
    try:
        title = ''
        link_elem = item.find('a')
        if link_elem:
            title = link_elem.text.strip()
        else:
            title = item.text.strip()
        title = clean_text(title)
        if '...' in title:
            title = title.split('...')[0].strip()
        suffixes = ['快资讯', '搜狐', '新浪', '网易', '腾讯', '今日头条', '百家号', '一点资讯', 'ZAKER', '大风号', '澎湃号', '媒体号']
        for suf in suffixes:
            if title.endswith(suf):
                title = title[:-len(suf)].strip()
        title = re.sub(r'\s*\d+天前$', '', title)
        title = re.sub(r'\s*\d+小时前$', '', title)
        title = re.sub(r'\s*\d+分钟前$', '', title)
        if len(title) > 60:
            title = title[:60] + '...'
        return title
    except Exception as e:
        logging.debug(f"提取标题失败: {e}")
        return ''

def fetch_article_summary(url, session, timeout=10):
    """
    从新闻详情页提取正文前30字作为摘要
    """
    try:
        resp = session.get(url, timeout=timeout)
        if resp.status_code != 200:
            return ''
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        article_text = ''
        
        # 1. 找 article 标签
        article = soup.find('article')
        if article:
            article_text = article.text.strip()
        
        # 2. 找常见的正文容器 class
        if not article_text or len(article_text) < 20:
            content_selectors = [
                '.content', '.article-content', '.article-text', '.detail-content',
                '.news-content', '.post-content', '.entry-content', '.text-content',
                '.main-content', '.article-body', '.news-body', '.detail-body',
                '.content-body', '.article-detail', '.news-detail'
            ]
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    article_text = elem.text.strip()
                    break
        
        # 3. 找所有 p 标签，取前几个有内容的
        if not article_text or len(article_text) < 20:
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.text.strip()
                if len(text) > 20 and not text.startswith('广告') and not text.startswith('声明') and not text.startswith('原标题'):
                    paragraphs.append(text)
                    if len(''.join(paragraphs)) > 50:
                        break
            if paragraphs:
                article_text = ' '.join(paragraphs)
        
        # 清理正文
        if article_text:
            article_text = clean_text(article_text)
            # 去掉常见的干扰文字
            article_text = re.sub(r'（.*?版权.*?）', '', article_text)
            article_text = re.sub(r'责任编辑.*?$', '', article_text)
            article_text = re.sub(r'来源.*?$', '', article_text)
            article_text = re.sub(r'本报讯\s*', '', article_text)
            article_text = re.sub(r'新华社\s*', '', article_text)
            article_text = re.sub(r'记者.*?报道', '', article_text)
            article_text = re.sub(r'通讯员.*?报道', '', article_text)
            article_text = re.sub(r'【.*?】', '', article_text)
            article_text = article_text.strip()
            
            # 只取前30字，保证在30字以内结束（以句号、问号、感叹号结束）
            if len(article_text) > 30:
                # 尝试在30字附近找到合适的断句位置
                cut_text = article_text[:35]
                # 找句号、问号、感叹号
                for punct in ['。', '！', '？', '；', '，']:
                    pos = cut_text.rfind(punct)
                    if pos > 10 and pos <= 30:
                        article_text = article_text[:pos+1]
                        break
                # 如果没找到合适的标点，直接取30字
                if len(article_text) > 30:
                    article_text = article_text[:30] + '...'
            return article_text
        return ''
    except Exception as e:
        logging.debug(f"提取详情页摘要失败 {url}: {e}")
        return ''

def detect_scope(title):
    if any(w in title for w in ["世界", "国际", "全球"]):
        return "世界"
    elif "广州" in title:
        return "广州市"
    elif any(w in title for w in ["广东", "深圳", "佛山", "东莞", "中山", "珠海"]):
        return "广东省"
    else:
        return "全国"

def detect_type(title):
    type_map = {
        "项目建设进展": ["封顶", "开工", "竣工", "通车", "开通", "投运", "动工", "建设", "进展", "完成", "交付", "贯通", "合龙"],
        "规划公示/获批": ["规划", "公示", "获批", "审议", "通过", "方案", "批复", "可研", "立项", "选址"],
        "政策/行业观点": ["政策", "出台", "发布", "意见", "办法", "条例", "观点", "论坛", "会议", "座谈", "解读"],
        "商业配套/招商": ["商业", "招商", "商场", "签约", "入驻", "开业", "品牌"],
        "投融资": ["投资", "融资", "资本", "基金", "授信", "债券", "REITs", "PPP", "资金", "亿元"],
        "可持续经营运营": ["可持续", "经营", "运营", "营收", "盈利", "客流", "票务"]
    }
    for t, kws in type_map.items():
        if any(kw in title for kw in kws):
            return t
    return "综合"

def extract_keywords(title):
    subjects = ['国铁', '铁路', '城际', '地铁']
    areas = ['规划', '城市设计', '建筑', '交通', '产业', '投融资', '招商', '运营', '站城融合', 'TOD', '获奖']
    keywords = []
    for s in subjects:
        if s in title:
            keywords.append(s)
    for a in areas:
        if a in title:
            keywords.append(a)
    return keywords if keywords else ["轨道"]

def fetch_with_retry(url, headers, timeout=20, retries=2):
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            return resp
        except Exception as e:
            if attempt < retries:
                logging.debug(f"重试 {url} (第{attempt+1}次)")
                time.sleep(1)
            else:
                raise e
    return None

def fetch_news():
    logging.info("🤖 爬虫启动（30字内摘要版）")
    
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
        logging.info(f"📚 已有 {len(all_news)} 条数据")
    except FileNotFoundError:
        all_news = []
        logging.info("📚 从零开始")
    except json.JSONDecodeError:
        all_news = []
        logging.warning("⚠️ 数据文件损坏，从零开始")
    
    existing_keys = {item["标题"][:20] + item.get("链接", "")[:50] for item in all_news}
    
    try:
        with open('sources.json', 'r', encoding='utf-8') as f:
            sources = json.load(f)
        logging.info(f"📡 加载 {len(sources)} 个数据源")
    except FileNotFoundError:
        logging.error("❌ 找不到 sources.json")
        return
    except json.JSONDecodeError:
        logging.error("❌ sources.json 格式错误")
        return
    
    new_count = 0
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    
    for src in sources:
        name = src.get('name', '未知')
        base_url = src.get('url', '')
        selector = src.get('select', 'a')
        limit = src.get('limit_per_page', 10)
        pages = src.get('pages', 1)
        encoding = src.get('encoding', 'utf-8')
        
        if not base_url:
            logging.warning(f"⚠️ {name} 缺少URL，跳过")
            continue
        
        logging.info(f"🔍 抓取: {name}")
        
        for page in range(1, pages + 1):
            if page == 1:
                page_url = base_url
            else:
                if '?' in base_url:
                    page_url = base_url + f'&page={page}'
                else:
                    page_url = base_url + f'?page={page}'
            
            try:
                resp = fetch_with_retry(page_url, session.headers, timeout=20)
                if resp is None or resp.status_code != 200:
                    logging.warning(f"⚠️ {name} 第 {page} 页访问失败")
                    continue
                
                resp.encoding = encoding
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select(selector)
                if not items:
                    logging.warning(f"⚠️ {name} 第 {page} 页无匹配链接")
                    continue
                
                count = 0
                for item in items[:limit]:
                    try:
                        link_elem = item.find('a')
                        if link_elem:
                            link = link_elem.get('href')
                        else:
                            link = item.get('href')
                        
                        if not link:
                            continue
                        
                        full_link = urljoin(page_url, link)
                        title = extract_title_and_summary(item, soup)
                        
                        if not title:
                            continue
                        
                        # ===== 组合过滤逻辑 =====
                        has_subject = any(s in title for s in SUBJECTS)
                        has_area = any(a in title for a in AREAS)
                        if not (has_subject and has_area):
                            continue
                        
                        key = title[:20] + full_link[:50]
                        if key in existing_keys:
                            continue
                        existing_keys.add(key)
                        
                        # ===== 进入详情页抓取摘要（30字以内） =====
                        summary = fetch_article_summary(full_link, session, timeout=10)
                        if not summary:
                            summary = ''
                        
                        media = get_media_name(full_link) or name
                        publish_date = datetime.now().strftime("%Y-%m-%d")
                        scope = detect_scope(title)
                        news_type = detect_type(title)
                        keywords = extract_keywords(title)
                        
                        all_news.append({
                            "日期": publish_date,
                            "标题": title,
                            "链接": full_link,
                            "来源": media,
                            "范围": scope,
                            "关键词": keywords,
                            "摘要": summary,
                            "类型": news_type
                        })
                        count += 1
                        new_count += 1
                        
                        time.sleep(random.uniform(0.5, 1.2))
                    except Exception as e:
                        logging.debug(f"处理条目失败: {e}")
                        continue
                
                logging.info(f"✅ {name} 第 {page} 页新增 {count} 条")
                
            except Exception as e:
                logging.error(f"❌ {name} 第 {page} 页出错: {e}")
            
            time.sleep(random.uniform(0.8, 1.8))
        
        time.sleep(random.uniform(1.5, 3.0))
    
    all_news.sort(key=lambda x: x["日期"], reverse=True)
    
    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    logging.info(f"🎉 完成！新增 {new_count} 条，共 {len(all_news)} 条")

if __name__ == "__main__":
    fetch_news()
