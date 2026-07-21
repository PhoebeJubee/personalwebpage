#!/usr/bin/env python3
"""抓取 B 站 UP 主投稿视频并输出为 static/data/bilibili.json。

WBI 签名 + Cookie 链流程：
  1. /x/frontend/finger/spi → buvid3
  2. /x/web-interface/nav → img_key + sub_key
  3. mixin_key 混淆 + wts → MD5 生成 w_rid
  4. /x/space/wbi/arc/search 带签名 + 显式 Cookie 请求

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
    from curl_cffi import requests as http
    IMPERSONATE = "chrome120"
except ImportError:
    import requests as http
    IMPERSONATE = None

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


def load_uid():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    return cfg.get("bilibili", "uid", fallback="").strip()


def _http_get(url, **kwargs):
    kwargs.setdefault("timeout", 15)
    if IMPERSONATE:
        kwargs.setdefault("impersonate", IMPERSONATE)
    return http.get(url, **kwargs)


def _get_wbi_keys():
    spi = _http_get(f"{API_BASE}/x/frontend/finger/spi").json()
    buvid3 = spi.get("data", {}).get("b_3", "")

    nav = _http_get(f"{API_BASE}/x/web-interface/nav").json()
    wbi_img = nav.get("data", {}).get("wbi_img", {})
    img_key = wbi_img.get("img_url", "").rsplit("/", 1)[-1].split(".")[0]
    sub_key = wbi_img.get("sub_url", "").rsplit("/", 1)[-1].split(".")[0]

    raw = img_key + sub_key
    mixin_key = "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]
    return buvid3, mixin_key


def _sign(params, mixin_key):
    params["wts"] = str(int(time.time()))
    params_sorted = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params_sorted)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params_sorted["w_rid"] = w_rid
    return urllib.parse.urlencode(params_sorted)


def fetch_videos(mid, ps=12, max_retry=3):
    buvid3, mixin_key = _get_wbi_keys()

    headers = {
        "User-Agent": UA,
        "Referer": f"https://space.bilibili.com/{mid}/video",
        "Origin": "https://space.bilibili.com",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": f"buvid3={buvid3}",
    }

    videos = []
    pn = 1
    while True:
        params = {
            "mid": mid,
            "ps": str(ps),
            "tid": "0",
            "pn": str(pn),
            "order": "pubdate",
        }
        query = _sign(dict(params), mixin_key)

        last_err = None
        for attempt in range(max_retry):
            resp = _http_get(
                f"{API_BASE}/x/space/wbi/arc/search?{query}",
                headers=headers,
            )
            ct = resp.headers.get("content-type", "")
            if "json" not in ct:
                last_err = f"HTTP {resp.status_code} (非 JSON 响应)"
                if attempt < max_retry - 1:
                    time.sleep(2 ** attempt)
                continue
            data = resp.json()
            if data.get("code") == 0:
                break
            last_err = f"code={data.get('code')} message={data.get('message')}"
            if attempt < max_retry - 1:
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"Bilibili API 失败 ({last_err})")

        vlist = data.get("data", {}).get("list", {}).get("vlist", [])
        videos.extend(vlist)
        page = data.get("data", {}).get("page", {})
        count = page.get("count", 0)
        if not vlist or len(videos) >= count or len(videos) >= ps:
            break
        pn += 1
    return videos[:ps]


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


def main():
    uid = load_uid()
    if not uid or uid == "YOUR_BILIBILI_UID":
        print("[bilibili] 未配置 uid，写出空数据。请在 scripts/config.ini 填写 [bilibili] uid")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    try:
        raw = fetch_videos(uid)
    except Exception as e:
        print(f"[bilibili] 抓取失败: {e}", file=sys.stderr)
        print("[bilibili] 写出空数据，站点仍可构建")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    hidden_map = _load_existing_hidden()
    videos = [normalize(v) for v in raw]
    for v in videos:
        if v["bvid"] in hidden_map:
            v["hidden"] = hidden_map[v["bvid"]]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"[bilibili] 已写入 {len(videos)} 条视频 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
