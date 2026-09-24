# -*- coding: utf-8 -*-
"""Паспорт стиля «Harry Potter»: старый пергамент, тиснёное золото, свет свечи.

Пришёл на замену «Toca Boca» (Анна и дочки решили 22.09.2026: прежний стиль
выглядел слишком по-детски — сердечки, звёздочки, конфетти). Настроение —
старая книга заклинаний: бумага с потёртостями, тёмные чернила, сургучная
печать, тонкая золотая рамка, медленно плывущие искры-светлячки вместо
хлопьев конфетти. Ничего из фирменной графики фильмов/игры не копируем —
только настроение и оттенки.
"""
from styles.engine import render_deck

CORNER = ('<svg class="{pos}" viewBox="0 0 64 64"><path d="M4 60V18Q4 4 18 4H60M16 60V26Q16 16 26 16H60"/>'
          '<circle cx="24" cy="24" r="2.6" fill="#c9a227"/></svg>')

PASSPORT = {
    "id": "harry",
    "name": "Harry Potter",
    "vars": {
        "--page-bg": ("radial-gradient(ellipse at 18% 12%, rgba(255,248,225,.55), transparent 42%), "
                      "radial-gradient(ellipse at center, transparent 52%, rgba(55,34,14,.28) 100%), "
                      "radial-gradient(circle at 1px 1px, rgba(110,80,35,.14) 1px, transparent 1.6px) 0 0 / 24px 24px, "
                      "linear-gradient(155deg, #f1e4c3 0%, #e7d3a0 45%, #d9bf88 100%)"),
        "--page-bg-solid": "#e7d3a0",
        "--ink": "#2e2010", "--muted": "#7a6244", "--accent": "#9c6b1f", "--head": "#241608",
        "--card": "#f7eed6", "--card-line": "#c9a668", "--card-shadow": "0 3px 0 #c9a668, 0 12px 24px rgba(60,40,10,.16)",
        "--line": "#c9a668", "--radius": "4px",
        "--font-head": "Herculanum, Copperplate, 'Big Caslon', Didot, Georgia, serif",
        "--font-body": "'Iowan Old Style', Palatino, Georgia, 'Times New Roman', serif",
        "--t-in": "t-glow .7s ease both", "--more-fg": "#2e2010",
        "--modal-bg": "#f7eed6", "--modal-ink": "#2e2010", "--modal-line": "#9c6b1f", "--modal-shadow": "0 0 46px rgba(156,107,31,.35)",
    },
    "modal_tag": "Секрет свитка",
    "wow": {},
    "markers": "number",
    "emblem_title": "❧",
    "kicker_title": "Свиток",
    "css": """
  #embers { position: fixed; inset: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
  .frame { position: fixed; inset: max(12px, 2.2vmin); z-index: 1; pointer-events: none;
    border: 1px solid rgba(156,107,31,.45); box-shadow: inset 0 0 34px rgba(120,80,20,.12); }
  .frame svg { position: absolute; width: 56px; height: 56px; fill: none; stroke: #9c6b1f; stroke-width: 1.6; opacity: .8; }
  .frame .tl { top: -5px; left: -5px; } .frame .tr { top: -5px; right: -5px; transform: scaleX(-1); }
  .frame .bl { bottom: -5px; left: -5px; transform: scaleY(-1); } .frame .br { bottom: -5px; right: -5px; transform: scale(-1, -1); }

  h1, h2 { text-shadow: 0 1px 0 rgba(255,255,255,.4); }
  .kicker { font-family: var(--font-head); text-transform: none; letter-spacing: .3em; }
  .emblem { position: relative; isolation: isolate; color: #f4e4c1; }
  .emblem::before { content: ''; position: absolute; inset: 3%; z-index: -1; border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #9c2a3a, #611722 72%); border: 3px solid #c9a227;
    box-shadow: 0 6px 16px rgba(50,15,10,.4), inset 0 0 14px rgba(0,0,0,.35); }

  .card, .side, .node { position: relative; background: linear-gradient(160deg, var(--card), #efdfb4 130%); }
  .card::after, .side::after { content: ''; position: absolute; top: 0; right: 0; width: 16px; height: 16px;
    background: linear-gradient(135deg, transparent 50%, rgba(120,90,40,.4) 50%); }
  .num { font: 700 1.3rem/1 var(--font-head); color: var(--accent); letter-spacing: .04em; }
  .card p { color: #3a2a14; }

  .step .dot { background: #611722; border-color: var(--accent); color: #f4e4c1; font-family: var(--font-head); }
  .step::before { background: var(--line); opacity: .7; }

  .core { background: linear-gradient(160deg, #611722, #480f18); color: #f4e4c1; border: 2px solid var(--accent);
    box-shadow: 0 8px 20px rgba(50,15,10,.3); }
  .stem, .nodes::before, .node::before { background: var(--line); }

  .bignum .value { text-shadow: 0 2px 0 rgba(255,255,255,.35); }
  .quote blockquote { background: var(--card); border: 1px solid var(--card-line); border-radius: 3px;
    padding: 5vh 4vw 4vh; box-shadow: var(--card-shadow); }
  .quote cite { font-family: var(--font-head); letter-spacing: .16em; }

  .demo { color: var(--muted); }
  #dots i.on { box-shadow: 0 0 8px rgba(156,107,31,.5); }
  .btns button { font-family: var(--font-head); letter-spacing: .04em; }
""",
    "html": '<canvas id="embers"></canvas><div class="frame">' + "".join(CORNER.format(pos=p) for p in ("tl", "tr", "bl", "br")) + "</div>",
    # медленные искры-светлячки плывут вверх, как пыль в свете свечи
    "js": """
(function () {
  const cv = document.getElementById('embers'), cx = cv.getContext('2d');
  let W, H, motes = [];
  function resize() {
    const r = devicePixelRatio || 1; W = innerWidth; H = innerHeight;
    cv.width = W * r; cv.height = H * r; cx.setTransform(r, 0, 0, r, 0, 0);
    motes = Array.from({ length: Math.round(W * H / 30000) }, () => ({
      x: Math.random() * W, y: Math.random() * H + H, r: Math.random() * 1.5 + .6,
      vy: Math.random() * .3 + .1, vx: (Math.random() - .5) * .15, p: Math.random() * 6.28, s: Math.random() * .02 + .01 }));
  }
  addEventListener('resize', resize); resize();
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) return;
  (function tick() {
    cx.clearRect(0, 0, W, H);
    for (const m of motes) {
      m.y -= m.vy; m.x += m.vx; m.p += m.s;
      if (m.y < -10) { m.y = H + 10; m.x = Math.random() * W; }
      cx.globalAlpha = .2 + .5 * Math.abs(Math.sin(m.p));
      cx.fillStyle = '#c9a227'; cx.shadowColor = '#e8c26a'; cx.shadowBlur = 6;
      cx.beginPath(); cx.arc(m.x, m.y, m.r, 0, 6.283); cx.fill();
    }
    requestAnimationFrame(tick);
  })();
})();
""",
}


def render(deck: dict) -> str:
    return render_deck(deck, PASSPORT)
