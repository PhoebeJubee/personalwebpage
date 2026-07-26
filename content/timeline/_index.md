---
title: "游戏时光"
description: "从 Bangumi 同步的游戏记录和评分数据"
weight: 20
showDate: false
showReadingTime: false
---

这里展示我的游戏记录和评分数据。

<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/wordcloud@1.1.0/src/wordcloud2.js"></script>
<script>
const BANGUMI_DATA_URL = '../data/bangumi.json';

const PLATFORM_TAGS = new Set(['PC','PSP','STEAM','NDS','PS2','PS3','PS4','PSV','iOS','Android','Switch','NS','NS2','Xbox','Web','Mac','Linux','3DS','GBA','Wii','XBLA','网游','手游','网页游戏']);
const DIMENSION_MAP = {
  '悬疑推理': ['推理','悬疑','解谜','侦探','密室','文字冒险','视觉小说'],
  '视觉小说': ['Galgame','ADV','AVG','视觉小说','恋爱','全年龄','美少女','催泪','治愈'],
  '角色扮演': ['RPG','JRPG','回合制','MMORPG','ARPG','PRG'],
  '策略动作': ['SLG','SRPG','ACT','RTS','塔防','战棋','即时战略'],
  '恐怖猎奇': ['恐怖','猎奇','心理恐怖','血腥'],
  '独立游戏': ['独立游戏','Indie','像素','复古'],
  '国产游戏': ['国产','中文','国产galgame'],
  '手游休闲': ['手游','休闲','放置','卡牌','养成'],
};

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

function isMeaningfulTag(tag) {
  return !PLATFORM_TAGS.has(tag) && !/^\d{4}$/.test(tag) && tag !== '游戏' && tag.toLowerCase() !== 'galgame';
}

function computeTagFreq(games) {
  const freq = {};
  games.forEach(g => {
    (g.tags || []).forEach(t => {
      if (isMeaningfulTag(t)) freq[t] = (freq[t] || 0) + 1;
    });
  });
  return Object.entries(freq).sort((a, b) => b[1] - a[1]);
}

function computeRadarData(games) {
  const counts = {};
  Object.keys(DIMENSION_MAP).forEach(k => counts[k] = 0);
  games.forEach(g => {
    const tags = (g.tags || []).map(t => t.toLowerCase());
    Object.entries(DIMENSION_MAP).forEach(([dim, keywords]) => {
      if (keywords.some(kw => tags.includes(kw.toLowerCase()))) counts[dim]++;
    });
  });
  return counts;
}

function renderStats(games) {
  const rated = games.filter(g => g.rate > 0);
  const avgScore = rated.length ? rated.reduce((s, g) => s + g.rate, 0) / rated.length : 0;
  const perfectGames = rated.filter(g => g.rate >= 9).length;
  const thisYear = rated.filter(g => g.updated_at && new Date(g.updated_at).getFullYear() === new Date().getFullYear()).length;

  const cell = (num, label, color) => `
    <div style="background: linear-gradient(135deg, ${color[0]} 0%, ${color[1]} 100%); border-radius: 12px; padding: 20px 16px; text-align: center;">
      <div style="font-size: 36px; font-weight: bold; color: ${color[2]};">${num}</div>
      <div style="font-size: 13px; color: #666; margin-top: 4px;">${label}</div>
    </div>`;

  return `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; margin-bottom: 36px;">
      ${cell(rated.length, '已玩', ['#e3f2fd','#f3e5f5','#1976d2'])}
      ${cell(avgScore.toFixed(1), '平均评分', ['#e8f5e9','#f1f8e9','#2e7d32'])}
      ${cell(perfectGames, '神作 (9+)', ['#fce4ec','#f3e5f5','#c62828'])}
      ${cell(thisYear, '今年游玩', ['#fff3e0','#fbe9e7','#e65100'])}
    </div>`;
}

function renderWordCloud() {
  return `
    <div style="background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:16px;">
      <h3 style="font-size:16px;font-weight:700;margin-bottom:16px;color:#333;">🏷️ 标签词频</h3>
      <canvas id="wordcloud" width="700" height="500" style="width:100%;max-width:700px;display:block;margin:0 auto;"></canvas>
    </div>`;
}

const WC_DEFAULTS = { minCount: 2, maxTags: 80, canvasWidth: 700, canvasHeight: 500, fontSizeMin: 12, fontSizeMax: 54, rotateRatio: 0.4, blockedWords: [] };

function drawWordCloud(games) {
  const canvas = document.getElementById('wordcloud');
  if (!canvas || typeof WordCloud === 'undefined') return;

  fetch('../data/wordcloud-config.json?t=' + Date.now())
    .then(r => r.ok ? r.json() : WC_DEFAULTS)
    .catch(() => WC_DEFAULTS)
    .then(cfg => {
      const config = Object.assign({}, WC_DEFAULTS, cfg);
      const blocked = new Set((config.blockedWords || []).map(w => w.toLowerCase()));
      const freq = computeTagFreq(games).filter(([tag]) => !blocked.has(tag.toLowerCase()));
      if (!freq.length) return;
      const maxCount = freq[0][1];
      const isDark = document.documentElement.classList.contains('dark');

      canvas.width = config.canvasWidth;
      canvas.height = config.canvasHeight;
      canvas.style.width = '100%';

      const list = freq.slice(0, config.maxTags).map(([tag, count]) => {
        const ratio = count / maxCount;
        const size = Math.round(config.fontSizeMin + Math.log(1 + ratio * 20) * ((config.fontSizeMax - config.fontSizeMin) / 42 * 12));
        return [tag, Math.max(config.fontSizeMin, Math.min(config.fontSizeMax, size))];
      });

      const palette = isDark
        ? ['#90caf9','#80cbc4','#a5d6a7','#ffcc80','#ef9a9a','#b39ddb','#80deea','#fff59d','#f48fb1','#81d4fa']
        : ['#1565c0','#00695c','#2e7d32','#e65100','#c62828','#6a1b9a','#00838f','#f9a825','#ad1457','#1976d2'];

      WordCloud(canvas, {
        list: list,
        gridSize: 6,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif',
        fontWeight: '700',
        color: function() { return palette[Math.floor(Math.random() * palette.length)]; },
        backgroundColor: 'transparent',
        rotateRatio: config.rotateRatio,
        rotationSteps: 3,
        shuffle: true,
        drawOutOfBound: false,
        shrinkToFit: true,
        wait: 20,
      });
    });
}

function renderRadar(games) {
  return `
    <div style="background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:16px;">
      <h3 style="font-size:16px;font-weight:700;margin-bottom:16px;color:#333;">🎮 兴趣雷达</h3>
      <div style="position:relative;max-width:400px;margin:0 auto;">
        <canvas id="radarChart"></canvas>
      </div>
    </div>`;
}

function renderScoreDist() {
  return `
    <div style="background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:16px;">
      <h3 style="font-size:16px;font-weight:700;margin-bottom:16px;color:#333;">📊 评分分布</h3>
      <div style="position:relative;height:220px;">
        <canvas id="scoreChart"></canvas>
      </div>
    </div>`;
}

function renderSortBar(currentSort) {
  const btn = (key, label) => {
    const active = currentSort === key;
    return `<button onclick="sortGames('${key}')" style="padding:6px 16px;border-radius:6px;font-size:13px;font-weight:${active?600:400};cursor:pointer;transition:all 0.2s;border:1px solid ${active?'#1976d2':'#ddd'};background:${active?'#e3f2fd':'white'};color:${active?'#1976d2':'#666'};">${label}</button>`;
  };
  return `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
      <span style="font-size:13px;color:#999;">排序:</span>
      ${btn('score', '按评分 ↓')}
      ${btn('time', '按游玩时间 ↓')}
    </div>`;
}

function renderGameCard(item) {
  const name = item.name_cn || item.name || '';
  const orig = (item.name && item.name !== name) ? item.name : '';
  const score = item.rate || 0;
  const tags = (item.tags || []).slice(0, 5);
  const coverUrl = item.cover || '';
  const c = scoreColor(score);

  return `
    <div style="background:white;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08);padding:16px;margin-bottom:14px;display:flex;gap:16px;transition:transform 0.2s,box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'">
      ${coverUrl ? `<img src="${escapeHtml(coverUrl)}" alt="${escapeHtml(name)}" referrerpolicy="no-referrer" crossorigin="anonymous" style="width:96px;height:128px;object-fit:cover;border-radius:6px;flex-shrink:0;background:#f0f0f0;">` : ''}
      <div style="flex:1;min-width:0;">
        <div style="font-size:16px;font-weight:700;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(name)}</div>
        ${orig ? `<div style="font-size:12px;color:#888;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(orig)}</div>` : ''}
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:13px;color:#888;">
          ${item.date ? `<span>发售日: ${escapeHtml(item.date)}</span>` : ''}
          ${score > 0 ? `<span style="background:${c.bg};color:${c.fg};padding:2px 10px;border-radius:4px;font-weight:600;">${score}/10</span>` : ''}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;">
          ${tags.map(t => `<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;background:#e3f2fd;color:#1565c0;">${escapeHtml(t)}</span>`).join('')}
        </div>
      </div>
    </div>`;
}

function sortGames(key) {
  window._gameSort = key;
  const games = window._ratedGames;
  if (key === 'score') {
    games.sort((a, b) => b.rate - a.rate || (b.updated_at || '').localeCompare(a.updated_at || ''));
  } else {
    games.sort((a, b) => (b.updated_at || '').localeCompare(a.updated_at || '') || b.rate - a.rate);
  }
  const listEl = document.getElementById('game-list');
  listEl.innerHTML = renderSortBar(key) + games.map(renderGameCard).join('');
}

function initCharts(radarData, distData) {
  const isDark = document.documentElement.classList.contains('dark');
  const textColor = isDark ? '#aaa' : '#666';
  const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)';

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  const radarCanvas = document.getElementById('radarChart');
  if (radarCanvas) {
    new Chart(radarCanvas, {
      type: 'radar',
      data: {
        labels: Object.keys(radarData),
        datasets: [{
          label: '游戏数',
          data: Object.values(radarData),
          backgroundColor: 'rgba(25, 118, 210, 0.15)',
          borderColor: '#1976d2',
          borderWidth: 2,
          pointBackgroundColor: '#1976d2',
          pointRadius: 4,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          r: {
            beginAtZero: true,
            ticks: { stepSize: Math.max(1, Math.ceil(Math.max(...Object.values(radarData)) / 5)), font: { size: 11 } },
            grid: { color: gridColor },
            angleLines: { color: gridColor },
            pointLabels: { font: { size: 12 } },
          }
        }
      }
    });
  }

  const scoreCanvas = document.getElementById('scoreChart');
  if (scoreCanvas) {
    new Chart(scoreCanvas, {
      type: 'bar',
      data: {
        labels: distData.map((_, i) => i === 0 ? '' : i),
        datasets: [{
          data: distData,
          backgroundColor: distData.map((_, i) => {
            if (i === 0) return 'transparent';
            if (i >= 8) return '#4caf50';
            if (i >= 6) return '#ffc107';
            return '#f44336';
          }),
          borderRadius: 4,
          barPercentage: 0.7,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 12 } } },
          y: { beginAtZero: true, ticks: { stepSize: 10, font: { size: 11 } }, grid: { color: gridColor } },
        }
      }
    });
  }
}

async function loadBangumiData() {
  const container = document.getElementById('bangumi-timeline');
  try {
    const response = await fetch(BANGUMI_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const games = await response.json();
    if (!Array.isArray(games) || games.length === 0) {
      container.innerHTML = '<p style="color:#666;">暂无游戏记录，请先运行 scripts/fetch_bangumi.py 抓取数据。</p>';
      return;
    }
    const visible = games.filter(g => !g.hidden);
    if (visible.length === 0) {
      container.innerHTML = '<p style="color:#666;">所有游戏记录已隐藏。</p>';
      return;
    }

    const rated = visible.filter(g => g.rate > 0);
    window._ratedGames = rated;
    window._gameSort = 'score';

    rated.sort((a, b) => b.rate - a.rate || (b.updated_at || '').localeCompare(a.updated_at || ''));

    const dist = Array(11).fill(0);
    rated.forEach(g => dist[g.rate]++);
    const radarData = computeRadarData(rated);

    let html = '';
    html += renderStats(visible);
    html += renderWordCloud();
    html += renderRadar(rated);
    html += renderScoreDist();
    html += '<div id="game-list">';
    html += renderSortBar('score');
    html += rated.map(renderGameCard).join('');
    html += '</div>';

    container.innerHTML = html;

    requestAnimationFrame(() => {
      initCharts(radarData, dist);
      drawWordCloud(rated);
    });
  } catch (error) {
    console.error('加载 Bangumi 数据失败:', error);
    container.innerHTML = `
      <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:16px;">
        <p style="color:#856404;font-weight:500;">数据加载失败</p>
        <p style="color:#856404;font-size:14px;margin-top:8px;">请确认已运行脚本生成 static/data/bangumi.json</p>
        <p style="color:#856404;font-size:12px;margin-top:4px;">错误: ${error.message}</p>
      </div>`;
  }
}

document.addEventListener('DOMContentLoaded', loadBangumiData);
</script>

<div id="bangumi-timeline">
  <p style="color:#666;">正在加载游戏记录...</p>
</div>
