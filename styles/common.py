# -*- coding: utf-8 -*-
"""Общее для всех стилей: листание слайдов, всплывающие окна, конфетти, полный экран, автопоказ."""

# В странице должны быть секции .slide. Необязательно: #counter («2 / 5»), #dots (точки),
# #modal (окно с фактом), #play и #fs (кнопки автопоказа и полного экрана).
# Настройки праздника берутся из window.WOW (задаёт паспорт стиля).
NAV_JS = """
const slides = [...document.querySelectorAll('.slide')];
let cur = 0, timer = null;
const dotsBox = document.getElementById('dots'), modal = document.getElementById('modal');
const playBtn = document.getElementById('play'), fsBtn = document.getElementById('fs');
const notesBtn = document.getElementById('notesBtn');
if (notesBtn) notesBtn.onclick = () => { const n = document.getElementById('notes'); n.hidden = !n.hidden; };
if (dotsBox) slides.forEach((_, i) => { const d = document.createElement('i'); d.onclick = e => { e.stopPropagation(); show(i); }; dotsBox.appendChild(d); });

function show(i, quiet) {
  const next = Math.max(0, Math.min(slides.length - 1, i));
  if (next === cur && slides[cur].classList.contains('active')) return;
  document.body.classList.toggle('going-back', next < cur);
  slides[cur].classList.remove('active');
  cur = next;
  slides[cur].classList.add('active');
  const c = document.getElementById('counter');
  if (c) c.textContent = (cur + 1) + ' / ' + slides.length;
  if (dotsBox) [...dotsBox.children].forEach((d, k) => d.classList.toggle('on', k === cur));
  history.replaceState(null, '', '#' + (cur + 1));
  const nb = document.getElementById('notes');
  if (nb) nb.dataset.text = slides[cur].dataset.notes || '';
  if (nb) nb.textContent = nb.dataset.text || 'Для этого слайда шпаргалки нет.';
  if (cur === slides.length - 1) { stopPlay(); if (!quiet && slides.length > 2) celebrate(); }
  fit();
}
/* слайд не помещается в экран — чуть уменьшаем содержимое, чтобы ничего не пряталось за краем.
   На телефоне слайд, как и раньше, просто прокручивается (текст иначе стал бы мелким). */
function fit() {
  const sl = slides[cur], w = sl.querySelector('.wrap');
  if (!w) return;
  w.style.zoom = '';
  if (innerWidth <= 640) return;
  let z = 1;
  while (sl.scrollHeight > sl.clientHeight + 1 && z > 0.6) { z -= 0.03; w.style.zoom = z; }
}
addEventListener('resize', fit);
document.querySelectorAll('.slide img').forEach(im => im.addEventListener('load', fit));
function go(d) { show(cur + d); }

/* --- всплывающее окно с фактом --- */
function openModal(el) {
  if (!modal) return;
  modal.querySelector('.mtitle').textContent = el.dataset.title || '';
  modal.querySelector('.mtext').textContent = el.dataset.fact || '';
  modal.classList.add('open'); stopPlay();
}
function closeModal() { if (modal) modal.classList.remove('open'); }
const modalOpen = () => modal && modal.classList.contains('open');
const gameEl = document.getElementById('game');
const gameOpen = () => gameEl && gameEl.classList.contains('open');  // пока открыта игра, слайды не листаем

/* --- автопоказ и полный экран --- */
function stopPlay() { if (timer) { clearInterval(timer); timer = null; } if (playBtn) playBtn.textContent = '▶'; }
if (playBtn) playBtn.onclick = () => {
  if (timer) return stopPlay();
  if (cur >= slides.length - 1) show(0);
  playBtn.textContent = '⏸';
  timer = setInterval(() => { if (cur >= slides.length - 1) stopPlay(); else go(1); }, 6500);
};
if (fsBtn) {
  const de = document.documentElement;
  if (!(de.requestFullscreen || de.webkitRequestFullscreen)) fsBtn.style.display = 'none';
  fsBtn.onclick = () => {
    const on = document.fullscreenElement || document.webkitFullscreenElement;
    if (on) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    else (de.requestFullscreen || de.webkitRequestFullscreen).call(de);
  };
}

/* --- праздник на последнем слайде: конфетти или салют --- */
function celebrate() {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const W = window.WOW || {};
  if (!W.mode) return;
  const colors = W.colors || ['#1d4ed8', '#93a4d6', '#0f1b3d'], shapes = W.shapes || ['rect'], emoji = W.emoji || ['✨'];
  const cv = document.createElement('canvas');
  cv.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:25;pointer-events:none';
  document.body.appendChild(cv);
  const dpr = devicePixelRatio || 1, w = innerWidth, h = innerHeight;
  cv.width = w * dpr; cv.height = h * dpr;
  const cx = cv.getContext('2d'); cx.scale(dpr, dpr);
  const rnd = (a, b) => a + Math.random() * (b - a), pick = a => a[Math.floor(Math.random() * a.length)];
  let P = [];
  function confetti(n) {
    for (let k = 0; k < n; k++) P.push({ x: rnd(0, w), y: rnd(-h * .3, -10), vx: rnd(-1.4, 1.4), vy: rnd(1.5, 4.2), g: .04, rot: rnd(0, 6.28), vr: rnd(-.15, .15),
      s: rnd(9, 18), c: pick(colors), shape: pick(shapes), e: pick(emoji), a: 1, fade: 0 });
  }
  function burst(x, y) {
    for (let k = 0; k < 56; k++) { const an = rnd(0, 6.283), sp = rnd(1.2, 4.6);
      P.push({ x, y, vx: Math.cos(an) * sp, vy: Math.sin(an) * sp, g: .045, rot: 0, vr: 0, s: rnd(2.6, 5), c: pick(colors), shape: 'spark', a: 1, fade: rnd(.007, .013) }); }
  }
  if (W.mode === 'fireworks') [0, 350, 750, 1150, 1600].forEach(t => setTimeout(() => burst(rnd(w * .15, w * .85), rnd(h * .12, h * .5)), t));
  else confetti(W.count || 130);
  const t0 = performance.now();
  (function frame(t) {
    cx.clearRect(0, 0, w, h);
    P.forEach(p => {
      p.vy += p.g; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.a -= p.fade;
      if (p.a <= 0) return;
      cx.save(); cx.globalAlpha = Math.max(0, p.a); cx.translate(p.x, p.y); cx.rotate(p.rot); cx.fillStyle = p.c;
      if (p.shape === 'rect') cx.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2);
      else if (p.shape === 'emoji') { cx.font = (p.s * 1.7) + 'px serif'; cx.textAlign = 'center'; cx.textBaseline = 'middle'; cx.fillText(p.e, 0, 0); }
      else if (p.shape === 'star') { cx.beginPath(); for (let k = 0; k < 10; k++) { const r = k % 2 ? p.s * .45 : p.s; cx.lineTo(Math.cos(k * Math.PI / 5 - 1.57) * r, Math.sin(k * Math.PI / 5 - 1.57) * r); } cx.closePath(); cx.fill(); }
      else { cx.shadowColor = p.c; cx.shadowBlur = 14; cx.beginPath(); cx.arc(0, 0, p.s, 0, 6.283); cx.fill(); }
      cx.restore();
    });
    P = P.filter(p => p.a > 0 && p.y < h + 40);
    if ((P.length || t - t0 < 2000) && t - t0 < 6500) requestAnimationFrame(frame); else cv.remove();
  })(t0);
}

/* --- управление --- */
document.addEventListener('keydown', e => {
  if (gameOpen()) return;
  if (modalOpen()) { if (e.key === 'Escape') closeModal(); return; }
  const f = e.target.closest && e.target.closest('[data-fact]');
  if (f && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); openModal(f); return; }
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') go(1);
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') go(-1);
});
document.addEventListener('click', e => {
  if (gameOpen()) return;
  if (modalOpen()) { if (!e.target.closest('.mbox') || e.target.closest('.mx')) closeModal(); return; }
  const f = e.target.closest('[data-fact]');
  if (f) { openModal(f); return; }
  if (e.target.closest('a, button, i, #notes')) return;
  go(e.clientX < innerWidth * 0.33 ? -1 : 1);
});
let sx = null;
document.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
document.addEventListener('touchend', e => {
  if (sx === null || modalOpen() || gameOpen()) { sx = null; return; }
  const dx = e.changedTouches[0].clientX - sx; sx = null;
  if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
}, { passive: true });
const fromHash = () => Math.max(0, (parseInt(location.hash.slice(1), 10) || 1) - 1);
window.addEventListener('hashchange', () => show(fromHash(), true));
show(fromHash(), true);
"""
