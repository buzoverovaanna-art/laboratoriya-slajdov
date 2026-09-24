# -*- coding: utf-8 -*-
"""Стиль «Мем-шоу»: гифки, попапы-сюрпризы, конфетти, звуки по клику.

Самодостаточный HTML: открывается без интернета (гифки появятся
после подключения Tenor и будут встраиваться в файл).
"""
import html


def render(deck: dict) -> str:
    slides_html = []
    for i, s in enumerate(deck["slides"]):
        if s["type"] == "title":
            inner = f"""
        <div class="center">
          <div class="boom">💥</div>
          <h1>{html.escape(s['title'])}</h1>
          <p class="sub">{html.escape(s['subtitle'])}</p>
        </div>"""
        elif s["type"] == "outro":
            inner = f"""
        <div class="center">
          <div class="boom">🎤</div>
          <h1>{html.escape(s['title'])}</h1>
          <p class="sub">{html.escape(s['subtitle'])}</p>
          <p class="mic-drop">∇ микрофон брошен ∇</p>
        </div>"""
        else:
            bullets = "\n".join(
                f"<li><span class='pin'>▸</span> {html.escape(b)}</li>" for b in s["bullets"]
            )
            emoji = html.escape(s.get("emoji", "✨"))
            inner = f"""
        <div class="content-slide">
          <div class="emoji">{emoji}</div>
          <h2>{html.escape(s['title'])}</h2>
          <ul>{bullets}</ul>
        </div>"""
        note = '<div class="demo-note">демо-режим: тексты напишет ИИ после подключения ключа</div>' if deck.get("demo") else ""
        slides_html.append(f'<section class="slide" onclick="next()">{inner}{note}</section>')

    slides = "\n".join(slides_html)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(deck['topic'])} — Мем-шоу</title>
<style>
  :root {{
    --bg: #12071f; --card: #1d0d33; --accent: #ffd166; --accent2: #ef476f;
    --text: #fff7ed; --muted: #b8a6d9;
  }}
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ font-family: 'Comic Sans MS', 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); overflow: hidden; }}
  .slide {{
    display: none; min-height: 100vh; padding: 8vh 8vw;
    background: radial-gradient(circle at 20% 20%, #231042 0%, var(--bg) 60%);
    animation: pop .45s ease;
  }}
  .slide.active {{ display: block; }}
  @keyframes pop {{ from {{ transform: scale(.92); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
  .center {{ text-align: center; padding-top: 12vh; }}
  h1 {{ font-size: clamp(2.2rem, 7vw, 5rem); text-shadow: 4px 4px 0 var(--accent2); letter-spacing: .02em; }}
  h2 {{ font-size: clamp(1.6rem, 4.5vw, 3.2rem); color: var(--accent); margin-bottom: 4vh; text-shadow: 3px 3px 0 #00000055; }}
  .sub {{ color: var(--muted); font-size: clamp(1rem, 2.5vw, 1.6rem); margin-top: 2vh; }}
  .boom {{ font-size: clamp(3rem, 9vw, 6rem); animation: wobble 1.6s ease infinite; display: inline-block; }}
  @keyframes wobble {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg) scale(1.15); }} }}
  .emoji {{ font-size: clamp(2.5rem, 6vw, 4.5rem); margin-bottom: 2vh; }}
  ul {{ list-style: none; max-width: 40em; margin: 0 auto; }}
  li {{ font-size: clamp(1.1rem, 2.6vw, 1.7rem); padding: 1.6vh 0; border-bottom: 2px dashed #ffffff22; }}
  .pin {{ color: var(--accent2); font-weight: bold; }}
  .mic-drop {{ margin-top: 5vh; font-size: 1.3rem; color: var(--accent); }}
  .demo-note {{ position: absolute; bottom: 2vh; right: 2vw; color: #ffffff55; font-size: .75rem; font-family: monospace; }}
  .hint {{ position: fixed; bottom: 2vh; left: 2vw; color: #ffffff66; font-size: .8rem; z-index: 5; }}
  .nav {{ position: fixed; bottom: 2vh; left: 50%; transform: translateX(-50%); display: flex; gap: 12px; z-index: 5; }}
  .nav button {{
    font-size: 1.2rem; padding: 8px 22px; border-radius: 40px; border: none;
    background: var(--accent); color: #201038; cursor: pointer; font-weight: bold;
  }}
  .nav button:hover {{ transform: scale(1.1); }}
  .counter {{ position: fixed; bottom: 2.5vh; right: 2vw; color: #ffffff66; font-family: monospace; z-index: 5; }}
  .popup {{
    position: fixed; inset: 0; display: none; place-items: center; z-index: 50;
    background: #000000aa;
  }}
  .popup.open {{ display: grid; }}
  .popup-box {{
    background: var(--card); border: 4px solid var(--accent); border-radius: 20px;
    padding: 5vh 5vw; text-align: center; animation: pop .3s ease; max-width: 80vw;
  }}
  .popup-box .big {{ font-size: clamp(3rem, 10vw, 6rem); }}
  .popup-box p {{ font-size: clamp(1rem, 3vw, 1.5rem); margin-top: 2vh; }}
  #confetti {{ position: fixed; inset: 0; pointer-events: none; z-index: 40; }}
</style>
</head>
<body>
{slides}
<div class="hint">клик по слайду — дальше · сюрпризы ждут 🎁</div>
<div class="nav"><button onclick="go(-1)">◀</button><button onclick="boom()">🎉</button><button onclick="go(1)">▶</button></div>
<div class="counter" id="counter"></div>
<canvas id="confetti"></canvas>
<div class="popup" id="popup" onclick="this.classList.remove('open')">
  <div class="popup-box">
    <div class="big" id="popup-emoji">😸</div>
    <p id="popup-text">Сюрприз!</p>
  </div>
</div>
<script>
  const slides = [...document.querySelectorAll('.slide')];
  let cur = 0;
  const surprises = [
    ['🦄','Внимание: на этом докладе заскучать невозможно'],
    ['🐸','Факт: ты уже дочитал(а) до сюрприза. Уважение 👏'],
    ['🍕','Перерыв на пиццу не предусмотрен, но звучит приятно'],
    ['🚀','Этот слайд посетили точно с космической скоростью'],
    ['😎','Скучно было? Вот и мы о том же — дальше интереснее'],
  ];
  function show(i) {{
    slides[cur].classList.remove('active');
    cur = Math.max(0, Math.min(slides.length - 1, i));
    slides[cur].classList.add('active');
    document.getElementById('counter').textContent = (cur + 1) + ' / ' + slides.length;
  }}
  function go(d) {{ show(cur + d); }}
  function next() {{ go(1); }}
  function surprise() {{
    const s = surprises[Math.floor(Math.random() * surprises.length)];
    document.getElementById('popup-emoji').textContent = s[0];
    document.getElementById('popup-text').textContent = s[1];
    document.getElementById('popup').classList.add('open');
    beep(660, .08); setTimeout(() => beep(880, .1), 90);
  }}
  function beep(freq, dur) {{
    try {{
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.frequency.value = freq; o.type = 'triangle';
      o.connect(g); g.connect(ctx.destination);
      g.gain.setValueAtTime(.15, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(.001, ctx.currentTime + dur);
      o.start(); o.stop(ctx.currentTime + dur);
    }} catch (e) {{}}
  }}
  const cvs = document.getElementById('confetti'), cx = cvs.getContext('2d');
  let pieces = [];
  function resize() {{ cvs.width = innerWidth; cvs.height = innerHeight; }}
  addEventListener('resize', resize); resize();
  function boom() {{
    beep(520, .12);
    const colors = ['#ffd166', '#ef476f', '#06d6a0', '#118ab2', '#f78c6b'];
    for (let i = 0; i < 120; i++) {{
      pieces.push({{
        x: innerWidth / 2, y: innerHeight / 2,
        vx: (Math.random() - .5) * 14, vy: (Math.random() - .8) * 12,
        s: 4 + Math.random() * 6, c: colors[i % colors.length], r: Math.random() * Math.PI, life: 1
      }});
    }}
  }}
  (function tick() {{
    cx.clearRect(0, 0, cvs.width, cvs.height);
    pieces = pieces.filter(p => p.life > 0);
    for (const p of pieces) {{
      p.x += p.vx; p.y += p.vy; p.vy += .35; p.life -= .012; p.r += .1;
      cx.save(); cx.translate(p.x, p.y); cx.rotate(p.r);
      cx.fillStyle = p.c; cx.globalAlpha = Math.max(0, p.life);
      cx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s * .6); cx.restore();
    }}
    requestAnimationFrame(tick);
  }})();
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') go(1);
    if (e.key === 'ArrowLeft') go(-1);
  }});
  show(0);
  setTimeout(surprise, 12000);
</script>
</body>
</html>"""
