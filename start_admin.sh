#!/bin/bash
# 个人网站管理面板启动脚本
# 双击或在终端运行此脚本即可打开管理面板

cd "$(dirname "$0")"
echo "启动管理面板..."
echo "浏览器打开: http://127.0.0.1:5000"
echo "按 Ctrl+C 停止"
echo ""

# 尝试打开浏览器
(sleep 1 && xdg-open http://127.0.0.1:5000 2>/dev/null || open http://127.0.0.1:5000 2>/dev/null) &

python3 scripts/admin/app.py
