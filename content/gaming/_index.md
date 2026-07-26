---
title: "游戏鉴赏"
description: "从 Bilibili 同步的游戏视频合集"
weight: 10
showDate: false
showReadingTime: false
---

这里展示我的游戏视频作品。

<script>
const BILIBILI_DATA_URL = '../data/bilibili.json';

function formatNumber(num) {
  num = Number(num) || 0;
  if (num >= 10000) return (num / 10000).toFixed(1) + '万';
  return num.toString();
}

function formatDuration(seconds) {
  seconds = Number(seconds) || 0;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

const DEFAULT_COVER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgwIiBoZWlnaHQ9IjI3MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZpbGw9IiM5OTkiIGZvbnQtc2l6ZT0iMjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7miZPnnIzlmag8L3RleHQ+PC9zdmc+';

let allVideos = [];
let currentSort = 'play';

function renderVideoCard(video) {
  const title = (video.title || '').replace(/<[^>]+>/g, '');
  let cover = video.pic || '';
  if (cover.startsWith('//')) cover = 'https:' + cover;
  cover = cover.replace(/@.*$/, '');
  const duration = formatDuration(video.duration);
  const playCount = formatNumber(video.play);
  const danmaku = formatNumber(video.video_review);
  const url = video.url || `https://www.bilibili.com/video/${video.bvid || ''}`;

  return `
    <a href="${escapeHtml(url)}" target="_blank" rel="noopener" style="text-decoration: none; color: inherit; display: block; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; overflow: hidden; transition: all 0.3s;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 24px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'">
      <div style="position: relative; width: 100%; aspect-ratio: 16/9; background: #f3f4f6; overflow: hidden;">
        <img 
          src="${escapeHtml(cover)}" 
          alt="${escapeHtml(title)}" 
          referrerpolicy="no-referrer"
          crossorigin="anonymous"
          style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s;" 
          loading="lazy"
          onerror="this.onerror=null;this.src='${DEFAULT_COVER}'"
          onmouseover="this.style.transform='scale(1.05)'"
          onmouseout="this.style.transform='scale(1)'"
        >
        <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.75); color: white; font-size: 12px; padding: 2px 8px; border-radius: 4px; backdrop-filter: blur(4px);">${duration}</div>
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 40px; background: linear-gradient(to bottom, rgba(0,0,0,0.3), transparent);"></div>
      </div>
      <div style="padding: 14px 16px;">
        <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #1f2937; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; line-height: 1.4;">${escapeHtml(title)}</div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #9ca3af;">
          <div style="display: flex; gap: 12px;">
            <span style="display: flex; align-items: center; gap: 3px;">
              <svg style="width: 14px; height: 14px;" fill="currentColor" viewBox="0 0 16 16"><path d="M8 3a5 5 0 100 10A5 5 0 008 3zM0 8a8 8 0 1116 0A8 8 0 010 8z"/><path d="M8 6.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/></svg>
              ${playCount}
            </span>
            <span style="display: flex; align-items: center; gap: 3px;">
              <svg style="width: 14px; height: 14px;" fill="currentColor" viewBox="0 0 16 16"><path d="M2.678 11.894a1 1 0 01.287.801 10.97 10.97 0 01-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 01.71-.074A8.06 8.06 0 008 14c3.996 0 7-2.807 7-6s-3.004-6-7-6-7 2.808-7 6c0 1.468.617 2.83 1.678 3.894z"/></svg>
              ${danmaku}
            </span>
          </div>
          <span style="color: #00a1d6; font-weight: 500; font-size: 12px;">Bilibili</span>
        </div>
      </div>
    </a>
  `;
}

function renderSortBar() {
  const bar = document.getElementById('sort-bar');
  if (!bar) return;
  bar.innerHTML = `
    <div style="display: flex; gap: 8px; margin-bottom: 20px;">
      <button id="sort-play" onclick="sortBy('play')" style="padding: 6px 16px; border-radius: 20px; border: 1px solid #e5e7eb; background: ${currentSort === 'play' ? '#6366f1' : 'white'}; color: ${currentSort === 'play' ? 'white' : '#374151'}; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s;">按播放量</button>
      <button id="sort-time" onclick="sortBy('created')" style="padding: 6px 16px; border-radius: 20px; border: 1px solid #e5e7eb; background: ${currentSort === 'created' ? '#6366f1' : 'white'}; color: ${currentSort === 'created' ? 'white' : '#374151'}; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s;">按更新时间</button>
    </div>
  `;
}

function sortBy(key) {
  currentSort = key;
  renderSortBar();
  renderVideos();
}

function renderVideos() {
  const container = document.getElementById('bilibili-videos');
  if (!allVideos.length) return;
  const sorted = [...allVideos].sort((a, b) => (b[currentSort] || 0) - (a[currentSort] || 0));
  container.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">
      ${sorted.map(renderVideoCard).join('')}
    </div>
  `;
}

async function loadBilibiliVideos() {
  const container = document.getElementById('bilibili-videos');
  try {
    const response = await fetch(BILIBILI_DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const videos = await response.json();
    if (!Array.isArray(videos) || videos.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无视频，请先运行 scripts/fetch_bilibili.py 抓取数据。</p>';
      return;
    }
    allVideos = videos.filter(v => !v.hidden);
    if (allVideos.length === 0) {
      container.innerHTML = '<p style="color: #666;">所有视频已隐藏。</p>';
      return;
    }
    renderSortBar();
    renderVideos();
  } catch (error) {
    console.error('加载 Bilibili 视频失败:', error);
    container.innerHTML = `
      <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;">
        <p style="color: #856404; font-weight: 500;">视频加载失败</p>
        <p style="color: #856404; font-size: 14px; margin-top: 8px;">请确认已运行脚本生成 static/data/bilibili.json</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', loadBilibiliVideos);
</script>

<div id="sort-bar"></div>
<div id="bilibili-videos">
  <p style="color: #666;">正在加载视频...</p>
</div>
