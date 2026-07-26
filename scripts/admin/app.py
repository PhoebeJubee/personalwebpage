#!/usr/bin/env python3
"""个人网站管理面板 - Flask 后端。

提供配置编辑、数据查看/编辑、一键抓取、iframe 实时预览等功能。
启动时自动拉起 Hugo dev server，退出时自动清理。
"""
import atexit
import configparser
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time

import tomllib
from flask import Flask, jsonify, render_template, request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, "scripts")
DATA_DIR = os.path.join(ROOT, "static", "data")
CONFIG_FILE = os.path.join(SCRIPTS, "config.ini")
PARAMS_FILE = os.path.join(ROOT, "config", "_default", "params.toml")
WORDCLOUD_CONFIG_FILE = os.path.join(DATA_DIR, "wordcloud-config.json")

HUGO_PORT = 1319
HUGO_URL = f"http://127.0.0.1:{HUGO_PORT}/personalwebpage"

PAGE_MAP = {
    "bangumi": "timeline",
    "bilibili": "gaming",
    "github": "projects",
}

SOURCES = {
    "bangumi": {"script": "fetch_bangumi.py", "label": "Bangumi"},
    "bilibili": {"script": "fetch_bilibili.py", "label": "Bilibili"},
    "github": {"script": "fetch_github.py", "label": "GitHub"},
}

_here = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(_here, "templates"))

fetch_status = {"running": False, "current": "", "log": [], "last_run": {}}
_hugo_proc = None


# ── Hugo server management ──────────────────────────────────────────

def _start_hugo():
    global _hugo_proc
    if _hugo_proc and _hugo_proc.poll() is None:
        return
    cmd = [
        "hugo", "server", "-D", "--port", str(HUGO_PORT),
        "--bind", "127.0.0.1",
        "--baseURL", f"http://127.0.0.1:{HUGO_PORT}/personalwebpage/",
        "--disableLiveReload",
    ]
    _hugo_proc = subprocess.Popen(
        cmd, cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    _wait_hugo_ready()


def _wait_hugo_ready(timeout=15):
    import urllib.request
    import urllib.error
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(HUGO_URL, timeout=2)
            return True
        except Exception:
            time.sleep(0.3)
    return False


def _stop_hugo():
    global _hugo_proc
    if _hugo_proc is None:
        return
    try:
        os.killpg(os.getpgid(_hugo_proc.pid), signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        _hugo_proc.wait(timeout=3)
    except Exception:
        try:
            os.killpg(os.getpgid(_hugo_proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
    _hugo_proc = None


atexit.register(_stop_hugo)


# ── Helpers ──────────────────────────────────────────────────────────

def _data_file(source):
    return os.path.join(DATA_DIR, f"{source}.json")


def _read_json(source):
    path = _data_file(source)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(source, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_data_file(source), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    assets_dir = os.path.join(ROOT, "assets", "data")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, f"{source}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _read_config():
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    result = {}
    for section in cfg.sections():
        result[section] = dict(cfg.items(section))
    return result


def _write_config(data):
    cfg = configparser.ConfigParser()
    for section, items in data.items():
        cfg[section] = items
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


# ── params.toml helpers ─────────────────────────────────────────────

def _read_params():
    if not os.path.exists(PARAMS_FILE):
        return {}
    with open(PARAMS_FILE, "rb") as f:
        return tomllib.load(f)


def _write_params(data):
    lines = []
    _dump_toml(data, lines, root=True)
    with open(PARAMS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _dump_toml(data, lines, root=True, prefix=""):
    simple = {}
    sections = {}
    for k, v in data.items():
        if isinstance(v, dict):
            sections[k] = v
        else:
            simple[k] = v
    for k, v in simple.items():
        lines.append(f"{k} = {_toml_value(v)}")
    for k, v in sections.items():
        heading = f"{prefix}.{k}" if prefix else k
        if _is_inline_section(v):
            lines.append(f"\n[{heading}]")
            for sk, sv in v.items():
                lines.append(f"{sk} = {_toml_value(sv)}")
        else:
            lines.append(f"\n[{heading}]")
            _dump_toml(v, lines, root=False, prefix=heading)


def _is_inline_section(d):
    return all(not isinstance(v, dict) for v in d.values())


def _toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        if any(c in v for c in '[]{}#,=\n"\\'):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return f'"{v}"'
    if isinstance(v, list):
        items = []
        for item in v:
            if isinstance(item, dict):
                inner = ", ".join(f'{ik} = {_toml_value(iv)}' for ik, iv in item.items())
                items.append(f"{{ {inner} }}")
            else:
                items.append(_toml_value(item))
        return "[" + ", ".join(items) + "]"
    return f'"{v}"'


def _run_fetch(source):
    fetch_status["running"] = True
    fetch_status["log"] = []
    fetch_status["current"] = source

    if source == "all":
        scripts = ["fetch_bangumi.py", "fetch_bilibili.py", "fetch_github.py"]
    else:
        scripts = [SOURCES[source]["script"]]

    for script in scripts:
        fetch_status["log"].append(f">>> 运行 {script}...")
        try:
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS, script)],
                capture_output=True, text=True, timeout=120, cwd=ROOT,
            )
            if result.stdout.strip():
                fetch_status["log"].append(result.stdout.strip())
            if result.returncode != 0 and result.stderr.strip():
                fetch_status["log"].append(f"[错误] {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            fetch_status["log"].append(f"[超时] {script} 执行超过 120 秒")
        except Exception as e:
            fetch_status["log"].append(f"[异常] {e}")

    fetch_status["running"] = False
    fetch_status["current"] = ""
    fetch_status["last_run"][source] = time.strftime("%Y-%m-%d %H:%M:%S")


# ── Routes ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("admin.html", hugo_url=HUGO_URL)


@app.route("/api/status")
def api_status():
    result = {}
    for source in SOURCES:
        path = _data_file(source)
        if os.path.exists(path):
            size = os.path.getsize(path)
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
            data = _read_json(source)
            count = len(data) if isinstance(data, list) else 0
            hidden_count = sum(1 for d in data if isinstance(d, dict) and d.get("hidden"))
            result[source] = {
                "exists": True, "size": size, "mtime": mtime,
                "count": count, "hidden_count": hidden_count,
            }
        else:
            result[source] = {"exists": False, "size": 0, "mtime": "", "count": 0, "hidden_count": 0}
    return jsonify(result)


@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(_read_config())


@app.route("/api/config", methods=["PUT"])
def api_save_config():
    data = request.get_json()
    _write_config(data)
    return jsonify({"ok": True})


@app.route("/api/params", methods=["GET"])
def api_get_params():
    return jsonify(_read_params())


@app.route("/api/params", methods=["PUT"])
def api_save_params():
    data = request.get_json()
    _write_params(data)
    return jsonify({"ok": True})


# ── Wordcloud config ───────────────────────────────────────────────

WORDCLOUD_DEFAULTS = {
    "minCount": 2,
    "maxTags": 80,
    "canvasWidth": 700,
    "canvasHeight": 500,
    "fontSizeMin": 12,
    "fontSizeMax": 54,
    "rotateRatio": 0.4,
    "blockedWords": [],
}


def _read_wordcloud_config():
    if not os.path.exists(WORDCLOUD_CONFIG_FILE):
        return dict(WORDCLOUD_DEFAULTS)
    try:
        with open(WORDCLOUD_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(WORDCLOUD_DEFAULTS)
        merged.update(data)
        return merged
    except Exception:
        return dict(WORDCLOUD_DEFAULTS)


def _write_wordcloud_config(data):
    merged = dict(WORDCLOUD_DEFAULTS)
    merged.update(data)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(WORDCLOUD_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    assets_dir = os.path.join(ROOT, "assets", "data")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "wordcloud-config.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)


@app.route("/api/wordcloud-config", methods=["GET"])
def api_get_wordcloud_config():
    return jsonify(_read_wordcloud_config())


@app.route("/api/wordcloud-config", methods=["PUT"])
def api_save_wordcloud_config():
    data = request.get_json()
    _write_wordcloud_config(data)
    return jsonify({"ok": True})


CAREER_FILE = os.path.join(DATA_DIR, "career.json")


def _read_career():
    if not os.path.exists(CAREER_FILE):
        return {}
    with open(CAREER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_career(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CAREER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    assets_dir = os.path.join(ROOT, "assets", "data")
    os.makedirs(assets_dir, exist_ok=True)
    with open(os.path.join(assets_dir, "career.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/api/career", methods=["GET"])
def api_get_career():
    return jsonify(_read_career())


@app.route("/api/career", methods=["PUT"])
def api_save_career():
    data = request.get_json()
    _write_career(data)
    return jsonify({"ok": True})


@app.route("/api/data/<source>", methods=["GET"])
def api_get_data(source):
    if source not in SOURCES:
        return jsonify({"error": "unknown source"}), 404
    return jsonify(_read_json(source))


@app.route("/api/data/<source>", methods=["PUT"])
def api_save_data(source):
    if source not in SOURCES:
        return jsonify({"error": "unknown source"}), 404
    data = request.get_json()
    _write_json(source, data)
    return jsonify({"ok": True, "count": len(data) if isinstance(data, list) else 0})


@app.route("/api/fetch/<source>", methods=["POST"])
def api_fetch(source):
    if source not in SOURCES and source != "all":
        return jsonify({"error": "unknown source"}), 404
    if fetch_status["running"]:
        return jsonify({"error": "正在抓取中，请稍后"}), 409
    thread = threading.Thread(target=_run_fetch, args=(source,), daemon=True)
    thread.start()
    return jsonify({"ok": True, "message": f"开始抓取 {source}"})


@app.route("/api/fetch/status")
def api_fetch_status():
    return jsonify(fetch_status)


@app.route("/api/toggle-hidden/<source>", methods=["POST"])
def api_toggle_hidden(source):
    if source not in SOURCES:
        return jsonify({"error": "unknown source"}), 404
    body = request.get_json() or {}
    index = body.get("index")
    if index is None:
        return jsonify({"error": "missing index"}), 400
    data = _read_json(source)
    if not isinstance(data, list) or index < 0 or index >= len(data):
        return jsonify({"error": "invalid index"}), 400
    item = data[index]
    item["hidden"] = not item.get("hidden", False)
    _write_json(source, data)
    return jsonify({"ok": True, "hidden": item["hidden"]})


@app.route("/api/data/<source>/<int:index>", methods=["PATCH"])
def api_patch_item(source, index):
    if source not in SOURCES:
        return jsonify({"error": "unknown source"}), 404
    data = _read_json(source)
    if not isinstance(data, list) or index < 0 or index >= len(data):
        return jsonify({"error": "invalid index"}), 400
    updates = request.get_json() or {}
    item = data[index]
    for k, v in updates.items():
        item[k] = v
    _write_json(source, data)
    return jsonify({"ok": True, "item": item})


@app.route("/api/hugo-status")
def api_hugo_status():
    if _hugo_proc and _hugo_proc.poll() is None:
        return jsonify({"running": True, "url": HUGO_URL})
    return jsonify({"running": False})


if __name__ == "__main__":
    print(f"管理面板启动: http://127.0.0.1:5000")
    print(f"项目根目录: {ROOT}")
    print(f"启动 Hugo dev server (端口 {HUGO_PORT})...")
    _start_hugo()
    if _hugo_proc and _hugo_proc.poll() is None:
        print(f"Hugo dev server 就绪: {HUGO_URL}")
    else:
        print("[警告] Hugo dev server 启动失败，预览功能不可用")
    print("按 Ctrl+C 停止")
    app.run(host="127.0.0.1", port=5000, debug=False)
