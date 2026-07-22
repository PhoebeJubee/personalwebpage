#!/usr/bin/env python3
"""抓取 Bangumi 游戏收藏（subject_type=4）并输出为 static/data/bangumi.json。

修复原前端脚本的两个 bug：
  - updated_at 是 ISO 字符串，不能当 Unix 时间戳乘 1000
  - tags 在收藏项顶层（item.tags），不在 subject 里
"""
import configparser
import json
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "data")
OUT_FILE = os.path.join(OUT_DIR, "bangumi.json")

API = "https://api.bgm.tv/v0/users/{uid}/collections?subject_type=4&limit=50&offset={offset}"
HEADERS = {"User-Agent": "PersonalSite/1.0 (https://github.com)"}


def _load_cfg():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    return cfg


def load_uid():
    return _load_cfg().get("bangumi", "uid", fallback="").strip()


def _load_proxies():
    cfg = _load_cfg()
    url = cfg.get("proxy", "url", fallback="").strip()
    if url:
        return {"http": url, "https": url}
    return None


def _get_with_fallback(url, **kwargs):
    proxies = kwargs.pop("proxies", None) or _load_proxies()
    try:
        return requests.get(url, **kwargs)
    except requests.ConnectionError:
        if proxies:
            print(f"  [proxy] 直连失败，使用代理重试: {url[:80]}")
            return requests.get(url, proxies=proxies, **kwargs)
        raise


def fetch_all(uid):
    items = []
    offset = 0
    limit = 50
    while True:
        url = API.format(uid=uid, offset=offset)
        resp = _get_with_fallback(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        page = data.get("data") or []
        items.extend(page)
        total = data.get("total", 0)
        if not page or len(items) >= total:
            break
        offset += limit
        if offset > total:
            break
    return items


def normalize(item):
    subject = item.get("subject") or {}
    images = subject.get("images") or {}
    cover = images.get("large") or images.get("medium") or images.get("small") or ""
    return {
        "name": subject.get("name", ""),
        "name_cn": subject.get("name_cn", "") or subject.get("name", ""),
        "date": subject.get("date", ""),
        "cover": cover,
        "rate": item.get("rate", 0) or 0,
        "type": item.get("type", 0),
        "updated_at": item.get("updated_at", ""),
        "tags": item.get("tags") or [],
    }


def _load_existing_hidden():
    if not os.path.exists(OUT_FILE):
        return {}
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            old = json.load(f)
        return {g["name"]: g.get("hidden", False) for g in old if g.get("name")}
    except Exception:
        return {}


def main():
    uid = load_uid()
    if not uid or uid == "YOUR_BANGUMI_UID":
        print("[bangumi] 未配置 uid，写出空数据。请在 scripts/config.ini 填写 [bangumi] uid")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    try:
        raw = fetch_all(uid)
    except Exception as e:
        print(f"[bangumi] 抓取失败: {e}", file=sys.stderr)
        print("[bangumi] 写出空数据，站点仍可构建（页面会提示暂无记录）")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    hidden_map = _load_existing_hidden()
    games = [normalize(it) for it in raw]
    for g in games:
        if g["name"] in hidden_map:
            g["hidden"] = hidden_map[g["name"]]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)
    print(f"[bangumi] 已写入 {len(games)} 条游戏记录 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
