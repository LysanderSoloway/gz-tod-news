import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# ============================================================
# 爬虫主函数（直接从 news_data.json 读取，不依赖 HISTORICAL_NEWS）
# ============================================================
def fetch_news():
    print("🤖 小机器人开始干活啦！（修复版）")

    # 直接从 news_data.json 加载已有数据
    try:
        with open('news_data.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
            print(f"📚 加载现有数据 {len(all_news)} 条")
    except FileNotFoundError:
        all_news = []
        print("📚 未找到 news_data.json，从零开始")

    existing_titles = {item["标题"][:20] + item.get("链接", "")[:50] for item in all_news}
    new_count = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    # ============================================================
    # 数据源列表
    # ============================================================
    sources = [
    # ---- 原有稳定网站 ----
    {"name": "中国轨道交通网", "url": "https://www.rail-transit.com/news/", "select": "a[title]", "limit": 12},
    {"name": "中国城市轨道交通协会", "url": "https://www.camet.org.cn/news/", "select": "a", "limit": 10},
    {"name": "中国TOD网", "url": "https://www.chinatod.com.cn/index.php?m=content&c=index&a=lists&catid=36", "select": "a[title]", "limit": 12},
    {"name": "人民铁道网", "url": "https://www.peoplerail.com/", "select": "a", "limit": 10},
    {"name": "中国交通新闻网", "url": "https://www.zgjtb.com/", "select": "a", "limit": 10},
    {"name": "世界轨道交通资讯网", "url": "https://rail.ally.net.cn/", "select": "a", "limit": 10},
    {"name": "中国城市轨道交通网", "url": "https://www.chinametro.net/", "select": "a", "limit": 10},
    {"name": "北京日报", "url": "https://xinwen.bjd.com.cn/", "select": "a", "limit": 10},
    {"name": "天津日报", "url": "https://epaper.tianjinwe.com/", "select": "a", "limit": 10},
    {"name": "南方日报", "url": "https://epaper.nfnews.com/", "select": "a", "limit": 10},
    {"name": "广州日报大洋网", "url": "https://news.dayoo.com/guangzhou/", "select": "a", "limit": 10},
    {"name": "深圳新闻网", "url": "https://www.sznews.com/news/", "select": "a", "limit": 10},
    {"name": "厦门网", "url": "https://news.xmnn.cn/", "select": "a", "limit": 10},
    {"name": "杭州网", "url": "https://www.hangzhou.com.cn/", "select": "a", "limit": 10},
    {"name": "四川网络广播电视台", "url": "https://www.sctv.com/", "select": "a", "limit": 10},
    {"name": "沈阳网", "url": "https://www.syd.com.cn/", "select": "a", "limit": 10},
    {"name": "观点网", "url": "https://www.guandian.cn/", "select": "a", "limit": 10},

    # ---- 优化后的政府类网站（使用精准新闻栏目页） ----
    {"name": "北京市人民政府", "url": "https://www.beijing.gov.cn/zhengce/zcjd/", "select": "a", "limit": 10},
    {"name": "上海松江", "url": "https://www.shsj.gov.cn/zwdt/", "select": "a", "limit": 10},
    {"name": "象山县人民政府", "url": "https://www.xiangshan.gov.cn/col/col122900/", "select": "a", "limit": 10},
    {"name": "合肥市人民政府", "url": "https://www.hefei.gov.cn/xwzx/", "select": "a", "limit": 10},
    {"name": "马鞍山市人民政府", "url": "https://www.mas.gov.cn/xwzx/", "select": "a", "limit": 10},
    {"name": "佛山市人民政府", "url": "https://www.foshan.gov.cn/zwgk/", "select": "a", "limit": 10},
    {"name": "广东省交通运输厅", "url": "https://td.gd.gov.cn/zxzx/", "select": "a", "limit": 10},

    # ---- 企业/地铁官网 ----
    {"name": "宁波轨道交通官网", "url": "https://www.nbmetro.com/", "select": "a", "limit": 10},
    {"name": "成都轨道集团", "url": "https://www.chengdurail.com/", "select": "a", "limit": 10},
    {"name": "无锡地铁", "url": "https://www.wxmetro.com/", "select": "a", "limit": 10},
    {"name": "广州地铁官网", "url": "https://www.gzmtr.com/", "select": "a", "limit": 10},
    {"name": "天津轨道交通集团", "url": "http://www.tjgdjt.com/xinwen/", "select": "a", "limit": 10},

    # ---- 地方新闻媒体 ----
    {"name": "青岛新闻网", "url": "https://www.qingdaonews.com/", "select": "a", "limit": 10},
    {"name": "香港政府新闻网", "url": "https://www.news.gov.hk/tc/", "select": "a", "limit": 10},
]

    for src in sources:
        try:
            print(f"正在访问 {src['name']}...")
            r = requests.get(src['url'], headers=headers, timeout=20)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(src['select'])
            if not items:
                print(f"⚠️ {src['name']} 无匹配链接，跳过")
                continue
            count = 0
            for item in items[:src['limit']]:
                title = item.text.strip()
                link = item.get('href')

                if not title or not link or len(title) < 6:
                    continue

                if any(k in title for k in ['监测月报', '监测报告', '广告', '专题']):
                    continue

                if not any(k in title for k in keyword_filters):
                    continue

                if not link.startswith('http'):
                    if link.startswith('/'):
                        base = src['url'].split('/')[0] + '//' + src['url'].split('/')[2]
                        link = base + link
                    else:
                        link = src['url'].rstrip('/') + '/' + link.lstrip('/')

                key = title[:20] + link[:50]
                if key in existing_titles:
                    continue
                existing_titles.add(key)

                # 范围判断
                if "世界" in title or "国际" in title:
                    scope = "世界"
                elif "广东" in title or "深圳" in title or "佛山" in title:
                    scope = "广州市" if "广州" in title else "广东省"
                elif "广州" in title:
                    scope = "广州市"
                else:
                    scope = "全国"

                # 类型判断
                news_type = "综合"
                type_keywords = {
                    "项目建设进展": ["封顶", "开工", "竣工", "通车", "开通", "投运", "动工", "推进", "建设", "进展", "完成", "交付", "贯通", "合龙", "施工"],
                    "规划公示/获批": ["规划", "公示", "获批", "审议", "通过", "方案", "批复", "可研", "立项", "选址"],
                    "政策/行业观点": ["政策", "出台", "发布", "意见", "办法", "条例", "观点", "论坛", "会议", "座谈", "解读", "建议"],
                    "商业配套/招商": ["商业", "招商", "商场", "签约", "入驻", "开业", "品牌", "零售"],
                    "投融资": ["投资", "融资", "资本", "基金", "授信", "债券", "REITs", "PPP", "资金", "亿元"],
                    "可持续经营运营": ["可持续", "经营", "运营", "营收", "盈利", "客流", "票务"]
                }
                for t, kws in type_keywords.items():
                    if any(kw in title for kw in kws):
                        news_type = t
                        break

                # 关键词提取
                keywords = []
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
                for kw, words in kw_map.items():
                    if any(w in title for w in words):
                        keywords.append(kw)
                if not keywords:
                    keywords = ["轨道"]

                summary = title[:80] + ("..." if len(title) > 80 else "")

                all_news.append({
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "标题": title,
                    "链接": link,
                    "来源": src['name'],
                    "范围": scope,
                    "关键词": keywords,
                    "摘要": summary,
                    "类型": news_type
                })
                count += 1
                new_count += 1
            print(f"✅ {src['name']} 新增 {count} 条")
        except Exception as e:
            print(f"❌ {src['name']} 出错: {e}")
        time.sleep(0.8)

    all_news.sort(key=lambda x: x["日期"], reverse=True)

    with open('news_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

    print(f"🎉 共 {len(all_news)} 条新闻，新增 {new_count} 条")

if __name__ == "__main__":
    fetch_news()
