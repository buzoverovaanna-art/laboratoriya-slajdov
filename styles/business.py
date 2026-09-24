# -*- coding: utf-8 -*-
"""Паспорт стиля «Business»: деловой, строгий, без украшательств.

Правила «не как у ИИ»: без эмодзи, без градиентов, один яркий цвет (синий),
много воздуха. Принципы внимания из manim-video: главное ярко, контекст
приглушённо, сетка едва видна; бенто-плитки вместо списков.

Оформление как у корпоративного доклада: тёмно-синий титульный слайд,
светлые рабочие слайды с бегущей строкой темы сверху и крупным номером слайда.
"""
from styles.engine import render_deck

PASSPORT = {
    "id": "business",
    "name": "Business",
    "vars": {
        "--page-bg": "#f5f6f8", "--ink": "#0f1b3d", "--muted": "#5b6475", "--accent": "#1d4ed8",
        "--head": "#0f1b3d", "--card": "#ffffff", "--card-line": "#dfe2e8",
        "--card-shadow": "0 1px 0 #dfe2e8, 0 14px 30px rgba(15,27,61,.06)", "--line": "#c3c9d6", "--radius": "8px",
        "--font-head": "Georgia, 'Times New Roman', serif",
        "--font-body": "-apple-system, 'Helvetica Neue', Arial, sans-serif",
        "--t-in": "t-slide .5s ease both", "--t-in-back": "t-slide-back .5s ease both",
        "--modal-bg": "#ffffff", "--modal-ink": "#0f1b3d", "--modal-line": "#1d4ed8",
    },
    "modal_tag": "Пояснение",
    "wow": {},
    "markers": "number",
    "emblem_title": "",          # без значков и эмодзи
    "kicker_title": "Доклад",
    "css": """
  /* сетка едва видна */
  body::before { content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: .5;
    background-image: linear-gradient(#e6e8ed 1px, transparent 1px), linear-gradient(90deg, #e6e8ed 1px, transparent 1px);
    background-size: 8vw 8vw; }

  .slide { text-align: left; padding-left: 10vw; padding-right: 10vw; box-shadow: inset 0 6px 0 var(--accent); }
  .wrap { align-items: flex-start; }
  .bignum { align-items: flex-start; }

  /* бегущая строка темы и крупный номер слайда */
  .slide::after { content: attr(data-topic); position: absolute; top: 4.2vh; left: 10vw; right: 10vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    font: 600 .7rem -apple-system, 'Helvetica Neue', Arial, sans-serif; letter-spacing: .26em; text-transform: uppercase; color: var(--muted); }
  .slide::before { content: attr(data-n); position: absolute; right: 6vw; bottom: 6vh; z-index: -1; font: 700 clamp(6rem, 24vmin, 15rem)/1 Georgia, serif; color: rgba(29,78,216,.07); }

  /* титульный слайд: тёмно-синий, как обложка отчёта */
  .slide[data-kind=title], .slide[data-kind=outro] { box-shadow: none; }
  .slide[data-kind=title]::before { inset: 0; right: auto; bottom: auto; z-index: -1; width: 100%; height: 100%; font-size: 0; background: #0f1b3d; color: transparent; }
  .slide[data-kind=title]::after { color: #8fa6e0; }
  .slide[data-kind=title] h1 { color: #fff; }
  .slide[data-kind=title] .kicker { color: #8fb0ff; }
  .slide[data-kind=title] .sub { color: #b9c4e4; }
  .slide[data-kind=title] .author { color: #fff; padding: 10px 0 0; border-top: 2px solid #3d63d8; margin-top: 5vh; min-width: 16em; }
  .slide[data-kind=title] .divider::before { background: #5b82f0; }
  .slide[data-kind=title] .wrap { max-width: 44em; margin-left: 0; }

  .divider { font-size: 0; margin: 3.4vh 0; opacity: 1; }
  .divider::before { width: 4em; height: 3px; opacity: 1; background: var(--accent); }
  .divider::after { display: none; }
  .kicker { letter-spacing: .32em; font-weight: 700; font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; }
  h1 { font-weight: 500; max-width: 14em; }
  h2 { font-weight: 500; }

  /* карточки: строгие, с синей полосой и крупным номером */
  .card { border-left: 4px solid var(--accent); }
  .num { font: 700 1.5rem/1 Georgia, serif; letter-spacing: 0; margin-bottom: 1.6vh; }
  .card p { color: #1f2a4d; }

  .step { text-align: left; padding-left: 0; }
  .step::before { left: 1.25rem; background: var(--line); }
  .step .dot { left: 1.25rem; background: var(--accent); color: #fff; border: 0; }
  .step b, .step p { padding-left: 0; }
  .side { border-top: 4px solid var(--accent); }
  .side h3 { color: var(--accent); }
  .stem, .nodes::before, .node::before { display: none; }
  .core { border: 0; border-left: 5px solid var(--accent); background: #0f1b3d; color: #fff; border-radius: 4px; }
  .node { border-left: 3px solid var(--accent); }
  .nodes { padding-top: 2vh; }
  .core { margin-bottom: 1vh; }
  .bignum .value { font-weight: 600; padding-left: .3em; border-left: 6px solid var(--accent); }
  .quote blockquote { padding-left: 1.2em; border-left: 6px solid var(--accent); }
  .quote blockquote::before { display: none; }
  .demo { color: var(--muted); }
  .hud { color: var(--muted); }
  #dots i { border-radius: 2px; }
  .btns button { border-radius: 4px; }
""",
    "html": "",
    "js": "",
}


def render(deck: dict) -> str:
    return render_deck(deck, PASSPORT)
