---
title: "Vibe Coding"
description: "我的 GitHub 开源项目展示"
showDate: false
showReadingTime: false
---

这里展示我的开源项目。

<script>
// 数据由本地脚本 scripts/fetch_github.py 抓取并生成 static/data/github.json
// 修改 GitHub 账号/指定项目请编辑 scripts/config.ini 的 [github]，然后重新运行脚本
const GITHUB_DATA_URL = '/data/github.json';

const LANGUAGE_COLORS = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Java: '#b07219',
  Go: '#00ADD8',
  Rust: '#dea584',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Vue: '#41b883',
  'C++': '#f34b7d',
  C: '#555555',
  Shell: '#89e051'
};

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderProjectCard(repo) {
  const languageColor = LANGUAGE_COLORS[repo.language] || '#8b8b8b';
  const topics = (repo.topics || []).slice(0, 5);

  return `
    <a href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener" style="text-decoration: none; color: inherit; display: block; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; border-left: 4px solid #3b82f6; transition: all 0.3s; margin-bottom: 16px;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">
      <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #1f2937;">${escapeHtml(repo.name)}</div>
      <div style="font-size: 14px; color: #6b7280; margin-bottom: 12px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">${escapeHtml(repo.description || '暂无描述')}</div>
      <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 16px; font-size: 14px; color: #6b7280;">
        ${repo.language ? `
          <span style="display: flex; align-items: center; gap: 4px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background: ${languageColor};"></span>
            ${escapeHtml(repo.language)}
          </span>
        ` : ''}
        <span style="display: flex; align-items: center; gap: 4px;">⭐ ${repo.stargazers_count}</span>
        <span style="display: flex; align-items: center; gap: 4px;">🍴 ${repo.forks_count}</span>
      </div>
      ${topics.length > 0 ? `
        <div style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px;">
          ${topics.map(t => `<span style="padding: 2px 8px; border-radius: 12px; font-size: 12px; background: #dbeafe; color: #1e40af;">${escapeHtml(t)}</span>`).join('')}
        </div>
      ` : ''}
    </a>
  `;
}

async function loadGitHubProjects() {
  const container = document.getElementById('github-projects');
  try {
    const response = await fetch(GITHUB_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const repos = await response.json();
    if (!Array.isArray(repos) || repos.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无项目，请先运行 scripts/fetch_github.py 抓取数据。</p>';
      return;
    }
    container.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;">
        ${repos.map(renderProjectCard).join('')}
      </div>
    `;
  } catch (error) {
    console.error('加载 GitHub 项目失败:', error);
    container.innerHTML = `
      <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;">
        <p style="color: #856404; font-weight: 500;">项目加载失败</p>
        <p style="color: #856404; font-size: 14px; margin-top: 8px;">请确认已运行脚本生成 static/data/github.json，且已重新构建站点。</p>
        <p style="color: #856404; font-size: 12px; margin-top: 4px;">错误: ${error.message}</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', loadGitHubProjects);
</script>

<div id="github-projects">
  <p style="color: #666;">正在加载项目...</p>
</div>
