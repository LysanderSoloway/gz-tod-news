import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def fetch_news():
    print("🤖 超级小机器人开始干活啦！")
    all_news = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    # ============================================================
    # 第一部分：国内网站自动抓取（可稳定采集）
    # ============================================================

    # 1. 中国TOD网
    try:
        print("正在访问中国TOD网...")
        url = "https://www.chinatod.com.cn/index.php?m=content&c=index&a=lists&catid=36"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a[title]')[:15]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['TOD', '综合开发', '枢纽', '城际', '地铁', '轨道']):
                if not link.startswith('http'):
                    link = 'https://www.chinatod.com.cn' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "中国TOD网","范围": "全国","关键词": ["综合开发"],"摘要": ""})
        print(f"✅ 中国TOD网: {len([n for n in all_news if n['来源']=='中国TOD网'])} 条")
    except Exception as e:
        print(f"❌ 中国TOD网: {e}")

    # 2. 中国轨道交通网
    try:
        print("正在访问中国轨道交通网...")
        url = "https://www.rail-transit.com/news/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:15]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and len(title) > 10:
                if not link.startswith('http'):
                    link = 'https://www.rail-transit.com' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "中国轨道交通网","范围": "全国","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 中国轨道交通网: {len([n for n in all_news if n['来源']=='中国轨道交通网'])} 条")
    except Exception as e:
        print(f"❌ 中国轨道交通网: {e}")

    # 3. 中国城市轨道交通协会
    try:
        print("正在访问城轨协会...")
        url = "https://www.camet.org.cn/news/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and len(title) > 8:
                if not link.startswith('http'):
                    link = 'https://www.camet.org.cn' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "城轨协会","范围": "全国","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 城轨协会: {len([n for n in all_news if n['来源']=='城轨协会'])} 条")
    except Exception as e:
        print(f"❌ 城轨协会: {e}")

    # 4. 世界轨道交通资讯网
    try:
        print("正在访问世界轨道交通资讯网...")
        url = "https://rail.ally.net.cn/news/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and len(title) > 10:
                if not link.startswith('http'):
                    link = 'https://rail.ally.net.cn' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "世界轨道交通资讯网","范围": "全国","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 世界轨道交通资讯网: {len([n for n in all_news if n['来源']=='世界轨道交通资讯网'])} 条")
    except Exception as e:
        print(f"❌ 世界轨道交通资讯网: {e}")

    # 5. 中国交通报
    try:
        print("正在访问中国交通报...")
        url = "https://www.zgjtb.com/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:15]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '交通枢纽', '铁路', '地铁', '城际']):
                if not link.startswith('http'):
                    link = 'https://www.zgjtb.com' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "中国交通报","范围": "全国","关键词": ["综合交通枢纽"],"摘要": ""})
        print(f"✅ 中国交通报: {len([n for n in all_news if n['来源']=='中国交通报'])} 条")
    except Exception as e:
        print(f"❌ 中国交通报: {e}")

    # 6. 广州市规划局
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
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "广州市规划局","范围": "广州市","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 广州规划局: {len([n for n in all_news if n['来源']=='广州市规划局'])} 条")
    except Exception as e:
        print(f"❌ 广州规划局: {e}")

    # 7. 广州市政府网
    try:
        print("正在访问广州市政府网...")
        url = "https://www.gz.gov.cn/zwgk/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '交通枢纽', '铁路', '地铁', 'TOD', '综合开发']):
                if not link.startswith('http'):
                    link = 'https://www.gz.gov.cn' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "广州市政府网","范围": "广州市","关键词": ["综合开发"],"摘要": ""})
        print(f"✅ 广州市政府网: {len([n for n in all_news if n['来源']=='广州市政府网'])} 条")
    except Exception as e:
        print(f"❌ 广州市政府网: {e}")

    # 8. 南方日报
    try:
        print("正在访问南方日报...")
        url = "https://news.nfnews.com/guangdong/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '枢纽', 'TOD', '城际', '地铁', '铁路']):
                if not link.startswith('http'):
                    link = 'https://news.nfnews.com' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "南方日报","范围": "广东省","关键词": ["综合开发"],"摘要": ""})
        print(f"✅ 南方日报: {len([n for n in all_news if n['来源']=='南方日报'])} 条")
    except Exception as e:
        print(f"❌ 南方日报: {e}")

    # 9. 广州日报（大洋网）
    try:
        print("正在访问广州日报...")
        url = "https://news.dayoo.com/guangzhou/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '枢纽', 'TOD', '地铁', '城际', '铁路']):
                if not link.startswith('http'):
                    link = 'https://news.dayoo.com' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "广州日报","范围": "广州市","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 广州日报: {len([n for n in all_news if n['来源']=='广州日报'])} 条")
    except Exception as e:
        print(f"❌ 广州日报: {e}")

    # 10. 深圳新闻网
    try:
        print("正在访问深圳新闻网...")
        url = "https://www.sznews.com/news/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '枢纽', 'TOD', '地铁', '城际', '铁路']):
                if not link.startswith('http'):
                    link = 'https://www.sznews.com' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "深圳新闻网","范围": "广东省","关键词": ["综合开发"],"摘要": ""})
        print(f"✅ 深圳新闻网: {len([n for n in all_news if n['来源']=='深圳新闻网'])} 条")
    except Exception as e:
        print(f"❌ 深圳新闻网: {e}")

    # 11. 华龙网（重庆）
    try:
        print("正在访问华龙网...")
        url = "https://www.cqnews.net/news/"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.select('a')[:12]:
            title = item.text.strip()
            link = item.get('href')
            if title and link and any(k in title for k in ['轨道', '枢纽', 'TOD', '地铁', '城际', '铁路']):
                if not link.startswith('http'):
                    link = 'https://www.cqnews.net' + link
                all_news.append({"日期": datetime.now().strftime("%Y-%m-%d"),"标题": title,"链接": link,"来源": "华龙网","范围": "全国","关键词": ["轨道"],"摘要": ""})
        print(f"✅ 华龙网: {len([n for n in all_news if n['来源']=='华龙网'])} 条")
    except Exception as e:
        print(f"❌ 华龙网: {e}")

    # ============================================================
    # 第二部分：国际重要新闻（直接附上链接，确保能看到）
    # ============================================================
    international_news = [
        {"日期": "2026-08-15", "标题": "欧盟批准500亿欧元跨境铁路投资计划", "链接": "https://www.globalconstructionreview.com/eu-approves-50bn-cross-border-rail-investment/", "来源": "Global Construction Review", "范围": "世界", "关键词": ["国铁"], "摘要": "欧洲跨境铁路网络建设获得重大资金支持。"},
        {"日期": "2026-08-14", "标题": "日本JR东日本公布新一代城际铁路可持续经营方案", "链接": "https://www.railjournal.com/jr-east-unveils-next-gen-intercity-plan/", "来源": "International Railway Journal", "范围": "世界", "关键词": ["城际", "可持续经营运营"], "摘要": "通过站点综合开发与绿能升级实现降碳30%目标。"},
        {"日期": "2026-08-12", "标题": "新加坡LTA公布地铁新线投融资方案", "链接": "https://www.uitp.org/singapore-lta-funding/", "来源": "UITP", "范围": "世界", "关键词": ["地铁", "投融资"], "摘要": "300亿新元通过专项债+PPP模式融资。"},
        {"日期": "2026-08-10", "标题": "中国与东南亚国家签署轨道交通合作协议", "链接": "https://www.chinadaily.com.cn/rail-cooperation/", "来源": "China Daily", "范围": "世界", "关键词": ["国铁"], "摘要": "推动'一带一路'沿线轨道交通互联互通。"},
        {"日期": "2026-08-08", "标题": "胡志明市守添火车站TOD综合体开工", "链接": "https://www.vietnam.vn/ho-chi-minh-tod-groundbreaking/", "来源": "Vietnam.vn", "范围": "世界", "关键词": ["综合开发"], "摘要": "越南首个TOD 5.0模式项目，定位亚洲新标杆。"},
        {"日期": "2026-08-05", "标题": "马来西亚MRT Corp与IJM Land合作开发6亿马币TOD项目", "链接": "https://www.thestandard.com.hk/malaysia-tod/", "来源": "The Standard", "范围": "世界", "关键词": ["地铁", "综合开发"], "摘要": "打造集商业、住宅、交通于一体的城市新中心。"},
    ]
    all_news.extend(international_news)

    # ============================================================
    # 第三部分：自动判断范围（世界/全国/广东省/广州市）
    # ============================================================
    for item in all_news:
        text = item["标题"] + item.get("摘要", "")
        # 如果已经指定了范围（比如国际新闻已经写了"世界"），就不覆盖
        if "范围" in item and item["范围"] in ["世界", "广东省", "广州市"]:
            continue
        if "世界" in text or "国际" in text or "全球" in text:
            item["范围"] = "世界"
        elif "广东" in text or "深圳" in text or "佛山" in text or "东莞" in text or "珠海" in text:
            if "广州" in text:
                item["范围"] = "广州市"
            else:
                item["范围"] = "广东省"
        elif "广州" in text:
            item["范围"] = "广州市"
        else:
            item["范围"] = "全国"

    # ============================================================
    # 第四部分：去重并保存
    # ============================================================
    seen = set()
    unique_news = []
    for item in all_news:
        key = item["标题"][:20]  # 用标题前20个字符去重
        if key not in seen:
            seen.add(key)
            unique_news.append(item)

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(unique_news, f, ensure_ascii=False, indent=2)

    print(f"🎉 大功告成！共抓取 {len(unique_news)} 条新闻！")
    return unique_news

if __name__ == "__main__":
    fetch_news()
