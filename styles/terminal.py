# -*- coding: utf-8 -*-
"""Стиль «Терминал»: ретро-матрица, эффект печатной машинки.

Идея из ascii-video: символы как носитель эстетики.
"""
import html


def render(deck: dict) -> str:
    blocks = []
    for i, s in enumerate(deck["slides"]):
        if s["type"] == "title":
            lines = [f"$ load --topic \"{s['title']}\"", "> " + s["subtitle"], "> status: READY"]
            head = "┌─[ " + html.escape(s["topic"] if "topic" in s else "presentation") + " ]"
        elif s["type"] == "outro":
            lines = ["> " + s["subtitle"], "$ exit 0", "> EOF"]
        else:
            lines = [f"$ section --name \"{s['title']}\""] + ["> " + b for b in s["bullets"]]
        block_lines = "\n".join(f'<span class="tl">{html.escape(l)}</span>' for l in lines)
        blocks.append(f'<section class="slide"><pre class="term" data-lines="{len(lines)}">{block_lines}</pre></section>')

    slides = "\n".join(blocks)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(deck['topic'])} — terminal</title>
<style>
  * {{ margin: 0; box-sizing: border-box; }}
  body {{ background: #050805; color: #33ff66; font-family: 'SF Mono', Menlo, monospace; overflow: hidden; }}
  #matrix {{ position: fixed; inset: 0; opacity: .16; z-index: 0; }}
  .slide {{
    display: none; min-height: 100vh; padding: 12vh 8vw; position: relative; z-index: 1;
  }}
  .slide.active {{ display: block; }}
  .term {{
    font-size: clamp(.95rem, 2.2vw, 1.5rem); line-height: 2.1; white-space: pre-wrap;
    text-shadow: 0 0 8px #33ff6655; max-width: 46em;
  }}
  .tl {{ display: block; opacity: 0; animation: type-in .12s steps(2) forwards; }}
  .cursor {{ display: inline-block; width: .6em; height: 1.1em; background: #33ff66;
    animation: blink 1s step-end infinite; vertical-align: text-bottom; }}
  .prompt {{ position: fixed; bottom: 3vh; left: 8vw; z-index: 2; }}
  .hint {{ position: fixed; bottom: 3vh; right: 8vw; color: #33ff6666; font-size: .75rem; z-index: 2; }}
  @keyframes type-in {{ to {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
</head>
<body>
<canvas id="matrix"></canvas>
{slides}
<div class="prompt">user@school:~$ <span class="cursor"></span></div>
<div class="hint">→ дальше</div>
<script>
  const slides = [...document.querySelectorAll('.slide')];
  let cur = 0;
  function show(i) {{
    slides[cur].classList.remove('active');
    cur = Math.max(0, Math.min(slides.length - 1, i));
    const active = slides[cur];
    active.classList.add('active');
    active.querySelectorAll('.tl').forEach((l, k) => {{ l.style.animation = 'none'; void l.offsetWidth;
      l.style.animation = `type-in .12s steps(2) ${{k * .55}}s forwards`; }});
  }}
  function go(d) {{ show(cur + d); }}
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') go(1);
    if (e.key === 'ArrowLeft') go(-1);
  }});
  document.addEventListener('click', () => go(1));
  const cvs = document.getElementById('matrix'), cx = cvs.getContext('2d');
  let cols = [];
  function resize() {{
    cvs.width = innerWidth; cvs.height = innerHeight;
    cols = Array(Math.floor(cvs.width / 14)).fill(0).map(() => Math.random() * -50);
  }}
  addEventListener('resize', resize); resize();
  const glyphs = '01アイウエオカキクケコサシスセソ<>{{}}[]#$&';
  (function tick() {{
    cx.fillStyle = '#050805'; cx.fillRect(0, 0, cvs.width, cvs.height);
    cx.font = '13px monospace';
    cols.forEach((y, i) => {{
      cx.fillStyle = Math.random() > .97 ? '#aaffcc' : '#1a7a3a';
      cx.fillText(glyphs[Math.floor(Math.random() * glyphs.length)], i * 14, y * 16);
      cols[i] = y * 16 > cvs.height && Math.random() > .975 ? 0 : y + 1;
    }});
    requestAnimationFrame(tick);
  }})();
  show(0);
</script>
</body>
</html>"""
