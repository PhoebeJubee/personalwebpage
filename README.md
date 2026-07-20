# 个人自媒体主页

基于 Hugo + Blowfish 主题构建的个人网站，适配手机和桌面端。

## 页面结构

- 🎮 **游戏时光** (`/timeline/`) - 从 Bangumi 同步游戏记录和评分
- 🎬 **游戏鉴赏** (`/gaming/`) - 从 Bilibili 同步游戏视频
- 💻 **Vibe Coding** (`/projects/`) - 展示 GitHub 开源项目
- 📝 **文章专栏** (`/articles/`) - 公众号文章和知乎回答
- 💼 **考公求职** (`/career/`) - 大图展示区域

## 快速开始

### 1. 安装 Hugo (extended 版本，需要 0.148+)

```bash
# macOS
brew install hugo

# Windows
scoop install hugo-extended

# Linux (参考 https://gohugo.io/installation/)
```

### 2. 启动本地预览

```bash
cd mysite
hugo server -D
# 访问 http://localhost:1313
```

### 3. 配置个人信息

编辑 `config/_default/params.toml`：

```toml
[author]
  name = "你的名字"
  headline = "自媒体创作者 | 游戏爱好者 | Vibe Coder"
  bio = "个人简介"
  links = [
    { bilibili = "https://space.bilibili.com/你的UID" },
    { zhihu = "https://www.zhihu.com/people/你的ID" },
    { tiktok = "https://www.douyin.com/user/你的ID" },
    { github = "https://github.com/你的用户名" }
  ]
```

### 4. 配置数据源（重要）

三个动态页（游戏时光 / 游戏鉴赏 / Vibe Coding）的数据**不再由前端直接调用平台 API**（浏览器会因 CORS 报 `Failed to fetch`），而是由**本地脚本抓取后生成静态 JSON**，前端读取本地 JSON 渲染。

所有账号统一配置在 **`scripts/config.ini`**：

```ini
[bangumi]
uid = 你的Bangumi用户名或UID

[bilibili]
uid = 你的B站UID

[github]
username = 你的GitHub用户名
featured_repos =        ; 可选，逗号分隔；留空则自动取 star 最高的前 12 个非 fork 仓库
```

> 修改账号只需改这一个文件，无需碰页面代码。

### 5. 抓取数据并构建

```bash
# 一键抓取三个数据源，生成 static/data/{bangumi,bilibili,github}.json
python3 scripts/fetch_all.py
# 或单独抓取：
python3 scripts/fetch_bangumi.py
python3 scripts/fetch_bilibili.py
python3 scripts/fetch_github.py

# 构建站点（JSON 会被自动拷贝到 public/data/）
hugo
```

页面逻辑：
- 游戏时光：读取 `/data/bangumi.json`，展示统计卡片 + 游戏卡片（评分/标签/封面，已修复 `updated_at` 时间戳与 `tags` 字段取值）
- 游戏鉴赏：读取 `/data/bilibili.json`，展示视频卡片网格
- Vibe Coding：读取 `/data/github.json`，展示开源项目卡片

若尚未抓取数据，页面会提示"暂无记录"，**不会一直卡在加载中**。

### 5. 添加文章

在 `content/articles/` 目录下创建 Markdown 文件：

```markdown
---
title: "文章标题"
date: 2026-07-20
description: "文章描述"
source: "公众号"
tags: ["标签1", "标签2"]
---

文章正文内容...
```

### 6. 考公求职大图

将图片放到 `static/images/` 目录，在 `content/career/_index.md` 中插入：

```html
<img src="/images/your-image.jpg" alt="考公求职" style="width: 100%; border-radius: 8px;">
```

## 部署到 GitHub Pages

### 1. 创建 GitHub 仓库

在 GitHub 创建仓库，建议命名为 `yourusername.github.io`。

### 2. 修改 baseURL

编辑 `hugo.toml`：
```toml
baseURL = "https://yourusername.github.io/"
```

### 3. 推送代码

```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/yourusername.github.io.git
git push -u origin main
```

### 4. 配置 GitHub Pages

在仓库 **Settings > Pages** 中：
- Source 选择 **GitHub Actions**
- 保存后自动部署

### 5. 访问网站

打开 `https://yourusername.github.io/`

## 日常维护

- 添加游戏记录：在 Bangumi 更新后，重新运行 `python3 scripts/fetch_all.py && hugo`
- 添加视频：在 B 站更新后，重新运行上面的命令
- 添加文章：在 `content/articles/` 下新建 Markdown 文件（无需跑脚本）
- 添加项目：在 GitHub 更新后，重新运行上面的命令；或用 `featured_repos` 指定展示项
- 修改大图：替换 `static/images/` 中的图片
- 修改账号：只改 `scripts/config.ini`，然后重新抓取

> 提示：三个动态页的数据都是**构建时静态生成**的，所以每次数据变化都要"跑脚本 + 重新构建 + 重新部署"三者缺一不可。

## 技术栈

- [Hugo](https://gohugo.io/) - 静态站点生成器
- [Blowfish](https://blowfish.page/) - Hugo 主题 (Tailwind CSS)
- Bangumi API - 游戏数据
- Bilibili API - 视频数据
- GitHub API - 开源项目数据
