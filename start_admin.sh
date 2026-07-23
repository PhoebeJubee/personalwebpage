#!/bin/bash
# 个人网站管理面板启动脚本
# 双击或在终端运行此脚本即可打开管理面板

cd "$(dirname "$0")"

echo "清理旧进程..."

# 按进程名杀
pkill -f "hugo server" 2>/dev/null
pkill -f "admin/app.py" 2>/dev/null

# 按端口杀：占用 5000 和 1319 的进程
for port in 5000 1319; do
  pid=$(lsof -ti :$port 2>/dev/null)
  [ -n "$pid" ] && kill -9 $pid 2>/dev/null
done

sleep 1

# 清理 Hugo 构建缓存
rm -rf resources/_gen

echo "启动管理面板..."
echo "浏览器打开: http://127.0.0.1:5000"
echo "按 Ctrl+C 停止"
echo ""

# 尝试打开浏览器
(sleep 2 && xdg-open http://127.0.0.1:5000 2>/dev/null || open http://127.0.0.1:5000 2>/dev/null) &

python3 scripts/admin/app.py
