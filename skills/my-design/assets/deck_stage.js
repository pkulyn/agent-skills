/**
 * DeckStage — HTML幻灯片引擎（单文件架构）
 * 固定画布 1920×1080 (16:9)
 *
 * 用法：在HTML末尾引入 <script src="deck_stage.js"></script>
 * 幻灯片用 <section class="slide" data-screen-label="01 Title"> 包裹
 */
(function () {
  const CANVAS_W = 1920;
  const CANVAS_H = 1080;
  const STORAGE_KEY = 'deck_stage_current';

  // ── 收集所有 slide ──
  const slides = document.querySelectorAll('section.slide');
  const total = slides.length;
  if (total === 0) return;

  // ── 读取持久化页码（1-indexed）──
  let current = 1;
  try {
    const saved = parseInt(localStorage.getItem(STORAGE_KEY), 10);
    if (saved >= 1 && saved <= total) current = saved;
  } catch (_) {}

  // ── 页码指示器 ──
  const indicator = document.createElement('div');
  indicator.id = 'deck-indicator';
  Object.assign(indicator.style, {
    position: 'fixed', bottom: '16px', right: '24px',
    fontSize: '14px', fontFamily: 'system-ui, sans-serif',
    color: 'rgba(255,255,255,0.6)', pointerEvents: 'none',
    zIndex: '9999', userSelect: 'none'
  });
  document.body.appendChild(indicator);

  // ── 自动缩放容器 ──
  const wrapper = document.createElement('div');
  wrapper.id = 'deck-wrapper';
  Object.assign(wrapper.style, {
    position: 'fixed', top: '0', left: '0',
    width: '100vw', height: '100vh',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    backgroundColor: '#000', overflow: 'hidden'
  });
  document.body.appendChild(wrapper);

  const viewport = document.createElement('div');
  viewport.id = 'deck-viewport';
  Object.assign(viewport.style, {
    width: CANVAS_W + 'px', height: CANVAS_H + 'px',
    transformOrigin: '0 0', position: 'relative', overflow: 'hidden'
  });
  wrapper.appendChild(viewport);

  // 把 slide 移入 viewport
  slides.forEach(s => viewport.appendChild(s));

  // ── 渲染当前帧 ──
  function render() {
    slides.forEach((s, i) => {
      s.style.display = (i + 1 === current) ? '' : 'none';
    });
    indicator.textContent = current + ' / ' + total;
    try { localStorage.setItem(STORAGE_KEY, current); } catch (_) {}
    scaleToFit();
  }

  // ── 缩放适配 ──
  function scaleToFit() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const scale = Math.min(vw / CANVAS_W, vh / CANVAS_H);
    viewport.style.transform = 'scale(' + scale + ')';
    // letterbox 居中偏移
    const rw = CANVAS_W * scale;
    const rh = CANVAS_H * scale;
    viewport.style.position = 'absolute';
    viewport.style.left = ((vw - rw) / 2) + 'px';
    viewport.style.top = ((vh - rh) / 2) + 'px';
  }

  // ── 导航 ──
  function go(n) {
    current = Math.max(1, Math.min(total, n));
    render();
  }

  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case ' ':
        e.preventDefault(); go(current + 1); break;
      case 'ArrowLeft': case 'ArrowUp':
        e.preventDefault(); go(current - 1); break;
      case 'Home': e.preventDefault(); go(1); break;
      case 'End': e.preventDefault(); go(total); break;
    }
  });

  // ── 触摸滑动 ──
  let touchX = 0;
  document.addEventListener('touchstart', function (e) { touchX = e.touches[0].clientX; }, { passive: true });
  document.addEventListener('touchend', function (e) {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) go(current + (dx < 0 ? 1 : -1));
  });

  // ── 窗口缩放 ──
  window.addEventListener('resize', scaleToFit);

  // ── Speaker Notes（可选）──
  // 按 S 键切换 speaker view，显示 <aside class="notes">
  let speakerView = false;
  const notesPanel = document.createElement('div');
  notesPanel.id = 'deck-speaker-notes';
  Object.assign(notesPanel.style, {
    position: 'fixed', bottom: '0', left: '0', width: '100vw',
    maxHeight: '30vh', overflow: 'auto', padding: '16px 24px',
    fontFamily: 'system-ui, sans-serif', fontSize: '16px',
    color: '#222', backgroundColor: '#f5f5f5', borderTop: '1px solid #ccc',
    display: 'none', zIndex: '10000', boxSizing: 'border-box'
  });
  document.body.appendChild(notesPanel);

  function updateNotes() {
    const activeSlide = slides[current - 1];
    const note = activeSlide ? activeSlide.querySelector('aside.notes') : null;
    notesPanel.innerHTML = note ? note.innerHTML : '<em>No notes</em>';
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 's' || e.key === 'S') {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      speakerView = !speakerView;
      notesPanel.style.display = speakerView ? '' : 'none';
      if (speakerView) updateNotes();
    }
  });

  const _origRender = render;
  // Override render to also update notes
  // (re-patch)
  const origGo = go;

  // ── 初始化 ──
  render();
})();
