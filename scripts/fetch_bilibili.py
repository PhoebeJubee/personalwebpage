#!/usr/bin/env python3
"""抓取 B 站 UP 主投稿视频并输出为 static/data/bilibili.json。

WBI 签名流程：
  1. /x/frontend/finger/spi → buvid3 cookie
  2. /x/web-interface/nav → img_key + sub_key
  3. mixin_key 混淆 + wts 时间戳 → MD5 生成 w_rid
  4. /x/space/wbi/arc/search 带签名请求数据
"""
import configparser
import hashlib
import json
import os
import sys
import time
import urllib.parse

import requests

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


def _get(session):
    """获取 buvid3 cookie 和 WBI 签名密钥。"""
    # 1. buvid3
    spi = session.get(f"{API_BASE}/x/frontend/finger/spi", timeout=15).json()
    buvid3 = spi.get("data", {}).get("b_3", "")
    if buvid3:
        session.cookies.set("buvid3", buvid3, domain=".bilibili.com")

    # 2. WBI keys
    nav = session.get(f"{API_BASE}/x/web-interface/nav", timeout=15).json()
    wbi_img = nav.get("data", {}).get("wbi_img", {})
    img_url = wbi_img.get("img_url", "")
    sub_url = wbi_img.get("sub_url", "")
    img_key = img_url.rsplit("/", 1)[-1].split(".")[0] if img_url else ""
    sub_key = sub_url.rsplit("/", 1)[-1].split(".")[0] if sub_url else ""
    return img_key, sub_key


def _mixin_key(orig):
    return "".join(orig[i] for i in MIXIN_KEY_ENC_TAB)[:32]


def _sign(params, mixin_key):
    params["wts"] = str(int(time.time()))
    params_sorted = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params_sorted)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params_sorted["w_rid"] = w_rid
    return urllib.parse.urlencode(params_sorted)


def fetch_videos(mid, ps=12, max_retry=3):
    session = requests.Session()
    session.headers.update({
        "User-Agent": UA,
        "Referer": f"https://space.bilibili.com/{mid}/video",
    })

    img_key, sub_key = _get(session)
    mixin_key = _mixin_key(img_key + sub_key)

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
            resp = session.get(
                f"{API_BASE}/x/space/wbi/arc/search?{query}",
                timeout=30,
            )
            resp.raise_for_status()
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

    videos = [normalize(v) for v in raw]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"[bilibili] 已写入 {len(videos)} 条视频 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
