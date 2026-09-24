# -*- coding: utf-8 -*-
"""Паспорт стиля «Genshin Impact»: ночное небо, золотая рамка, значки стихий.

Настроение как в игре, графика своя: звёзды на canvas, золотые уголки,
карточки с цветом стихии. Логотипы и персонажей игры не используем.
"""
from styles.engine import render_deck

CORNER = ('<svg class="{pos}" viewBox="0 0 64 64"><path d="M4 60V18Q4 4 18 4H60M16 60V26Q16 16 26 16H60"/>'
          '<path d="M4 4l10 10"/><circle cx="24" cy="24" r="3" fill="#e8c26a"/></svg>')

PASSPORT = {
    "id": "genshin",
    "name": "Genshin Impact",
    "vars": {
        "--page-bg": ("radial-gradient(ellipse at 80% 8%, #3a3f8f 0, transparent 45%), "
                      "linear-gradient(180deg, #070b26 0%, #141b4d 55%, #3a2a63 100%)"),
        "--page-bg-solid": "#141b4d",
        "--ink": "#f4efe2", "--muted": "#b7b3d6", "--accent": "#e8c26a", "--head": "#e8c26a",
        "--card": "rgba(255,255,255,.07)", "--card-line": "rgba(232,194,106,.35)",
        "--card-shadow": "0 10px 34px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.08)",
        "--line": "rgba(232,194,106,.5)", "--radius": "10px",
        "--t-in": "t-glow .7s ease both", "--more-fg": "#141b4d",
        "--modal-bg": "#171f5c", "--modal-ink": "#f4efe2", "--modal-line": "#e8c26a", "--modal-shadow": "0 0 50px rgba(232,194,106,.35)",
    },
    "modal_tag": "Знание",
    "wow": {},
    "markers": "gem",
    "emblem_title": "✦",
    "kicker_title": "Презентация",
    # значки стихий по кругу: (название, цвет, значок)
    "accents": [
        ("Пиро", "#ff7a45", "🔥"), ("Гидро", "#4fb3ff", "💧"), ("Анемо", "#5eead4", "🌀"),
        ("Электро", "#b78bff", "⚡"), ("Дендро", "#8bd450", "🌿"), ("Крио", "#a5e8ff", "❄️"),
        ("Гео", "#f0c44c", "🪨"),
    ],
    "css": """
  #sky { position: fixed; inset: 0; width: 100%; height: 100%; z-index: 0; }
  .frame { position: fixed; inset: max(12px, 2.4vmin); z-index: 1; pointer-events: none;
    border: 1.5px solid rgba(232,194,106,.55); border-radius: 6px; box-shadow: inset 0 0 40px rgba(232,194,106,.08); }
  .frame svg { position: absolute; width: 64px; height: 64px; fill: none; stroke: #e8c26a; stroke-width: 2; }
  .frame .tl { top: -6px; left: -6px; } .frame .tr { top: -6px; right: -6px; transform: scaleX(-1); }
  .frame .bl { bottom: -6px; left: -6px; transform: scaleY(-1); } .frame .br { bottom: -6px; right: -6px; transform: scale(-1, -1); }
  h2 { background: linear-gradient(180deg, #fff0b8, #e8c26a 70%, #b98a34); -webkit-background-clip: text; background-clip: text;
    color: transparent; filter: drop-shadow(0 2px 14px rgba(232,194,106,.35)); }
  h1 { color: transparent; filter: drop-shadow(0 2px 14px rgba(232,194,106,.35)); }
  h1 .l { background: linear-gradient(180deg, #fff0b8, #e8c26a 70%, #b98a34); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .bignum .value { text-shadow: 0 0 40px rgba(232,194,106,.5); }
  .emblem { position: relative; }
  .emblem::before { content: ''; position: absolute; inset: 12%; transform: rotate(45deg); border: 2px solid #e8c26a;
    background: rgba(232,194,106,.1); box-shadow: 0 0 30px rgba(232,194,106,.45); }
  .emblem::after { content: ''; position: absolute; inset: 0; transform: rotate(45deg) scale(.86); border: 1px solid rgba(232,194,106,.5); }
  .card::before { content: ''; position: absolute; left: 14px; right: 14px; top: 0; height: 3px; border-radius: 0 0 4px 4px;
    background: var(--el, #e8c26a); box-shadow: 0 0 16px var(--el, #e8c26a); }
  .gem { box-shadow: 0 0 18px color-mix(in srgb, var(--el, #e8c26a) 55%, transparent); }
  .num { color: #e8c26a; }
  .quote blockquote { color: #fff0b8; }
  #dots i { border-radius: 0; transform: rotate(45deg); }
  #dots i.on { box-shadow: 0 0 12px #e8c26a; }
  .hud { left: max(84px, 9vmin); right: max(84px, 9vmin); bottom: 26px; }
  .demo { bottom: 74px; }
  .btns button { background: rgba(232,194,106,.1); color: #fff0b8; border-color: rgba(232,194,106,.5); }
""",
    "html": ('<canvas id="sky"></canvas><div class="frame">'
             + "".join(CORNER.format(pos=p) for p in ("tl", "tr", "bl", "br")) + "</div>"),
    "js": """
(function () {
  const cv = document.getElementById('sky'), cx = cv.getContext('2d');
  let W, H, stars = [], shoot = null;
  function resize() {
    const r = devicePixelRatio || 1; W = innerWidth; H = innerHeight;
    cv.width = W * r; cv.height = H * r; cx.setTransform(r, 0, 0, r, 0, 0);
    stars = Array.from({ length: Math.round(W * H / 9000) }, () => ({
      x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.4 + .3,
      p: Math.random() * 6.28, s: Math.random() * .02 + .008 }));
  }
  addEventListener('resize', resize); resize();
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function tick() {
    cx.clearRect(0, 0, W, H);
    for (const s of stars) {
      s.p += s.s;
      cx.globalAlpha = .35 + .65 * Math.abs(Math.sin(s.p));
      cx.fillStyle = '#fff6d6'; cx.beginPath(); cx.arc(s.x, s.y, s.r, 0, 6.283); cx.fill();
    }
    if (!shoot && !still && Math.random() < .004) shoot = { x: Math.random() * W * .7 + W * .3, y: Math.random() * H * .35, l: 0 };
    if (shoot) {
      shoot.x -= 9; shoot.y += 4.5; shoot.l += 1;
      const g = cx.createLinearGradient(shoot.x, shoot.y, shoot.x + 90, shoot.y - 45);
      g.addColorStop(0, 'rgba(255,240,184,.95)'); g.addColorStop(1, 'rgba(255,240,184,0)');
      cx.globalAlpha = 1; cx.strokeStyle = g; cx.lineWidth = 2; cx.beginPath();
      cx.moveTo(shoot.x, shoot.y); cx.lineTo(shoot.x + 90, shoot.y - 45); cx.stroke();
      if (shoot.l > 60) shoot = null;
    }
    if (!still) requestAnimationFrame(tick);
  }
  tick();
})();
""",
}


def render(deck: dict) -> str:
    return render_deck(deck, PASSPORT)
