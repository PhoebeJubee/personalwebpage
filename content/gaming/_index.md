---
title: "游戏鉴赏"
description: "从 Bilibili 同步的游戏视频合集"
showDate: false
showReadingTime: false
---

这里展示我的游戏视频作品。

<script>
const BILIBILI_UID = 'YOUR_BILIBILI_UID';
const BILIBILI_API = `https://api.bilibili.com/x/space/wbi/arc/search?mid=${BILIBILI_UID}&ps=12&tid=0&pn=1&order=pubdate`;

function formatNumber(num) {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万';
  return num.toString();
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function renderVideoCard(video) {
  const bvid = video.bvid;
  const title = video.title.replace(/<[^>]+>/g, '');
  const cover = video.pic;
  const duration = formatDuration(video.duration);
  const playCount = formatNumber(video.play);
  const danmaku = formatNumber(video.video_review);
  const url = `https://www.bilibili.com/video/${bvid}`;
  
  return `
    <a href="${url}" target="_blank" rel="noopener" style="text-decoration: none; color: inherit; display: block; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; transition: all 0.3s; margin-bottom: 16px;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 4px 16px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">
      <div style="position: relative; width: 100%; aspect-ratio: 16/9; background: #f0f0f0; overflow: hidden;">
        <img src="${cover}@480w_270h_1c.webp" alt="${title}" style="width: 100%; height: 100%; object-fit: cover;" loading="lazy">
        <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; padding: 2px 8px; border-radius: 4px;">${duration}</div>
      </div>
      <div style="padding: 16px;">
        <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${title}</div>
        <div style="display: flex; justify-content: space-between; font-size: 14px; color: #666;">
          <div style="display: flex; gap: 12px;">
            <span>👁 ${playCount}</span>
            <span>💬 ${danmaku}</span>
          </div>
        </div>
      </div>
    </a>
  `;
}

async function loadBilibiliVideos() {
  const container = document.getElementById('bilibili-videos');
  
  try {
    const proxyUrl = 'https://api.allorigins.win/raw?url=';
    const response = await fetch(proxyUrl + encodeURIComponent(BILIBILI_API));
    
    if (!response.ok) throw new Error('API 请求失败');
    
    const data = await response.json();
    const videos = data.data?.list?.vlist || [];
    
    if (videos.length === 0) {
      container.innerHTML = '<p style="color: #666;">暂无视频</p>';
      return;
    }
    
    container.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">
        ${videos.map(renderVideoCard).join('')}
      </div>
    `;
  } catch (error) {
    console.error('加载 Bilibili 视频失败:', error);
    container.innerHTML = `
      <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px;">
        <p style="color: #856404; font-weight: 500;">视频加载失败</p>
        <p style="color: #856404; font-size: 14px; margin-top: 8px;">请检查 Bilibili UID 配置或网络连接</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', loadBilibiliVideos);
</script>

<div id="bilibili-videos">
  <p style="color: #666;">正在加载视频...</p>
</div>
