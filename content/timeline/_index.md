---
title: "游戏时光"
description: "从 Bangumi 同步的游戏记录和评分数据"
showDate: false
showReadingTime: false
---

这里展示我的游戏记录和评分数据。

<script>
// 数据由本地脚本 scripts/fetch_bangumi.py 抓取并生成 static/data/bangumi.json
// 修改 Bangumi 账号请编辑 scripts/config.ini 的 [bangumi] uid，然后重新运行脚本
const BANGUMI_DATA_URL = '/data/bangumi.json';

function scoreColor(score) {
  if (score >= 8) return { bg: '#d4edda', fg: '#155724' };
  if (score >= 6) return { bg: '#fff3cd', fg: '#856404' };
  return { bg: '#f8d7da', fg: '#721c24' };
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function renderGameCard(item) {
  // 注意字段已扁平化：name/name_cn/date/cover/rate/tags 均为顶层字段
  const name = item.name_cn || item.name || '';
  const orig = (item.name && item.name !== name) ? item.name : '';
  const score = item.rate || 0;
  const tags = (item.tags || []).slice(0, 5);
  const coverUrl = item.cover || '';
  const c = scoreColor(score);

  return `
    <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 16px; margin-bottom: 16px; display: flex; gap: 16px;">
      ${coverUrl ? `<img src="${escapeHtml(coverUrl)}" alt="${escapeHtml(name)}" style="width: 96px; height: 128px; object-fit: cover; border-radius: 4px;">` : ''}
      <div style="flex: 1;">
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">${escapeHtml(name)}</div>
        ${orig ? `<div style="font-size: 12px; color: #666; margin-bottom: 4px;">${escapeHtml(orig)}</div>` : ''}
        ${item.date ? `<div style="font-size: 14px; color: #666; margin-bottom: 4px;">发售日: ${escapeHtml(item.date)}</div>` : ''}
        ${score > 0 ? `<div style="margin-bottom: 8px;">我的评分: <span style="background: ${c.bg}; color: ${c.fg}; padding: 2px 8px; border-radius: 4px; font-weight: 500;">${score}/10</span></div>` : ''}
        <div style="margin-top: 8px;">
          ${tags.map(t => `<span style="display: inline-block; padding: 2px 8px; margin: 2px 4px 2px 0; border-radius: 12px; font-size: 12px; background: #e3f2fd; color: #1565c0;">${escapeHtml(t)}</span>`).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderStats(games) {
  const totalGames = games.length;
  const rated = games.filter(g => g.rate > 0);
  const avgScore = rated.length ? rated.reduce((s, g) => s + g.rate, 0) / rated.length : 0;
  const perfectGames = rated.filter(g => g.rate >= 9).length;
  // updated_at 是 ISO 字符串（如 2024-01-01T12:00:00+08:00），直接 new Date() 解析
  const thisYear = games.filter(g => g.updated_at && new Date(g.updated_at).getFullYear() === new Date().getFullYear()).length;

  const cell = (num, label) => `
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 8px; padding: 16px; text-align: center;">
      <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${num}</div>
      <div style="font-size: 14px; color: #666; margin-top: 4px;">${label}</div>
    </div>`;

  return `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 32px;">
      ${cell(totalGames, '总游戏数')}
      ${cell(avgScore.toFixed(1), '平均评分')}
      ${cell(perfectGames, '神作 (9+)')}
      ${cell(thisYear, '今年游玩')}
    </div>
  `;
}

async function loadBangumiData() {
  const container = document.getElementById('bangumi-timeline');
  try {
    const response = await fetch(BANGUMI_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const games = await response.json();
    if (!Array.isArray(games) || games.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无游戏记录，请先运行 scripts/fetch_bangumi.py 抓取数据。</p>';
      return;
    }
    const visible = games.filter(g => !g.hidden);
    if (visible.length === 0) {
      container.innerHTML = '<p style="color: #666;">所有游戏记录已隐藏。</p>';
      return;
    }
    container.innerHTML = renderStats(visible) + visible.map(renderGameCard).join('');
  } catch (error) {
    console.error('加载 Bangumi 数据失败:', error);
    container.innerHTML = `
      <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;">
        <p style="color: #856404; font-weight: 500;">数据加载失败</p>
        <p style="color: #856404; font-size: 14px; margin-top: 8px;">请确认已运行脚本生成 static/data/bangumi.json，且已重新构建站点。</p>
        <p style="color: #856404; font-size: 12px; margin-top: 4px;">错误: ${error.message}</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', loadBangumiData);
</script>

<div id="bangumi-timeline">
  <p style="color: #666;">正在加载游戏记录...</p>
</div>
