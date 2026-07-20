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

### 4. 配置数据源

#### Bangumi 游戏记录
编辑 `content/timeline/_index.md`，修改：
```javascript
const BANGUMI_UID = '你的Bangumi UID';
```

#### Bilibili 视频
编辑 `content/gaming/_index.md`，修改：
```javascript
const BILIBILI_UID = '你的Bilibili UID';
```

#### GitHub 项目
编辑 `content/projects/_index.md`，修改：
```javascript
const GITHUB_USERNAME = '你的GitHub用户名';
// 可选：指定要展示的项目
const FEATURED_REPOS = ['project1', 'project2'];
```

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

- 添加游戏记录：更新 Bangumi 即可自动同步
- 添加视频：更新 Bilibili 即可自动同步
- 添加文章：在 `content/articles/` 下新建 Markdown 文件
- 添加项目：更新 GitHub 即可自动同步
- 修改大图：替换 `static/images/` 中的图片

## 技术栈

- [Hugo](https://gohugo.io/) - 静态站点生成器
- [Blowfish](https://blowfish.page/) - Hugo 主题 (Tailwind CSS)
- Bangumi API - 游戏数据
- Bilibili API - 视频数据
- GitHub API - 开源项目数据
