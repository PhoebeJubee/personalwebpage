#!/usr/bin/env python3
"""抓取 B 站 UP 主投稿视频并输出为 static/data/bilibili.json。

Session + WBI 签名流程：
  1. 创建 curl_cffi.Session，先访问 bilibili.com 获取初始 Cookie（b_nut）
  2. /x/frontend/finger/spi → buvid3（追加到 session cookie）
  3. /x/web-interface/nav → img_key + sub_key → mixin_key
  4. /x/space/wbi/arc/search 翻页抓取，session 自动维护 Cookie 链

优先使用 curl_cffi 模拟 Chrome TLS 指纹（需 pip install curl_cffi），
回退到标准 requests。
"""
import configparser
import hashlib
import json
import os
import sys
import time
import urllib.parse

try:
    from curl_cffi import requests as _http_lib
    HAS_CURL_CFFI = True
except ImportError:
    import requests as _http_lib
    HAS_CURL_CFFI = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "data")
OUT_FILE = os.path.join(OUT_DIR, "bilibili.json")

API_BASE = "https://api.bilibili.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]

PAGE_SIZE = 30
PAGE_DELAY = 2.0
MAX_RETRY = 3
RETRY_BASE_DELAY = 3


def _load_cfg():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    return cfg


def _load_proxies():
    cfg = _load_cfg()
    url = cfg.get("proxy", "url", fallback="").strip()
    if url:
        return {"http": url, "https": url}
    return None


def load_uid():
    return _load_cfg().get("bilibili", "uid", fallback="").strip()


def _create_session():
    if HAS_CURL_CFFI:
        s = _http_lib.Session(impersonate="chrome120")
    else:
        s = _http_lib.Session()
        s.headers.update({"User-Agent": UA})
    return s


def _session_get(s, url, **kwargs):
    kwargs.setdefault("timeout", 15)
    try:
        return s.get(url, **kwargs)
    except Exception:
        proxies = _load_proxies()
        if proxies:
            s.proxies.update(proxies)
            return s.get(url, **kwargs)
        raise


def _init_session(s):
    _session_get(s, "https://www.bilibili.com")
    time.sleep(1)

    spi = _session_get(s, f"{API_BASE}/x/frontend/finger/spi").json()
    buvid3 = spi.get("data", {}).get("b_3", "")
    s.cookies.set("buvid3", buvid3, domain=".bilibili.com")
    time.sleep(0.5)

    nav = _session_get(s, f"{API_BASE}/x/web-interface/nav").json()
    wbi_img = nav.get("data", {}).get("wbi_img", {})
    img_key = wbi_img.get("img_url", "").rsplit("/", 1)[-1].split(".")[0]
    sub_key = wbi_img.get("sub_url", "").rsplit("/", 1)[-1].split(".")[0]

    raw = img_key + sub_key
    mixin_key = "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]
    return mixin_key


def _sign(params, mixin_key):
    params["wts"] = str(int(time.time()))
    params_sorted = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params_sorted)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params_sorted["w_rid"] = w_rid
    return urllib.parse.urlencode(params_sorted)


def fetch_videos(mid):
    s = _create_session()
    mixin_key = _init_session(s)
    print(f"  Session 初始化完成，开始抓取 mid={mid}")

    headers = {
        "Referer": f"https://space.bilibili.com/{mid}/video",
        "Origin": "https://space.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    videos = []
    pn = 1
    count = None

    while True:
        params = {
            "mid": mid,
            "ps": str(PAGE_SIZE),
            "tid": "0",
            "pn": str(pn),
            "order": "pubdate",
        }
        query = _sign(dict(params), mixin_key)

        last_err = None
        data = None
        for attempt in range(MAX_RETRY):
            resp = _session_get(
                s,
                f"{API_BASE}/x/space/wbi/arc/search?{query}",
                headers=headers,
            )
            ct = resp.headers.get("content-type", "")
            if "json" not in ct:
                last_err = f"HTTP {resp.status_code} (非 JSON 响应)"
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            data = resp.json()
            code = data.get("code")
            if code == 0:
                break
            last_err = f"code={code} message={data.get('message')}"
            if code in (-352, -412):
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
            else:
                time.sleep(1)
        else:
            raise RuntimeError(f"Bilibili API 失败 (第 {pn} 页, {last_err})")

        vlist = data.get("data", {}).get("list", {}).get("vlist", [])
        if count is None:
            count = data.get("data", {}).get("page", {}).get("count", 0)
        videos.extend(vlist)
        print(f"  第 {pn} 页: 获取 {len(vlist)} 条 (累计 {len(videos)}/{count})")

        if not vlist or len(videos) >= count:
            break
        pn += 1
        time.sleep(PAGE_DELAY)

    return videos


def normalize(v):
    return {
        "bvid": v.get("bvid", ""),
        "title": v.get("title", ""),
        "pic": v.get("pic", ""),
        "duration": v.get("duration", 0),
        "play": v.get("play", 0),
        "video_review": v.get("video_review", 0),
        "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
    }


def _load_existing_hidden():
    if not os.path.exists(OUT_FILE):
        return {}
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            old = json.load(f)
        return {v["bvid"]: v.get("hidden", False) for v in old if v.get("bvid")}
    except Exception:
        return {}


def _write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    uid = load_uid()
    if not uid or uid == "YOUR_BILIBILI_UID":
        print("[bilibili] 未配置 uid，写出空数据。请在 scripts/config.ini 填写 [bilibili] uid")
        os.makedirs(OUT_DIR, exist_ok=True)
        _write_json([], OUT_FILE)
        _write_json([], os.path.join(ROOT, "assets", "data", "bilibili.json"))
        return

    try:
        raw = fetch_videos(uid)
    except Exception as e:
        print(f"[bilibili] 抓取失败: {e}", file=sys.stderr)
        print("[bilibili] 保留历史数据，站点仍可构建")
        return

    hidden_map = _load_existing_hidden()
    videos = [normalize(v) for v in raw]
    for v in videos:
        if v["bvid"] in hidden_map:
            v["hidden"] = hidden_map[v["bvid"]]
    _write_json(videos, OUT_FILE)
    _write_json(videos, os.path.join(ROOT, "assets", "data", "bilibili.json"))
    print(f"[bilibili] 已写入 {len(videos)} 条视频 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
