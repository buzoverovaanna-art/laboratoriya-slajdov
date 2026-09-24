# -*- coding: utf-8 -*-
"""Паспорт стиля «Toca Boca»: уют, пастель, круглые формы и стикеры.

Настроение как в игре, графика своя: пастельные пятна, «стикеры» с мордочками
(звезда, облако, сердце, цветок), карточки с толстой рамкой и «объёмной» тенью.
Логотипы и персонажей игры не используем.
"""
from styles.engine import render_deck

STAR = ('<svg class="st st1" viewBox="0 0 100 100"><path d="M50 6L61 38L95 38L67 58L78 92L50 71L22 92L33 58L5 38L39 38Z" '
        'fill="#ffd75e" stroke="#f2b705" stroke-width="4" stroke-linejoin="round"/><circle cx="42" cy="52" r="3.4" fill="#5b3f8f"/>'
        '<circle cx="58" cy="52" r="3.4" fill="#5b3f8f"/><path d="M42 61Q50 69 58 61" stroke="#5b3f8f" stroke-width="3" fill="none" stroke-linecap="round"/>'
        '<circle cx="36" cy="60" r="4" fill="#ff9fbd" opacity=".7"/><circle cx="64" cy="60" r="4" fill="#ff9fbd" opacity=".7"/></svg>')
HEART = ('<svg class="st st2" viewBox="0 0 100 100"><path d="M50 90C8 62 4 30 27 18C40 12 50 22 50 31C50 22 60 12 73 18C96 30 92 62 50 90Z" '
         'fill="#ff8fb8" stroke="#f0609a" stroke-width="4" stroke-linejoin="round"/><path d="M30 30Q26 36 30 43" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/></svg>')
CLOUD = ('<svg class="st st3" viewBox="0 0 120 80"><path d="M28 68C10 68 6 46 22 40C20 24 40 16 52 28C60 12 88 16 90 36C108 34 114 62 96 68Z" '
         'fill="#fff" stroke="#bfe0ff" stroke-width="4" stroke-linejoin="round"/><circle cx="46" cy="48" r="3.2" fill="#5b3f8f"/><circle cx="64" cy="48" r="3.2" fill="#5b3f8f"/>'
         '<path d="M50 56Q55 62 60 56" stroke="#5b3f8f" stroke-width="3" fill="none" stroke-linecap="round"/></svg>')
FLOWER = ('<svg class="st st4" viewBox="0 0 100 100"><g fill="#ffb3d1" stroke="#f58cb8" stroke-width="3"><circle cx="50" cy="20" r="16"/><circle cx="80" cy="42" r="16"/>'
          '<circle cx="68" cy="76" r="16"/><circle cx="32" cy="76" r="16"/><circle cx="20" cy="42" r="16"/></g><circle cx="50" cy="52" r="14" fill="#ffd75e" stroke="#f2b705" stroke-width="3"/></svg>')

PASSPORT = {
    "id": "toca",
    "name": "Toca Boca",
    "vars": {
        "--page-bg": "radial-gradient(circle at 1px 1px, rgba(255,160,200,.35) 2px, transparent 2.5px) 0 0 / 34px 34px, linear-gradient(160deg, #fff4f9, #eaf7ff 60%, #f1ecff)",
        "--page-bg-solid": "#fff4f9",
        "--ink": "#4b3a66", "--muted": "#8a7aa6", "--accent": "#ff6f9f", "--head": "#5b3f8f",
        "--card": "#ffffff", "--card-line": "#ffd0e2", "--card-shadow": "0 8px 0 #ffd0e2",
        "--line": "#ffb3d1", "--radius": "30px",
        "--font-head": "'Marker Felt', 'Chalkboard SE', 'Avenir Next Rounded', 'Trebuchet MS', sans-serif",
        "--font-body": "'Avenir Next Rounded', 'Avenir Next', 'Trebuchet MS', sans-serif",
        "--t-in": "t-pop .6s ease both",
        "--modal-bg": "#ffffff", "--modal-ink": "#4b3a66", "--modal-line": "#ff8fb8", "--modal-shadow": "0 12px 0 #ffd0e2",
    },
    "modal_tag": "Интересный факт ✨",
    "wow": {"mode": "confetti", "shapes": ["emoji"], "emoji": ["💖", "⭐", "🌸", "✨", "🦋", "🌈"], "count": 70},
    "markers": "gem",
    "emblem_title": "🌈",
    "kicker_title": "Моя презентация",
    # цветные «стикеры» для карточек: (подпись, цвет, значок)
    "accents": [
        ("", "#ff8fb8", "💖"), ("", "#5ecfae", "🌼"), ("", "#ffc94d", "⭐"),
        ("", "#6cb8ff", "☁️"), ("", "#a78bfa", "🦋"), ("", "#ff9f7a", "🍑"),
    ],
    "css": """
  .st { position: fixed; z-index: 1; pointer-events: none; filter: drop-shadow(0 6px 0 rgba(255,160,200,.35)); }
  .st1 { width: clamp(50px, 8vw, 90px); left: 3vw; top: 6vh; animation: float 6s ease-in-out infinite; }
  .st2 { width: clamp(44px, 7vw, 76px); right: 4vw; top: 10vh; animation: float 7s ease-in-out -2s infinite; }
  .st3 { width: clamp(70px, 11vw, 130px); left: 5vw; bottom: 12vh; animation: drift 14s ease-in-out infinite; }
  .st4 { width: clamp(50px, 8vw, 88px); right: 5vw; bottom: 14vh; animation: spin 24s linear infinite; }
  @keyframes float { 50% { transform: translateY(-16px) rotate(6deg); } }
  @keyframes drift { 50% { transform: translateX(26px); } }
  @keyframes spin { to { transform: rotate(360deg); } }
  .blob { position: fixed; z-index: 0; pointer-events: none; border-radius: 62% 38% 55% 45% / 48% 58% 42% 52%; animation: morph 16s ease-in-out infinite; }
  .blob.b1 { width: 46vmax; height: 40vmax; left: -14vmax; bottom: -16vmax; background: #d5f5e8; }
  .blob.b2 { width: 40vmax; height: 34vmax; right: -12vmax; top: -12vmax; background: #e6defc; animation-delay: -6s; }
  @keyframes morph { 50% { border-radius: 40% 60% 42% 58% / 58% 40% 60% 42%; transform: rotate(8deg) scale(1.05); } }

  h1, h2 { color: #5b3f8f; text-shadow: 3px 3px 0 #ffd0e2; }
  .kicker { padding: 6px 16px; border-radius: 999px; background: #fff; border: 3px solid #ffd0e2; color: #ff6f9f; letter-spacing: .12em; font-weight: 800; }
  .emblem { position: relative; isolation: isolate; }
  .emblem::before { content: ''; position: absolute; inset: 4%; z-index: -1; border-radius: 50%; background: #fff; border: 4px solid #ffb3d1; box-shadow: 0 8px 0 #ffd0e2; }
  .divider { font-size: 0; margin: 3vh 0; }
  .divider::before { content: ''; width: 14px; height: 14px; margin-right: 50px; border-radius: 50%; background: #ff8fb8; opacity: 1;
    box-shadow: 26px 0 0 #ffc94d, 52px 0 0 #5ecfae; }
  .divider::after { display: none; }
  .sub { font-style: normal; font-weight: 700; color: #8a7aa6; }
  .author { display: inline-block; padding: 8px 20px; border-radius: 999px; background: #fff; border: 3px solid #ffd0e2; box-shadow: 0 5px 0 #ffd0e2; color: #5b3f8f; letter-spacing: .04em; }

  .card, .side, .node { border-width: 3px; }
  .card:nth-child(odd), .side:nth-child(odd) { transform: rotate(-1.2deg); }
  .card:nth-child(even), .side:nth-child(even) { transform: rotate(1.2deg); }
  .card { box-shadow: 0 8px 0 var(--el, #ffd0e2); border-color: var(--el, #ffd0e2); }
  .gem { width: 3rem; height: 3rem; border: 0; background: var(--el, #ffb3d1); font-size: 1.5rem; box-shadow: 0 4px 0 rgba(0,0,0,.12); }
  .card small:empty { display: none; }
  .num { color: #ff6f9f; font-size: .9rem; }
  .step .dot { width: 2.9rem; height: 2.9rem; border: 0; background: var(--el, #ff8fb8); font-size: 1.4rem; box-shadow: 0 4px 0 rgba(0,0,0,.12); }
  .step::before { height: 0; background: none; border-top: 3px dashed #ffb3d1; top: 1.4rem; }
  .step { padding-top: 3.8rem; }
  .side { box-shadow: 0 8px 0 var(--el, #ffd0e2); border-color: var(--el, #ffd0e2); }
  .side li::before { content: '♥'; font-size: .8em; top: .05em; }
  .bignum .value { color: #ff6f9f; text-shadow: 5px 5px 0 #ffd0e2; }
  .quote blockquote { background: #fff; border: 3px solid #ffd0e2; border-radius: 36px; padding: 5vh 4vw 4vh; box-shadow: 0 10px 0 #ffd0e2; color: #5b3f8f; }
  .quote blockquote::before { color: #ff8fb8; }
  .quote cite { color: #8a7aa6; font-weight: 800; }
  .core { background: #ff8fb8; color: #fff; border: 0; border-radius: 999px; box-shadow: 0 8px 0 #ee6f9d; padding: 1.8vh 3vw; text-shadow: 2px 2px 0 rgba(0,0,0,.12); }
  .stem { background: #ffb3d1; } .nodes::before { background: #ffb3d1; } .node::before { background: #ffb3d1; }
  .node { font-weight: 700; }
  .node:nth-child(1) { background: #fff0f6; border-color: #ffb3d1; box-shadow: 0 6px 0 #ffb3d1; }
  .node:nth-child(2) { background: #effbf6; border-color: #a6e5cf; box-shadow: 0 6px 0 #a6e5cf; }
  .node:nth-child(3) { background: #f4f0ff; border-color: #cbbcf7; box-shadow: 0 6px 0 #cbbcf7; }
  .node:nth-child(n+4) { background: #fff8e6; border-color: #ffe08a; box-shadow: 0 6px 0 #ffe08a; }
  .demo { color: #8a7aa6; }
  #dots i { border-color: #ff8fb8; border-width: 2px; }
  #dots i.on { background: #ff8fb8; }
  .btns button { background: #ffe3ef; border: 3px solid #ff9fc4; color: #e0457f; box-shadow: 0 4px 0 #ff9fc4; font-weight: 800; }
  .pop { position: fixed; z-index: 9; pointer-events: none; font-size: 1.8rem; animation: pop .9s ease-out forwards; }
  @keyframes pop { from { opacity: 1; transform: translate(-50%, -50%) scale(.4); } to { opacity: 0; transform: translate(calc(-50% + var(--dx)), calc(-50% - 90px)) scale(1.3) rotate(var(--rot)); } }
""",
    "html": '<i class="blob b1"></i><i class="blob b2"></i>' + STAR + HEART + CLOUD + FLOWER,
    # нажал на экран — вылетает стикер
    "js": """
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const set = ['💖', '⭐', '🌸', '✨', '🦋', '🌈'];
  document.addEventListener('click', e => {
    if (e.target.closest('a, button, i')) return;
    const s = document.createElement('span');
    s.className = 'pop'; s.textContent = set[Math.floor(Math.random() * set.length)];
    s.style.left = e.clientX + 'px'; s.style.top = e.clientY + 'px';
    s.style.setProperty('--dx', (Math.random() * 80 - 40) + 'px');
    s.style.setProperty('--rot', (Math.random() * 60 - 30) + 'deg');
    document.body.appendChild(s); setTimeout(() => s.remove(), 950);
  });
})();
""",
}


def render(deck: dict) -> str:
    return render_deck(deck, PASSPORT)
