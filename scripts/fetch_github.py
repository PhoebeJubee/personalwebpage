#!/usr/bin/env python3
"""抓取 GitHub 用户仓库并输出为 static/data/github.json。

若 config 中设置了 featured_repos 则只保留指定仓库，否则取 star 最高的前 12 个非 fork 仓库。
"""
import configparser
import json
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "data")
OUT_FILE = os.path.join(OUT_DIR, "github.json")

API = "https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
HEADERS = {"User-Agent": "PersonalSite/1.0", "Accept": "application/vnd.github+json"}


def load_cfg():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    username = cfg.get("github", "username", fallback="").strip()
    featured = cfg.get("github", "featured_repos", fallback="").strip()
    featured = [x.strip() for x in featured.split(",") if x.strip()]
    return username, featured


def fetch_repos(username):
    resp = requests.get(API.format(username=username), headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize(r):
    return {
        "name": r.get("name", ""),
        "description": r.get("description") or "",
        "language": r.get("language") or "",
        "stargazers_count": r.get("stargazers_count", 0),
        "forks_count": r.get("forks_count", 0),
        "html_url": r.get("html_url", ""),
        "topics": r.get("topics") or [],
    }


def main():
    username, featured = load_cfg()
    if not username or username == "YOUR_GITHUB_USERNAME":
        print("[github] 未配置 username，写出空数据。请在 scripts/config.ini 填写 [github] username")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    try:
        repos = fetch_repos(username)
    except Exception as e:
        print(f"[github] 抓取失败: {e}", file=sys.stderr)
        print("[github] 写出空数据，站点仍可构建")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    repos = [r for r in repos if not r.get("fork")]
    if featured:
        wanted = {name.lower() for name in featured}
        repos = [r for r in repos if r.get("name", "").lower() in wanted]
    else:
        repos.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
        repos = repos[:12]

    out = [normalize(r) for r in repos]
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[github] 已写入 {len(out)} 个仓库 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
