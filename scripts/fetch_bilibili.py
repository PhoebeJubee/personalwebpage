#!/usr/bin/env python3
"""抓取 B 站 UP 主投稿视频并输出为 static/data/bilibili.json。

使用非 WBI 接口（x/space/arc/search），本地直抓，规避前端 CORS 与 WBI 签名问题。
"""
import configparser
import json
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "data")
OUT_FILE = os.path.join(OUT_DIR, "bilibili.json")

API = "https://api.bilibili.com/x/space/arc/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://space.bilibili.com",
}


def load_uid():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    return cfg.get("bilibili", "uid", fallback="").strip()


def fetch_videos(mid, ps=12):
    videos = []
    pn = 1
    while True:
        params = {
            "mid": mid,
            "ps": ps,
            "tid": 0,
            "pn": pn,
            "keyword": "",
            "order": "pubdate",
        }
        resp = requests.get(API, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"API code={data.get('code')} message={data.get('message')}")
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
