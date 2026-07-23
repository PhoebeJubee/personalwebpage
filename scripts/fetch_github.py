#!/usr/bin/env python3
"""抓取 GitHub 用户仓库并输出为 static/data/github.json。

按最近提交时间排序取前 10 个非 fork 仓库，同时读取每个仓库的 README。
若 config 中设置了 featured_repos 则只保留指定仓库。
"""
import base64
import configparser
import json
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "static", "data")
OUT_FILE = os.path.join(OUT_DIR, "github.json")

API_REPOS = "https://api.github.com/users/{username}/repos?sort=pushed&per_page=30"
API_README = "https://api.github.com/repos/{username}/{repo}/readme"
HEADERS = {"User-Agent": "PersonalSite/1.0", "Accept": "application/vnd.github+json"}

MAX_README_LEN = 3000
MAX_REPOS = 10


def _load_cfg():
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(ROOT, "scripts", "config.ini"))
    return cfg


def load_cfg():
    cfg = _load_cfg()
    username = cfg.get("github", "username", fallback="").strip()
    featured = cfg.get("github", "featured_repos", fallback="").strip()
    featured = [x.strip() for x in featured.split(",") if x.strip()]
    return username, featured


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


def fetch_repos(username):
    resp = _get_with_fallback(API_REPOS.format(username=username), headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_readme(username, repo):
    try:
        resp = _get_with_fallback(
            API_README.format(username=username, repo=repo),
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()
        content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
        if len(content) > MAX_README_LEN:
            content = content[:MAX_README_LEN] + "\n\n...(README 已截断)"
        return content
    except Exception:
        return ""


def normalize(r, readme=""):
    return {
        "name": r.get("name", ""),
        "description": r.get("description") or "",
        "language": r.get("language") or "",
        "stargazers_count": r.get("stargazers_count", 0),
        "forks_count": r.get("forks_count", 0),
        "html_url": r.get("html_url", ""),
        "pushed_at": r.get("pushed_at", ""),
        "topics": r.get("topics") or [],
        "readme": readme,
    }


def _load_existing_hidden():
    if not os.path.exists(OUT_FILE):
        return {}
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            old = json.load(f)
        return {r["name"]: r.get("hidden", False) for r in old if r.get("name")}
    except Exception:
        return {}


def _load_existing_custom_desc():
    if not os.path.exists(OUT_FILE):
        return {}
    try:
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            old = json.load(f)
        return {r["name"]: r.get("custom_description", "") for r in old if r.get("name")}
    except Exception:
        return {}


def main():
    username, featured = load_cfg()
    if not username or username == "YOUR_GITHUB_USERNAME":
        print("[github] 未配置 username，写出空数据。请在 scripts/config.ini 填写 [github] username")
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        assets_dir = os.path.join(ROOT, "assets", "data")
        os.makedirs(assets_dir, exist_ok=True)
        with open(os.path.join(assets_dir, "github.json"), "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return

    try:
        repos = fetch_repos(username)
    except Exception as e:
        print(f"[github] 抓取失败: {e}", file=sys.stderr)
        print("[github] 保留历史数据，站点仍可构建")
        return

    repos = [r for r in repos if not r.get("fork")]
    if featured:
        wanted = {name.lower() for name in featured}
        repos = [r for r in repos if r.get("name", "").lower() in wanted]
    else:
        repos = repos[:MAX_REPOS]

    hidden_map = _load_existing_hidden()
    custom_desc_map = _load_existing_custom_desc()
    out = []
    for r in repos:
        name = r.get("name", "")
        print(f"  [github] 读取 {name} 的 README...")
        readme = fetch_readme(username, name)
        item = normalize(r, readme)
        if name in hidden_map:
            item["hidden"] = hidden_map[name]
        if name in custom_desc_map and custom_desc_map[name]:
            item["custom_description"] = custom_desc_map[name]
        out.append(item)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    assets_dir = os.path.join(ROOT, "assets", "data")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "github.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[github] 已写入 {len(out)} 个仓库 -> {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
