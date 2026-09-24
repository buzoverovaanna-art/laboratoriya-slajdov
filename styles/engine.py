# -*- coding: utf-8 -*-
"""Общий движок презентаций.

Как это устроено:
  * РАСКЛАДКА — как выглядит слайд (карточки, лента времени, сравнение…).
    Раскладки написаны один раз и работают в любом стиле.
  * ПАСПОРТ СТИЛЯ — словарь: цвета, шрифты, фон, украшения, значки.
    Новый стиль = новый паспорт, раскладки трогать не нужно.

Данные слайдов (что кладёт Сценарист):
  title      {title, subtitle}
  cards      {title, bullets[]}            (старое имя «content» тоже понимается)
  timeline   {title, steps[{when, text}]}
  compare    {title, left{name, points[]}, right{name, points[]}}
  bignum     {title, value, caption}
  quote      {text, author}
  scheme     {title, center, nodes[]}
"""
import html
import json

from styles.common import NAV_JS
from styles.games_ui import GAMES_CSS, GAMES_JS

esc = html.escape

# ---------- паспорт по умолчанию: значения, которые стиль может переопределить ----------
DEFAULT_VARS = {
    "--page-bg": "#ffffff", "--ink": "#1a1a2e", "--muted": "#6b7280", "--accent": "#1d4ed8",
    "--head": "#1a1a2e", "--card": "#ffffff", "--card-line": "#e5e1d8", "--card-shadow": "none",
    "--line": "#c9c5bb", "--radius": "12px",
    "--font-head": "Georgia, 'Times New Roman', serif",
    "--font-body": "Georgia, 'Times New Roman', serif",
    "--t-in": "t-fade .5s ease both",
}

BASE_CSS = """
  * { margin: 0; box-sizing: border-box; }
  html, body { height: 100%; }
  body { color: var(--ink); font-family: var(--font-body); background: var(--page-bg); overflow: hidden; }
  .slide {
    display: none; position: relative; z-index: 2; height: 100vh; overflow-y: auto;
    padding: 8vh 8vw 13vh; flex-direction: column; text-align: center;
  }
  @supports (height: 100dvh) { .slide { height: 100dvh; } }
  .slide.active { display: flex; animation: var(--t-in); }
  body.going-back .slide.active { animation: var(--t-in-back, var(--t-in)); }
  .wrap { margin: auto; width: 100%; display: flex; flex-direction: column; align-items: center; }

  .emblem { width: clamp(80px, 15vmin, 130px); aspect-ratio: 1; margin-bottom: 4vh; display: grid; place-items: center;
    font-size: clamp(2rem, 7vmin, 3.2rem); opacity: 0; animation: rise .9s ease forwards; }
  .kicker { letter-spacing: .4em; text-transform: uppercase; font-size: clamp(.95rem, 2.4vmin, 1.35rem);
    color: var(--accent); margin-bottom: 3vh; opacity: 0; animation: rise .8s ease .2s forwards; }
  h1, h2 { font-family: var(--font-head); font-weight: 500; line-height: 1.12; color: var(--head);
    opacity: 0; animation: rise .9s ease .3s forwards; }
  h1 { font-size: clamp(2.4rem, 8.2vmin, 5.6rem); max-width: 16em; }
  h2 { font-size: clamp(1.9rem, 5.6vmin, 3.6rem); max-width: 22em; }
  .divider { display: flex; align-items: center; gap: 14px; margin: 3vh 0; color: var(--accent);
    opacity: 0; animation: rise .8s ease .55s forwards; }
  .divider::before, .divider::after { content: ''; width: clamp(50px, 14vw, 140px); height: 1px; background: var(--accent); opacity: .6; }
  .sub { color: var(--muted); font-size: clamp(1.15rem, 3vmin, 1.6rem); font-style: italic; max-width: 30em;
    opacity: 0; animation: rise .8s ease .8s forwards; }

  .author { margin-top: 3.4vh; font: 600 clamp(.9rem, 2.3vmin, 1.25rem) -apple-system, 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: .14em; color: var(--ink); opacity: 0; animation: rise .8s ease 1s forwards; }

  /* --- карточки --- */
  .cards { display: grid; gap: clamp(10px, 2vmin, 22px); width: min(100%, 62em);
    grid-template-columns: repeat(auto-fit, minmax(min(15em, 100%), 1fr)); }
  .card { position: relative; padding: clamp(16px, 3vmin, 30px) clamp(14px, 2.4vmin, 26px); text-align: left;
    border-radius: var(--radius); border: 1px solid var(--card-line); background: var(--card); box-shadow: var(--card-shadow);
    opacity: 0; transform: translateY(26px); animation: rise .8s ease var(--d, .5s) forwards; }
  .card p { font-size: clamp(1.15rem, 2.8vmin, 1.55rem); line-height: 1.5; }
  .num { display: block; font: 600 .75rem/1 -apple-system, 'Helvetica Neue', Arial, sans-serif; color: var(--accent);
    letter-spacing: .2em; margin-bottom: 1.4vh; }
  .gem { width: 2.6rem; height: 2.6rem; display: grid; place-items: center; margin-bottom: 1.2vh; font-size: 1.2rem;
    border-radius: 50%; border: 1.5px solid var(--el, var(--accent)); background: color-mix(in srgb, var(--el, var(--accent)) 22%, transparent); }
  .card small { display: block; letter-spacing: .3em; text-transform: uppercase; font-size: .68rem; color: var(--el, var(--accent)); margin-bottom: .6vh; }

  /* --- лента времени --- */
  .timeline { display: grid; gap: 14px; width: min(100%, 62em); grid-template-columns: repeat(auto-fit, minmax(9.5em, 1fr)); }
  .step { position: relative; padding-top: 3.4rem; text-align: center; opacity: 0; animation: rise .8s ease var(--d, .5s) forwards; }
  .step::before { content: ''; position: absolute; top: 1.2rem; left: 50%; right: -50%; height: 2px; background: var(--line); }
  .step:last-child::before { display: none; }
  .step .dot { position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 2.5rem; height: 2.5rem; display: grid; place-items: center;
    border-radius: 50%; border: 2px solid var(--el, var(--accent)); background: var(--page-bg-solid, var(--card)); color: var(--el, var(--accent)); font: 700 .9rem -apple-system, Arial, sans-serif; z-index: 1; }
  .step b { display: block; font-family: var(--font-head); font-size: clamp(1.25rem, 3.1vmin, 1.65rem); color: var(--head); margin-bottom: .5vh; }
  .step p { font-size: clamp(1.05rem, 2.5vmin, 1.35rem); line-height: 1.45; color: var(--muted); }

  /* --- сравнение --- */
  .compare { display: grid; gap: clamp(10px, 2vmin, 22px); width: min(100%, 60em); grid-template-columns: 1fr 1fr; align-items: stretch; }
  .side { text-align: left; padding: clamp(16px, 3vmin, 30px); border-radius: var(--radius); border: 1px solid var(--card-line);
    background: var(--card); box-shadow: var(--card-shadow); opacity: 0; animation: rise .8s ease var(--d, .5s) forwards; }
  .side h3 { font-family: var(--font-head); font-weight: 600; font-size: clamp(1.35rem, 3.4vmin, 1.85rem); color: var(--el, var(--accent)); margin-bottom: 1.6vh; }
  .side ul { list-style: none; padding: 0; display: grid; gap: 1.1vh; }
  .side li { position: relative; padding-left: 1.3em; font-size: clamp(1.1rem, 2.7vmin, 1.45rem); line-height: 1.45; }
  .side li::before { content: '◆'; position: absolute; left: 0; top: .1em; font-size: .7em; color: var(--el, var(--accent)); }

  /* --- большая цифра --- */
  .bignum { display: flex; flex-direction: column; align-items: center; }
  .bignum .value { font-family: var(--font-head); font-size: clamp(4.5rem, 24vmin, 12rem); line-height: 1; font-weight: 600; color: var(--accent);
    opacity: 0; animation: rise .9s ease .4s forwards; }
  .bignum .caption { max-width: 24em; color: var(--muted); font-size: clamp(1.2rem, 3.2vmin, 1.7rem); margin-top: 2vh; line-height: 1.4;
    opacity: 0; animation: rise .9s ease .7s forwards; }

  /* --- цитата --- */
  .quote blockquote { max-width: 22em; font-family: var(--font-head); font-style: italic; font-size: clamp(1.7rem, 5.4vmin, 3.2rem); line-height: 1.3; color: var(--head);
    opacity: 0; animation: rise .9s ease .3s forwards; }
  .quote blockquote::before { content: '“'; display: block; font-size: 2.6em; line-height: .6; color: var(--accent); margin-bottom: .1em; }
  .quote cite { display: block; margin-top: 3vh; font-style: normal; letter-spacing: .2em; text-transform: uppercase; font-size: clamp(.75rem, 1.8vmin, 1rem); color: var(--muted);
    opacity: 0; animation: rise .9s ease .7s forwards; }

  /* --- схема --- */
  .core { padding: 1.6vh 2.6vw; border-radius: var(--radius); border: 2px solid var(--accent); background: var(--card); box-shadow: var(--card-shadow);
    font-family: var(--font-head); font-size: clamp(1.2rem, 3.4vmin, 2rem); color: var(--head); max-width: 20em;
    opacity: 0; animation: rise .8s ease .3s forwards; }
  .stem { width: 2px; height: 3.4vh; background: var(--line); }
  .nodes { position: relative; display: grid; gap: clamp(10px, 2vmin, 20px); width: min(100%, 62em); padding-top: 3vh;
    grid-template-columns: repeat(auto-fit, minmax(min(11em, 100%), 1fr)); }
  .nodes::before { content: ''; position: absolute; top: 0; left: 12%; right: 12%; height: 2px; background: var(--line); }
  .node { position: relative; padding: clamp(12px, 2.4vmin, 22px); border-radius: var(--radius); border: 1px solid var(--card-line); background: var(--card);
    box-shadow: var(--card-shadow); font-size: clamp(1.1rem, 2.6vmin, 1.4rem); line-height: 1.4; opacity: 0; animation: rise .8s ease var(--d, .6s) forwards; }
  .node::before { content: ''; position: absolute; top: -3vh; left: 50%; width: 2px; height: 3vh; background: var(--line); }

  /* --- нижняя панель --- */
  .demo { position: fixed; bottom: 62px; left: 0; right: 0; z-index: 3; text-align: center; font: .72rem -apple-system, Arial, sans-serif;
    letter-spacing: .1em; color: var(--muted); opacity: .8; pointer-events: none; }
  .hud { position: fixed; z-index: 4; left: max(22px, 4vmin); right: max(22px, 4vmin); bottom: 16px; display: flex; justify-content: space-between; align-items: center; gap: 12px;
    font: .78rem -apple-system, Arial, sans-serif; letter-spacing: .1em; color: var(--muted); }
  .hud .topic { max-width: 30vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  #dots { display: flex; gap: 10px; }
  #dots i { width: 11px; height: 11px; border-radius: 50%; border: 1.5px solid var(--accent); cursor: pointer; transition: all .25s; }
  #dots i.on { background: var(--accent); }
  .btns button { background: transparent; color: var(--accent); border: 1px solid var(--accent); border-radius: 999px; padding: 8px 16px; font: inherit; cursor: pointer; min-height: 40px; }

  /* --- переходы между слайдами (стиль выбирает один через --t-in) --- */
  @keyframes t-fade { from { opacity: 0; } to { opacity: 1; } }
  @keyframes t-slide { from { opacity: 0; transform: translateX(7vw); } to { opacity: 1; transform: none; } }
  @keyframes t-slide-back { from { opacity: 0; transform: translateX(-7vw); } to { opacity: 1; transform: none; } }
  @keyframes t-glow { from { opacity: 0; filter: blur(16px) brightness(1.6); transform: scale(1.05); } to { opacity: 1; filter: none; transform: none; } }
  @keyframes t-pop { 0% { opacity: 0; transform: scale(.82) rotate(-2.5deg); } 55% { opacity: 1; transform: scale(1.04) rotate(1deg); } 100% { opacity: 1; transform: none; } }
  @keyframes t-comic { from { clip-path: polygon(0 0, 0 0, -30% 100%, 0 100%); } to { clip-path: polygon(0 0, 135% 0, 105% 100%, -30% 100%); } }
  @keyframes t-comic-back { from { clip-path: polygon(100% 0, 100% 0, 130% 100%, 100% 100%); } to { clip-path: polygon(-35% 0, 100% 0, 100% 100%, -5% 100%); } }

  /* --- название «выпрыгивает» по буквам --- */
  .reveal .w { display: inline-block; white-space: nowrap; }
  .reveal .l { display: inline-block; opacity: 0; animation: letter .6s cubic-bezier(.2, 1.5, .4, 1) calc(.4s + var(--i) * .04s) forwards; }
  @keyframes letter { from { opacity: 0; transform: translateY(.7em) scale(.5) rotate(-10deg); } to { opacity: 1; transform: none; } }

  /* --- шпаргалка выступления и источники --- */
  #notes { position: fixed; left: 50%; bottom: 66px; transform: translateX(-50%); z-index: 6; width: min(92vw, 46em); max-height: 36vh; overflow: auto; padding: 14px 18px;
    border-radius: 16px; background: rgba(15, 20, 40, .93); color: #fff; font: 1rem/1.55 -apple-system, 'Helvetica Neue', Arial, sans-serif; text-align: left; box-shadow: 0 12px 40px rgba(0,0,0,.4); }
  #notes[hidden] { display: none; }
  #notes::before { content: 'ШПАРГАЛКА · что говорить'; display: block; font-size: .7rem; letter-spacing: .18em; opacity: .65; margin-bottom: 6px; }
  .src { margin-top: 3vh; max-width: 46em; font: .78rem/1.5 -apple-system, Arial, sans-serif; color: var(--muted); opacity: .9; }

  /* --- всплывающее окно с фактом --- */
  [data-fact] { cursor: pointer; }
  .more { position: absolute; top: 10px; right: 12px; z-index: 2; width: 1.7rem; height: 1.7rem; display: grid; place-items: center; border-radius: 50%;
    background: var(--accent); color: var(--more-fg, #fff); font: 800 1.05rem/1 -apple-system, Arial, sans-serif; animation: hint 2.4s ease-in-out infinite; }
  .step .more { top: 0; right: 6%; } .node .more { top: 8px; right: 8px; }
  @keyframes hint { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
  #modal { position: fixed; inset: 0; z-index: 30; display: none; place-items: center; padding: 20px; background: rgba(10, 10, 25, .55); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }
  #modal.open { display: grid; animation: t-fade .25s ease both; }
  .mbox { position: relative; width: min(92vw, 34em); padding: clamp(22px, 4vw, 36px); text-align: left; border-radius: var(--radius); background: var(--modal-bg, #fff); color: var(--modal-ink, #14213d);
    border: 3px solid var(--modal-line, var(--accent)); box-shadow: var(--modal-shadow, 0 24px 60px rgba(0, 0, 0, .4)); animation: mpop .5s cubic-bezier(.2, 1.3, .4, 1) both; }
  @keyframes mpop { from { opacity: 0; transform: translateY(30px) scale(.85); } to { opacity: 1; transform: none; } }
  .mtag { font: 800 .75rem -apple-system, Arial, sans-serif; letter-spacing: .22em; text-transform: uppercase; color: var(--modal-line, var(--accent)); margin-bottom: 10px; }
  .mtitle { display: block; font-family: var(--font-head); font-size: clamp(1.35rem, 3.4vmin, 1.75rem); margin-bottom: 10px; }
  .mtext { font-size: clamp(1.15rem, 2.8vmin, 1.45rem); line-height: 1.5; }
  .mx { position: absolute; top: 10px; right: 12px; width: 2.4rem; height: 2.4rem; border-radius: 50%; border: 0; background: rgba(128, 128, 128, .2); color: inherit; font-size: 1.5rem; line-height: 1; cursor: pointer; }

  @keyframes rise { from { opacity: 0; transform: translateY(26px); } to { opacity: 1; transform: none; } }

  /* --- картинка на слайде: тематическая или мем/гифка --- */
  .wrap--pic { flex-direction: row; align-items: center; gap: clamp(20px, 4vw, 56px); text-align: left; max-width: 70em; }
  .wrap--pic .wrap-body { flex: 1 1 52%; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; }
  .wrap--pic .wrap-body > * { max-width: 100%; }
  .wrap--pic .wrap-body h1, .wrap--pic .wrap-body h2, .wrap--pic .wrap-body .sub, .wrap--pic .wrap-body .kicker,
  .wrap--pic .wrap-body .divider, .wrap--pic .wrap-body .author { text-align: left; align-self: flex-start; }
  .wrap--pic .wrap-body .divider::after { display: none; }
  .slide-pic { flex: 0 0 42%; max-width: 42%; margin: 0; opacity: 0; animation: rise .8s ease .15s forwards; }
  .slide-pic img { display: block; width: 100%; max-height: 56vh; object-fit: cover; border-radius: var(--radius); border: 1px solid var(--card-line); box-shadow: var(--card-shadow); }
  .slide-pic--meme img { object-fit: contain; background: var(--card); max-height: 46vh; }
  .slide-pic figcaption { margin-top: 1.2vh; font-size: .76rem; line-height: 1.35; color: var(--muted); }
  @media (max-width: 900px) {
    .wrap--pic { flex-direction: column; text-align: center; }
    .wrap--pic .wrap-body { align-items: center; }
    .wrap--pic .wrap-body h1, .wrap--pic .wrap-body h2, .wrap--pic .wrap-body .sub, .wrap--pic .wrap-body .kicker,
    .wrap--pic .wrap-body .divider, .wrap--pic .wrap-body .author { text-align: center; align-self: center; }
    .wrap--pic .wrap-body .divider::after { display: block; }
    .slide-pic { max-width: 70%; flex: 0 0 auto; order: -1; }
    .slide-pic img { max-height: 32vh; }
  }

  @media (max-width: 640px) {
    .compare { grid-template-columns: 1fr; }
    .stem, .nodes::before, .node::before { display: none; }
    .hud .topic { display: none; }
    .timeline { grid-template-columns: 1fr; }
    .step { text-align: left; padding: 0 0 0 3.6rem; min-height: 3rem; }
    .step::before { top: 2.4rem; bottom: -14px; left: 1.2rem; right: auto; width: 2px; height: auto; }
    .step .dot { left: 0; transform: none; }
  }
  @media (prefers-reduced-motion: reduce) { * { animation-duration: .01s !important; animation-delay: 0s !important; } }
"""

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__ — __STYLE__</title>
<style>
  :root { __VARS__ }
__BASE_CSS__
__EXTRA_CSS__
__GAME_CSS__
</style>
</head>
<body>
__EXTRA_HTML__
__SLIDES__
__DEMO__
<div class="hud">
  <span class="topic">__TOPIC__</span>
  <span id="dots"></span>
  <span class="btns">__NOTES_BTN__<button id="play" aria-label="Автопоказ">▶</button> <button id="fs" aria-label="На весь экран">⛶</button> <button onclick="go(-1)" aria-label="Назад">←</button> <button onclick="go(1)" aria-label="Дальше">→</button></span>
</div>
<div id="notes" hidden></div>
__GAME_HTML__
<div id="modal" role="dialog" aria-modal="true"><div class="mbox"><button class="mx" aria-label="Закрыть">×</button><div class="mtag">__MODAL_TAG__</div><b class="mtitle"></b><p class="mtext"></p></div></div>
<script>
window.WOW = __WOW__;
__NAV__
__EXTRA_JS__
__GAME_JS__
</script>
</body>
</html>"""


# ---------- раскладки ----------
def _accent(p, ctx):
    """Следующий значок/цвет из паспорта (по кругу) или None."""
    acc = p.get("accents")
    if not acc:
        return None
    a = acc[ctx["n"] % len(acc)]
    ctx["n"] += 1
    return a


def _mark(p, ctx, i):
    """Маркер карточки: (css-цвет, html). Значок стихии/цвет или номер 01, 02…"""
    a = _accent(p, ctx) if p.get("markers") == "gem" else None
    if a:
        name, color, icon = a
        return f"--el:{color};", f'<div class="gem">{icon}</div><small>{esc(name)}</small>'
    return "", f'<span class="num">{i + 1:02d}</span>'


def _titlebit(s, tag="h2"):
    return f"<{tag}>{esc(s['title'])}</{tag}><div class=\"divider\">◆</div>" if s.get("title") else ""


def _reveal(text):
    """Название по буквам: слова не рвутся, каждая буква появляется со своей задержкой."""
    out, i = [], 0
    for word in text.split(" "):
        letters = "".join(f'<span class="l" style="--i:{i + k}">{esc(ch)}</span>' for k, ch in enumerate(word))
        i += len(word) + 1
        out.append(f'<span class="w">{letters}</span>')
    return " ".join(out)


def _fact(title, facts, i):
    """Атрибуты и значок «нажми» для элемента с всплывающим фактом (если факт есть)."""
    fact = facts[i] if i < len(facts) else ""
    if not fact:
        return "", ""
    return (f' data-title="{esc(title, quote=True)}" data-fact="{esc(fact, quote=True)}" tabindex="0" role="button"',
            '<span class="more" aria-hidden="true">＋</span>')


def layout_title(s, p, ctx):
    emblem = f'<div class="emblem">{p.get("emblem_title", "")}</div>' if p.get("emblem_title") else ""
    return (f'{emblem}<div class="kicker">{esc(p.get("kicker_title", "Презентация"))}{esc(" · " + s["subject"]) if s.get("subject") else ""}</div>'
            f'<h1 class="reveal" aria-label="{esc(s["title"], quote=True)}"><span aria-hidden="true">{_reveal(s["title"])}</span></h1><div class="divider">◆</div><p class="sub">{esc(s.get("subtitle", ""))}</p>'
            + (f'<p class="author">{esc(s["author"])}</p>' if s.get("author") else ""))


def layout_cards(s, p, ctx):
    out = []
    for i, b in enumerate(s["bullets"]):
        color, mark = _mark(p, ctx, i)
        attrs, more = _fact(b, s.get("facts", []), i)
        out.append(f'<div class="card"{attrs} style="{color}--d:{round(0.5 + i * 0.16, 2)}s">{more}{mark}<p>{esc(b)}</p></div>')
    src = f'<p class="src">Источники: {esc("; ".join(s["sources"]))}</p>' if s.get("sources") else ""
    # эхо обложки: на «Выводах» повторяем тот же «кикер», что был на титульном слайде
    echo = (f'<div class="kicker">{esc(p.get("kicker_title", "Презентация"))}'
            f'{esc(" · " + s["subject"]) if s.get("subject") else ""}</div>') if s.get("cover_echo") else ""
    return f'{echo}{_titlebit(s)}<div class="cards">{"".join(out)}</div>{src}'


def layout_timeline(s, p, ctx):
    out = []
    for i, st in enumerate(s["steps"]):
        a = _accent(p, ctx) if p.get("markers") == "gem" else None
        color = f"--el:{a[1]};" if a else ""
        dot = a[2] if a else f"{i + 1}"
        attrs, more = _fact(st["text"], s.get("facts", []), i)
        out.append(f'<div class="step"{attrs} style="{color}--d:{round(0.5 + i * 0.16, 2)}s">{more}<div class="dot">{dot}</div>'
                   f'<b>{esc(st["when"])}</b><p>{esc(st["text"])}</p></div>')
    return f'{_titlebit(s)}<div class="timeline">{"".join(out)}</div>'


def layout_compare(s, p, ctx):
    sides = []
    for k, key in enumerate(("left", "right")):
        side = s[key]
        a = _accent(p, ctx) if p.get("markers") == "gem" else None
        color = f"--el:{a[1]};" if a else ""
        items = "".join(f"<li>{esc(x)}</li>" for x in side["points"])
        sides.append(f'<div class="side" style="{color}--d:{round(0.5 + k * 0.2, 2)}s"><h3>{esc(side["name"])}</h3><ul>{items}</ul></div>')
    return f'{_titlebit(s)}<div class="compare">{"".join(sides)}</div>'


def layout_bignum(s, p, ctx):
    return (f'<div class="bignum">'
            f'{_titlebit(s)}<div class="value">{esc(s["value"])}</div><p class="caption">{esc(s["caption"])}</p></div>')


def layout_quote(s, p, ctx):
    return f'<div class="quote"><blockquote>{esc(s["text"])}</blockquote><cite>{esc(s["author"])}</cite></div>'


def layout_scheme(s, p, ctx):
    nodes = ""
    for i, n in enumerate(s["nodes"]):
        attrs, more = _fact(n, s.get("facts", []), i)
        nodes += f'<div class="node"{attrs} style="--d:{round(0.6 + i * 0.14, 2)}s">{more}{esc(n)}</div>'
    return f'{_titlebit(s)}<div class="core">{esc(s["center"])}</div><div class="stem"></div><div class="nodes">{nodes}</div>'


GAME_INFO = {
    "team": ("🕵️", "Игра для класса", "Класс делится на 2 команды и отвечает на вопросы по теме — учитель ведёт счёт"),
}


def layout_games(s, p, ctx):
    """Слайд «Игровая зона»: кнопки, которые открывают игры на весь экран."""
    btns = "".join(
        f'<button class="gamebtn" data-game="{g}" style="--d:{round(0.5 + i * 0.16, 2)}s"><span class="gi">{GAME_INFO[g][0]}</span>'
        f'<b>{esc(GAME_INFO[g][1])}</b><span class="d">{esc(GAME_INFO[g][2])}</span></button>'
        for i, g in enumerate(s.get("available", [])) if g in GAME_INFO)
    note = ""
    if s.get("failed"):
        note = f'<p class="gamenote">Не получилось добавить: {esc(", ".join(s["failed"]))}. Попробуй ещё раз кнопкой «＋ Игра» на главной странице.</p>'
    return f'{_titlebit(s)}<div class="gamegrid">{btns}</div>{note}'


LAYOUTS = {
    "games": layout_games,
    "title": layout_title,
    "cards": layout_cards,
    "content": layout_cards,  # старое имя
    "outro": layout_title,    # старое имя: итоговый слайд-заставка
    "timeline": layout_timeline,
    "compare": layout_compare,
    "bignum": layout_bignum,
    "quote": layout_quote,
    "scheme": layout_scheme,
}


def _picture(s):
    """Картинка слайда (тематическая или мем/гифка) — figure с подписью-источником, если она есть."""
    img = s.get("image")
    if not img:
        return ""
    cap = f'<figcaption>{esc(img["credit"])}</figcaption>' if img.get("credit") else ""
    return (f'<figure class="slide-pic slide-pic--{esc(img.get("kind") or "photo")}">'
            f'<img src="{img["data"]}" alt="{esc(img.get("alt", ""), quote=True)}" loading="lazy">{cap}</figure>')


def render_deck(deck: dict, passport: dict) -> str:
    """Собирает одну самодостаточную HTML-страницу: раскладки × паспорт стиля."""
    ctx = {"n": 0}
    slides = []
    for n, s in enumerate(deck["slides"], 1):
        fn = LAYOUTS.get(s["type"])
        if fn is None:
            raise ValueError(f"Неизвестная раскладка: {s['type']}")
        pic = _picture(s)
        body = f'{pic}<div class="wrap-body">{fn(s, passport, ctx)}</div>' if pic else fn(s, passport, ctx)
        wrap_class = "wrap wrap--pic" if pic else "wrap"
        slides.append(f'<section class="slide" data-kind="{s["type"]}" data-n="{n:02d}" data-topic="{esc(deck["topic"], quote=True)}" data-notes="{esc(s.get("notes", ""), quote=True)}">'
                      f'<div class="{wrap_class}">{body}</div></section>')

    games = deck.get("games") or None
    game_html = ('<div id="game" aria-modal="true"></div><script type="application/json" id="game-data">'
                 + json.dumps(games, ensure_ascii=False).replace("</", "<\\/") + "</script>") if games else ""
    css_vars = dict(DEFAULT_VARS, **passport.get("vars", {}))
    demo = f'<div class="demo">{esc(deck.get("demo_note", "демо-режим: тексты напишет ИИ"))}</div>' if deck.get("demo") else ""
    return (
        PAGE.replace("__TITLE__", esc(deck["topic"]))
        .replace("__STYLE__", esc(passport["name"]))
        .replace("__TOPIC__", esc(deck["topic"]))
        .replace("__VARS__", " ".join(f"{k}: {v};" for k, v in css_vars.items()))
        .replace("__BASE_CSS__", BASE_CSS)
        .replace("__EXTRA_CSS__", passport.get("css", ""))
        .replace("__EXTRA_HTML__", passport.get("html", ""))
        .replace("__SLIDES__", "\n".join(slides))
        .replace("__NOTES_BTN__", '<button id="notesBtn" aria-label="Шпаргалка выступления">📝</button> ' if any(x.get("notes") for x in deck["slides"]) else "")
        .replace("__DEMO__", demo)
        .replace("__NAV__", NAV_JS)
        .replace("__EXTRA_JS__", passport.get("js", ""))
        .replace("__GAME_CSS__", GAMES_CSS if games else "")
        .replace("__GAME_JS__", GAMES_JS if games else "")
        .replace("__GAME_HTML__", game_html)
        .replace("__MODAL_TAG__", esc(passport.get("modal_tag", "Интересный факт")))
        .replace("__WOW__", json.dumps(passport.get("wow", {}), ensure_ascii=False))
    )
