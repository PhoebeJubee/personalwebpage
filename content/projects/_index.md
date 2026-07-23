---
title: "Vibe Coding"
description: "我的 GitHub 开源项目展示"
showDate: false
showReadingTime: false
---

这里展示我的开源项目。

<script src="../lib/marked.min.js"></script>
<script>
const GITHUB_DATA_URL = '../data/github.json';

const LANGUAGE_COLORS = {
  JavaScript: '#f1e05a', TypeScript: '#3178c6', Python: '#3572A5',
  HTML: '#e34c26', CSS: '#563d7c', Java: '#b07219', Go: '#00ADD8',
  Rust: '#dea584', Ruby: '#701516', PHP: '#4F5D95', Vue: '#41b883',
  'C++': '#f34b7d', C: '#555555', Shell: '#89e051', Dart: '#00B4AB',
  Kotlin: '#A97BFF', Swift: '#F05138'
};

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderProjectCard(repo, idx) {
  const langColor = LANGUAGE_COLORS[repo.language] || '#8b8b8b';
  const topics = (repo.topics || []).slice(0, 6);
  const hasReadme = repo.readme && repo.readme.trim().length > 10;
  const desc = repo.custom_description || repo.description ? escapeHtml(repo.custom_description || repo.description) : '';
  const updatedAt = repo.updated_at ? new Date(repo.updated_at).toLocaleDateString('zh-CN') : '';

  return `
    <div class="project-card" style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; transition: all 0.3s; overflow: hidden;" onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 8px 24px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'">
      <!-- 顶部色条 -->
      <div style="height: 3px; background: linear-gradient(90deg, ${langColor}, #3b82f6);"></div>
      
      <div style="padding: 20px; display: flex; gap: 20px;">
        <!-- 左侧：主信息 -->
        <div style="flex: 1; min-width: 0;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
            <svg style="width: 20px; height: 20px; color: #6b7280; flex-shrink: 0;" fill="currentColor" viewBox="0 0 16 16"><path d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"/></svg>
            <a href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener" style="font-size: 18px; font-weight: 700; color: #1d4ed8; text-decoration: none; word-break: break-all;">${escapeHtml(repo.name)}</a>
          </div>
          ${desc ? `<p style="font-size: 14px; color: #4b5563; line-height: 1.6; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">${desc}</p>` : ''}
          ${topics.length > 0 ? `
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
              ${topics.map(t => `<span style="padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;">${escapeHtml(t)}</span>`).join('')}
            </div>
          ` : ''}
          ${hasReadme ? `
            <button onclick="toggleReadme(${idx})" id="readme-btn-${idx}" style="font-size: 13px; color: #3b82f6; background: none; border: 1px solid #bfdbfe; border-radius: 6px; padding: 4px 14px; cursor: pointer; transition: all 0.2s; font-weight: 500;" onmouseover="this.style.background='#eff6ff';this.style.borderColor='#3b82f6'" onmouseout="this.style.background='none';this.style.borderColor='#bfdbfe'">📄 查看详情</button>
          ` : ''}
        </div>
        
        <!-- 右侧：统计信息 -->
        <div style="flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 10px; min-width: 100px;">
          ${repo.language ? `
            <div style="display: flex; align-items: center; gap: 6px; font-size: 13px; color: #4b5563; background: #f9fafb; padding: 4px 12px; border-radius: 20px; border: 1px solid #e5e7eb;">
              <span style="width: 10px; height: 10px; border-radius: 50%; background: ${langColor}; display: inline-block;"></span>
              ${escapeHtml(repo.language)}
            </div>
          ` : ''}
          <div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-end;">
            <div style="display: flex; align-items: center; gap: 4px; font-size: 14px; color: #f59e0b; font-weight: 600;">
              <svg style="width: 16px; height: 16px;" fill="currentColor" viewBox="0 0 16 16"><path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"/></svg>
              ${repo.stargazers_count || 0}
            </div>
          </div>
          ${updatedAt ? `
            <div style="font-size: 11px; color: #9ca3af;">更新于 ${updatedAt}</div>
          ` : ''}
        </div>
      </div>
      
      <!-- README 展开区 -->
      ${hasReadme ? `
        <div id="readme-${idx}" style="display: none; border-top: 1px solid #e5e7eb; background: #fafbfc;">
          <div class="readme-content" style="padding: 20px; font-size: 14px; color: #374151; line-height: 1.7; max-height: 500px; overflow-y: auto;"></div>
        </div>
      ` : ''}
    </div>
  `;
}

const readmeCache = {};
function toggleReadme(idx) {
  const el = document.getElementById('readme-' + idx);
  const btn = document.getElementById('readme-btn-' + idx);
  if (!el) return;
  if (el.style.display === 'none') {
    el.style.display = 'block';
    btn.textContent = '📄 收起';
    btn.style.background = '#eff6ff';
    if (!el.dataset.rendered) {
      const repos = window._githubRepos || [];
      const repo = repos[idx];
      if (repo && repo.readme) {
        try { el.querySelector('.readme-content').innerHTML = marked.parse(repo.readme); }
        catch (e) { el.querySelector('.readme-content').textContent = repo.readme; }
      }
      el.dataset.rendered = '1';
    }
  } else {
    el.style.display = 'none';
    btn.textContent = '📄 查看详情';
    btn.style.background = 'none';
  }
}

async function loadGitHubProjects() {
  const container = document.getElementById('github-projects');
  try {
    const response = await fetch(GITHUB_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const repos = await response.json();
    window._githubRepos = repos;
    if (!Array.isArray(repos) || repos.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无项目，请先运行 scripts/fetch_github.py 抓取数据。</p>';
      return;
    }
    const visible = repos.filter(r => !r.hidden);
    if (visible.length === 0) {
      container.innerHTML = '<p style="color: #666;">所有项目已隐藏。</p>';
      return;
    }
    window._githubRepos = visible;
    container.innerHTML = `<div style="display: flex; flex-direction: column; gap: 16px;">${visible.map((r, i) => renderProjectCard(r, i)).join('')}</div>`;
  } catch (error) {
    console.error('加载 GitHub 项目失败:', error);
    container.innerHTML = `<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;"><p style="color: #856404; font-weight: 500;">项目加载失败</p><p style="color: #856404; font-size: 14px; margin-top: 8px;">请确认已运行脚本生成 static/data/github.json</p></div>`;
  }
}

document.addEventListener('DOMContentLoaded', loadGitHubProjects);
</script>

<style>
.readme-content h1 { font-size: 1.4em; font-weight: bold; margin: 0.5em 0; }
.readme-content h2 { font-size: 1.2em; font-weight: bold; margin: 0.5em 0; }
.readme-content h3 { font-size: 1.05em; font-weight: bold; margin: 0.5em 0; }
.readme-content p { margin: 0.4em 0; }
.readme-content ul { list-style: disc; padding-left: 1.5em; margin: 0.4em 0; }
.readme-content ol { list-style: decimal; padding-left: 1.5em; margin: 0.4em 0; }
.readme-content code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
.readme-content pre { background: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 0.5em 0; }
.readme-content pre code { background: none; color: inherit; padding: 0; }
.readme-content a { color: #3b82f6; text-decoration: underline; }
.readme-content blockquote { border-left: 4px solid #d1d5db; padding-left: 1em; color: #6b7280; margin: 0.5em 0; }
.readme-content img { max-width: 100%; border-radius: 8px; }
@media (max-width: 640px) {
  .project-card > div:nth-child(2) { flex-direction: column !important; }
  .project-card > div:nth-child(2) > div:last-child { flex-direction: row !important; align-items: center !important; min-width: auto !important; }
}
</style>

<div id="github-projects">
  <p style="color: #666;">正在加载项目...</p>
</div>
