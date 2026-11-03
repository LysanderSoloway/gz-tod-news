import json
import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
}


def check_one(url):
    """返回 (url, valid, reason)"""
    if not url or not url.startswith('http'):
        return url, False, 'invalid_url'

    try:
        # 先用 HEAD，快
        r = requests.head(url, headers=HEADERS, timeout=8, verify=False, allow_redirects=True)

        # 很多站不支持 HEAD，返回 405/403 时改用 GET
        if r.status_code in (403, 405, 501):
            r = requests.get(url, headers=HEADERS, timeout=10, verify=False,
                             allow_redirects=True, stream=True)
            r.close()

        # 404 / 410 明确失效
        if r.status_code in (404, 410):
            return url, False, f'http_{r.status_code}'

        # 5xx 视为暂时失效，标记但不算死链
        if 500 <= r.status_code < 600:
            return url, False, f'http_{r.status_code}'

        # 重定向到首页 → 疑似失效
        orig_path = urlparse(url).path.rstrip('/')
        final_path = urlparse(r.url).path.rstrip('/')
        if orig_path and len(orig_path) > 3 and final_path in ('', '/'):
            return url, False, 'redirect_to_home'

        if r.status_code == 200:
            return url, True, 'ok'

        return url, False, f'http_{r.status_code}'

    except requests.exceptions.Timeout:
        return url, False, 'timeout'
    except requests.exceptions.SSLError:
        return url, False, 'ssl_error'
    except requests.exceptions.ConnectionError:
        return url, False, 'conn_error'
    except Exception as e:
        return url, False, f'error:{type(e).__name__}'


def main():
    with open('news_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 收集所有唯一链接
    urls = list({item.get('链接', '') for item in data if item.get('链接')})
    logging.info(f"共 {len(data)} 条记录，{len(urls)} 个唯一链接，开始校验…")

    results = {}
    done = 0

    # 10 线程并发，几百条大约 1～2 分钟
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(check_one, u): u for u in urls}
        for fut in as_completed(futures):
            url, valid, reason = fut.result()
            results[url] = {
                'valid': valid,
                'reason': reason,
                'checked_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            done += 1
            if done % 50 == 0:
                logging.info(f"  进度 {done}/{len(urls)}")

    with open('link_status.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    bad = [u for u, v in results.items() if not v['valid']]
    logging.info(f"✅ 校验完成：有效 {len(urls) - len(bad)} 个，失效 {len(bad)} 个")
    if bad:
        logging.info("失效链接（前 20 个）：")
        for u in bad[:20]:
            logging.info(f"  ❌ {u}  ({results[u]['reason']})")
    logging.info("结果已写入 link_status.json")


if __name__ == '__main__':
    main()
