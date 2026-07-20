---
title: "游戏时光"
description: "从 Bangumi 同步的游戏记录和评分数据"
showDate: false
showReadingTime: false
---

这里展示我的游戏记录和评分数据。

<script>
// Bangumi 用户配置 - 请修改为你的 Bangumi UID
const BANGUMI_UID = 'YOUR_BANGUMI_UID';
const BANGUMI_API = `https://api.bgm.tv/v0/users/${BANGUMI_UID}/collections?subject_type=4&limit=30`;

function getScoreClass(score) {
  if (score >= 8) return 'score-high';
  if (score >= 6) return 'score-mid';
  return 'score-low';
}

function renderGameCard(item) {
  const subject = item.subject;
  const score = item.rate || 0;
  const tags = (subject.tags || []).slice(0, 5);
  const coverUrl = subject.images?.large || subject.images?.medium || '';
  
  return `
    <div style="background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 16px; margin-bottom: 16px; display: flex; gap: 16px;">
      ${coverUrl ? `<img src="${coverUrl}" alt="${subject.name_cn || subject.name}" style="width: 96px; height: 128px; object-fit: cover; border-radius: 4px;">` : ''}
      <div style="flex: 1;">
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">${subject.name_cn || subject.name}</div>
        ${subject.name && subject.name !== (subject.name_cn || subject.name) ? `<div style="font-size: 12px; color: #666; margin-bottom: 4px;">${subject.name}</div>` : ''}
        ${subject.date ? `<div style="font-size: 14px; color: #666; margin-bottom: 4px;">发售日: ${subject.date}</div>` : ''}
        ${score > 0 ? `<div style="margin-bottom: 8px;">我的评分: <span style="background: ${score >= 8 ? '#d4edda' : score >= 6 ? '#fff3cd' : '#f8d7da'}; color: ${score >= 8 ? '#155724' : score >= 6 ? '#856404' : '#721c24'}; padding: 2px 8px; border-radius: 4px; font-weight: 500;">${score}/10</span></div>` : ''}
        <div style="margin-top: 8px;">
          ${tags.map(t => `<span style="display: inline-block; padding: 2px 8px; margin: 2px 4px 2px 0; border-radius: 12px; font-size: 12px; background: #e3f2fd; color: #1565c0;">${t.name}</span>`).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderStats(games) {
  const totalGames = games.length;
  const avgScore = games.filter(g => g.rate > 0).reduce((sum, g) => sum + g.rate, 0) / games.filter(g => g.rate > 0).length || 0;
  const perfectGames = games.filter(g => g.rate >= 9).length;
  const thisYear = games.filter(g => g.updated_at && new Date(g.updated_at * 1000).getFullYear() === new Date().getFullYear()).length;
  
  return `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 32px;">
      <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 8px; padding: 16px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${totalGames}</div>
        <div style="font-size: 14px; color: #666; margin-top: 4px;">总游戏数</div>
      </div>
      <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 8px; padding: 16px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${avgScore.toFixed(1)}</div>
        <div style="font-size: 14px; color: #666; margin-top: 4px;">平均评分</div>
      </div>
      <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 8px; padding: 16px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${perfectGames}</div>
        <div style="font-size: 14px; color: #666; margin-top: 4px;">神作 (9+)</div>
      </div>
      <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 8px; padding: 16px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${thisYear}</div>
        <div style="font-size: 14px; color: #666; margin-top: 4px;">今年游玩</div>
      </div>
    </div>
  `;
}

async function loadBangumiData() {
  const container = document.getElementById('bangumi-timeline');
  
  try {
    const response = await fetch(BANGUMI_API, {
      headers: { 'User-Agent': 'PersonalSite/1.0' }
    });
    
    if (!response.ok) throw new Error('API 请求失败');
    
    const data = await response.json();
    const games = data.data || [];
    
    if (games.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无游戏记录</p>';
      return;
    }
    
    container.innerHTML = renderStats(games) + games.map(renderGameCard).join('');
  } catch (error) {
    console.error('加载 Bangumi 数据失败:', error);
    container.innerHTML = `
      <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;">
        <p style="color: #856404; font-weight: 500;">数据加载失败</p>
        <p style="color: #856404; font-size: 14px; margin-top: 8px;">请检查 Bangumi UID 配置或网络连接</p>
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
