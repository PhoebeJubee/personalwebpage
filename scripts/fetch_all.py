#!/usr/bin/env python3
"""一键抓取全部数据源：Bangumi / Bilibili / GitHub。"""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")


def run(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


if __name__ == "__main__":
    for script in ("fetch_bangumi.py", "fetch_bilibili.py", "fetch_github.py"):
        print(f"===== {script} =====")
        run(script)
