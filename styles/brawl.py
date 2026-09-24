# -*- coding: utf-8 -*-
"""Паспорт стиля «Brawl Stars»: яркие цвета, толстые чёрные контуры, крупные надписи.

Настроение как в игре, графика своя: фиолетовая арена с лучами, жёлтые и голубые
«кнопки-карточки» с жирной обводкой и жёсткой тенью, комикс-надписи.
Логотипы и персонажей игры не используем.
"""
import math

from styles.engine import render_deck


def _burst(points=16, outer=50.0, inner=41.0):
    """Многоугольник-«взрыв» для значка (проценты для clip-path)."""
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / points - math.pi / 2
        pts.append(f"{50 + r * math.cos(a):.1f}% {50 + r * math.sin(a):.1f}%")
    return ", ".join(pts)


BURST = _burst()

STAR = ('<svg class="st st1" viewBox="0 0 100 100"><path d="M50 5L62 37L96 39L70 60L79 94L50 75L21 94L30 60L4 39L38 37Z" '
        'fill="#ffd400" stroke="#000" stroke-width="7" stroke-linejoin="round"/><path d="M50 22L56 40L52 44" stroke="#fff6a8" stroke-width="5" fill="none" stroke-linecap="round"/></svg>')
BOLT = ('<svg class="st st2" viewBox="0 0 100 100"><path d="M58 4L22 54H46L38 96L80 40H54Z" fill="#25c6f5" stroke="#000" stroke-width="7" stroke-linejoin="round"/></svg>')
GEM = ('<svg class="st st3" viewBox="0 0 100 100"><path d="M50 6L88 34L50 94L12 34Z" fill="#ff3d81" stroke="#000" stroke-width="7" stroke-linejoin="round"/>'
       '<path d="M12 34H88M34 34L50 94L66 34M34 34L50 6L66 34" stroke="#000" stroke-width="4" fill="none" stroke-linejoin="round"/></svg>')

PASSPORT = {
    "id": "brawl",
    "name": "Brawl Stars",
    "vars": {
        "--page-bg": "linear-gradient(180deg, #4f2aa6 0%, #35197f 55%, #24115e 100%)",
        "--page-bg-solid": "#35197f",
        "--ink": "#ffffff", "--muted": "#d8c9ff", "--accent": "#ffd400", "--head": "#ffd400",
        "--card": "#ffffff", "--card-line": "#000000", "--card-shadow": "0 8px 0 #000",
        "--line": "#ffd400", "--radius": "16px",
        "--card-ink": "#111111", "--card-head": "#111111", "--card-muted": "#444444", "--on-accent": "#111111",
        "--font-head": "'Arial Black', 'Impact', 'Avenir Next Heavy', 'Helvetica Neue', sans-serif",
        "--font-body": "'Avenir Next', 'Helvetica Neue', Arial, sans-serif",
        "--t-in": "t-comic .5s ease-out both", "--t-in-back": "t-comic-back .5s ease-out both", "--more-fg": "#000",
        "--modal-bg": "#ffd400", "--modal-ink": "#111", "--modal-line": "#000", "--modal-shadow": "0 12px 0 #000",
    },
    "modal_tag": "Секретный факт!",
    "wow": {},
    "markers": "gem",
    "emblem_title": "🏆",
    "kicker_title": "Новая презентация",
    # цветные «кнопки» для карточек: (подпись, цвет, значок)
    "accents": [
        ("", "#ffd400", "💥"), ("", "#25c6f5", "⚡"), ("", "#7be23a", "💣"),
        ("", "#ff3d81", "🔥"), ("", "#ff9d2e", "🎯"), ("", "#9aa6ff", "🛡️"),
    ],
    "css": """
  .rays { position: fixed; z-index: 0; left: 50%; top: 50%; width: 220vmax; height: 220vmax; margin: -110vmax 0 0 -110vmax; pointer-events: none;
    background: repeating-conic-gradient(from 0deg, rgba(255,255,255,.07) 0 8deg, transparent 8deg 16deg); animation: spin 90s linear infinite; }
  .dotsbg { position: fixed; z-index: 0; inset: 0; pointer-events: none; opacity: .18;
    background: radial-gradient(#000 22%, transparent 24%) 0 0 / 16px 16px;
    -webkit-mask-image: linear-gradient(200deg, transparent 55%, #000); mask-image: linear-gradient(200deg, transparent 55%, #000); }
  .st { position: fixed; z-index: 1; pointer-events: none; }
  .st1 { width: clamp(48px, 8vw, 88px); left: 3vw; top: 7vh; animation: wiggle 3.6s ease-in-out infinite; }
  .st2 { width: clamp(44px, 7vw, 76px); right: 4vw; top: 12vh; animation: wiggle 4.2s ease-in-out -1s infinite; }
  .st3 { width: clamp(44px, 7vw, 76px); left: 5vw; bottom: 14vh; animation: wiggle 4.8s ease-in-out -2s infinite; }
  @keyframes wiggle { 0%, 100% { transform: rotate(-8deg) translateY(0); } 50% { transform: rotate(9deg) translateY(-14px); } }
  @keyframes spin { to { transform: rotate(360deg); } }

  h1, h2 { text-transform: uppercase; font-weight: 900; -webkit-text-stroke: 8px #000; paint-order: stroke fill; text-shadow: 0 7px 0 #000; letter-spacing: .01em; transform: skew(-4deg); }
  h1 { font-size: clamp(2.2rem, 7.6vmin, 5.1rem); } h2 { font-size: clamp(1.75rem, 5.2vmin, 3.3rem); }
  .kicker { padding: 7px 18px; background: #25c6f5; color: #000; border: 3px solid #000; box-shadow: 0 4px 0 #000; transform: skew(-8deg); letter-spacing: .14em; font-weight: 900; }
  .emblem { position: relative; isolation: isolate; width: clamp(96px, 17vmin, 150px); }
  .emblem::before { content: ''; position: absolute; inset: -7px; z-index: -2; background: #000; clip-path: polygon(__BURST__); }
  .emblem::after { content: ''; position: absolute; inset: 0; z-index: -1; background: #ffd400; clip-path: polygon(__BURST__); }
  .divider { font-size: 0; margin: 3.2vh 0; }
  .divider::before { content: ''; width: clamp(110px, 22vw, 200px); height: 14px; border: 3px solid #000; border-radius: 4px; opacity: 1;
    background: repeating-linear-gradient(-45deg, #ffd400 0 10px, #000 10px 20px); }
  .divider::after { display: none; }
  .sub { font-style: normal; font-weight: 800; color: #e6dcff; }
  .author { display: inline-block; padding: 9px 22px; background: #ffd400; color: #000; border: 4px solid #000; box-shadow: 0 5px 0 #000; border-radius: 12px; transform: skew(-6deg); letter-spacing: .06em; font-weight: 900; }

  .card, .side, .node { border: 4px solid #000; }
  .card { background: var(--el, #ffd400); border-color: #000; box-shadow: 0 9px 0 #000; }
  .card:nth-child(odd) { transform: rotate(-1.5deg); } .card:nth-child(even) { transform: rotate(1.5deg); }
  .card p { color: #111; font-weight: 800; }
  .gem { width: 3.1rem; height: 3.1rem; border: 4px solid #000; background: #fff; font-size: 1.5rem; box-shadow: 0 4px 0 #000; }
  .card small:empty { display: none; }
  .num { color: #000; }
  .step .dot { width: 3.1rem; height: 3.1rem; border: 4px solid #000; background: var(--el, #ffd400); font-size: 1.4rem; box-shadow: 0 4px 0 #000; color: #000; }
  .step::before { height: 8px; top: 1.2rem; background: #ffd400; border: 2px solid #000; border-radius: 4px; }
  .step { padding-top: 3.9rem; } .step b { color: #fff; font-weight: 900; text-transform: uppercase; } .step p { color: #d8c9ff; font-weight: 700; }
  .side:nth-child(1) { background: #25c6f5; } .side:nth-child(2) { background: #ff3d81; }
  .side { box-shadow: 0 9px 0 #000; } .side:nth-child(odd) { transform: rotate(-1deg); } .side:nth-child(even) { transform: rotate(1deg); }
  .side h3 { color: #fff; -webkit-text-stroke: 5px #000; paint-order: stroke fill; text-transform: uppercase; font-weight: 900; }
  .side li { color: #111; font-weight: 800; }
  .side li::before { content: '★'; color: #fff; -webkit-text-stroke: 1.5px #000; font-size: .95em; top: 0; }
  .bignum .value { color: #ffd400; -webkit-text-stroke: 10px #000; paint-order: stroke fill; text-shadow: 0 12px 0 #000; transform: skew(-5deg); }
  .bignum .caption { color: #fff; font-weight: 800; }
  .quote blockquote { position: relative; background: #fff; color: #111; border: 5px solid #000; border-radius: 26px; padding: 5vh 4vw 4vh; box-shadow: 0 10px 0 #000;
    font-style: normal; font-weight: 900; margin-bottom: 26px; }
  .quote blockquote::before { color: #ff3d81; }
  .quote blockquote::after { content: ''; position: absolute; bottom: -32px; left: 14%; border: 18px solid transparent; border-top: 30px solid #000; border-bottom: 0; }
  .quote cite { color: #ffd400; font-weight: 900; margin-top: 4vh; }
  .core { background: #ffd400; color: #111; border: 5px solid #000; border-radius: 14px; box-shadow: 0 8px 0 #000; font-weight: 900; text-transform: uppercase; transform: skew(-4deg); }
  .stem, .nodes::before, .node::before { background: #ffd400; }
  .node { color: #111; font-weight: 800; box-shadow: 0 7px 0 #000; }
  .node:nth-child(1) { background: #25c6f5; } .node:nth-child(2) { background: #ff3d81; } .node:nth-child(3) { background: #7be23a; } .node:nth-child(n+4) { background: #ff9d2e; }
  .demo { color: #cbb8ff; }
  #dots i { width: 18px; height: 12px; border: 3px solid #000; border-radius: 3px; background: #fff; transform: skew(-14deg); }
  #dots i.on { background: #ffd400; }
  .btns button { background: #ffd400; color: #000; border: 3px solid #000; box-shadow: 0 4px 0 #000; font-weight: 900; border-radius: 12px; }
  .pop { position: fixed; z-index: 9; pointer-events: none; font: 900 clamp(1.5rem, 4vmin, 2.4rem) var(--font-head); color: #ffd400; -webkit-text-stroke: 6px #000; paint-order: stroke fill;
    text-shadow: 0 4px 0 #000; animation: pop .8s ease-out forwards; }
  @keyframes pop { 0% { opacity: 1; transform: translate(-50%, -50%) scale(.3) rotate(var(--rot)); } 30% { transform: translate(-50%, -60%) scale(1.25) rotate(var(--rot)); } 100% { opacity: 0; transform: translate(-50%, -140%) scale(1) rotate(var(--rot)); } }
""".replace("__BURST__", BURST),
    "html": '<i class="rays"></i><i class="dotsbg"></i>' + STAR + BOLT + GEM,
    # нажал на экран — вылетает комикс-надпись
    "js": """
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const words = ['БАМ!', 'ВАУ!', 'КРУТО!', 'ТОП!', 'ЕСТЬ!', 'УРА!'];
  document.addEventListener('click', e => {
    if (e.target.closest('a, button, i')) return;
    const s = document.createElement('span');
    s.className = 'pop'; s.textContent = words[Math.floor(Math.random() * words.length)];
    s.style.left = e.clientX + 'px'; s.style.top = e.clientY + 'px';
    s.style.setProperty('--rot', (Math.random() * 24 - 12) + 'deg');
    document.body.appendChild(s); setTimeout(() => s.remove(), 850);
  });
})();
""",
}


def render(deck: dict) -> str:
    return render_deck(deck, PASSPORT)
