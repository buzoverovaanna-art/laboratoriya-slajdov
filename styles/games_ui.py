# -*- coding: utf-8 -*-
"""Игра внутри презентации: «Игра для класса» (окно на весь экран).

Цвета, шрифты и форма берутся из стиля презентации (переменные CSS), поэтому в Brawl Stars игра яркая,
в Genshin Impact золотая и ночная, в Business строгая. Данные игры лежат в
<script id="game-data"> (см. games.py). Подключается, только если в презентацию добавлена игра.

Правила и счёт — как в классе: класс делится на 2 команды, вопросы показываются по очереди,
команда отвечает вслух, учитель кликает вариант, чтобы показать верный ответ, и ставит очко
командой вручную (кнопки +/− у её названия). Автосчёта нет — это решает учитель.
"""

GAMES_CSS = """
  /* --- кнопка на слайде «Игровая зона» --- */
  .gamegrid { display: flex; gap: clamp(12px, 2.4vmin, 24px); flex-wrap: wrap; justify-content: center; width: min(100%, 52em); }
  .gamebtn { flex: 1 1 15em; max-width: 24em; padding: clamp(18px, 3.4vmin, 32px); border-radius: var(--radius); border: 2px solid var(--accent); background: var(--card);
    color: var(--card-ink, var(--ink)); text-align: center; cursor: pointer; font: inherit; box-shadow: var(--card-shadow); transition: transform .15s ease;
    opacity: 0; animation: rise .8s ease var(--d, .5s) forwards; }
  .gamebtn:hover { transform: translateY(-4px) scale(1.02); }
  .gamebtn .gi { display: block; font-size: clamp(2.4rem, 8vmin, 3.6rem); }
  .gamebtn b { display: block; margin: .3em 0 .2em; font-family: var(--font-head); font-size: clamp(1.2rem, 3.2vmin, 1.7rem); color: var(--card-head, var(--head)); }
  .gamebtn span.d { color: var(--card-muted, var(--muted)); font-size: clamp(.9rem, 2.1vmin, 1.1rem); line-height: 1.4; }
  .gamenote { margin-top: 3vh; color: var(--muted); font-size: .95rem; max-width: 34em; }

  /* --- окно игры --- */
  #game { position: fixed; inset: 0; z-index: 40; display: none; overflow-y: auto; background: var(--page-bg); background-attachment: fixed; color: var(--ink); font-family: var(--font-body); }
  #game.open { display: block; animation: t-fade .3s ease both; }
  .g-close { position: fixed; top: 14px; right: 14px; z-index: 41; width: 46px; height: 46px; border-radius: 50%; border: 2px solid var(--accent); background: var(--card); color: var(--card-ink, var(--ink)); font-size: 1.4rem; cursor: pointer; }
  .g-wrap { max-width: 900px; margin: 0 auto; padding: max(64px, 7vh) 20px 40px; text-align: center; }
  .g-wrap h2 { font-family: var(--font-head); font-size: clamp(1.8rem, 5vmin, 3rem); color: var(--head); animation: none; opacity: 1; margin-bottom: 8px; -webkit-text-stroke: 0; text-shadow: none; transform: none; background: none; filter: none; }
  .g-sub { color: var(--muted); font-size: clamp(1.15rem, 2.8vmin, 1.45rem); margin-bottom: 22px; }
  .g-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 56px; padding: 12px 24px; margin: 6px; border-radius: 999px; border: 2px solid var(--accent);
    background: var(--card); color: var(--card-ink, var(--ink)); font: 700 clamp(1rem, 2.4vmin, 1.2rem) var(--font-body); cursor: pointer; box-shadow: var(--card-shadow); transition: transform .12s; }
  .g-btn:hover { transform: translateY(-2px); } .g-btn:active { transform: scale(.97); }
  .g-btn.main { background: var(--accent); color: var(--on-accent, #fff); }
  .g-names { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin: 6px 0 14px; }
  .g-names label { display: grid; gap: 4px; text-align: left; font-size: .8rem; color: var(--muted); font-weight: 700; }
  .g-names input { width: 12em; padding: 10px 14px; border-radius: 14px; border: 2px solid var(--accent); background: var(--card); color: var(--card-ink, var(--ink)); font: 700 1rem var(--font-body); }

  /* табло команд */
  .g-teams { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; }
  .g-team { display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; border: 2px solid var(--accent); background: var(--card); color: var(--card-ink, var(--ink)); box-shadow: var(--card-shadow); }
  .g-team .g-em { font-size: 1.25rem; }
  .g-tname { width: 8em; max-width: 30vw; border: none; background: transparent; font: 700 1rem var(--font-body); color: inherit; border-bottom: 2px dashed rgba(128,128,128,.4); text-align: center; padding: 2px 0; }
  .g-tname:focus { outline: none; border-color: var(--accent); }
  .g-sc { font-family: var(--font-head); font-size: 1.3rem; min-width: 1.4em; text-align: center; }
  .g-sbtn { width: 28px; height: 28px; flex: none; border-radius: 50%; border: 2px solid var(--accent); background: transparent; color: inherit; font: 800 1rem var(--font-body); line-height: 1; cursor: pointer; }
  .g-sbtn:hover { background: var(--accent); color: var(--on-accent, #fff); }

  /* вопрос */
  .g-q { padding: clamp(14px, 3vmin, 26px); border-radius: var(--radius); border: 2px solid var(--card-line, var(--accent)); background: var(--card); box-shadow: var(--card-shadow); text-align: left; color: var(--card-ink, var(--ink)); }
  .g-turn { color: var(--card-muted, var(--muted)); font-size: .92rem; margin-bottom: 8px; }
  .g-timer { height: 8px; border-radius: 9px; background: rgba(128,128,128,.25); overflow: hidden; margin-bottom: 12px; }
  .g-timer i { display: block; height: 100%; width: 100%; background: var(--accent); transform-origin: left; animation: gtimer 30s linear forwards; }
  .g-q h3 { font-family: var(--font-head); font-size: clamp(1.35rem, 3.6vmin, 2rem); line-height: 1.3; margin-bottom: 14px; color: var(--card-head, var(--head)); }
  .g-opts { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
  .g-opt { display: flex; align-items: center; gap: 10px; min-height: 60px; padding: 10px 14px; border-radius: 14px; border: 2px solid var(--accent); background: transparent; color: var(--card-ink, var(--ink));
    font: 700 clamp(1.1rem, 2.7vmin, 1.4rem) var(--font-body); text-align: left; cursor: pointer; transition: transform .12s, background .15s;
    opacity: 0; animation: g-pop .5s cubic-bezier(.2,1.5,.45,1) both; animation-delay: calc(var(--d, 0) * 1s); }
  .g-opt span { flex: none; display: grid; place-items: center; width: 2rem; height: 2rem; border-radius: 50%; background: var(--accent); color: var(--on-accent, #fff); font-weight: 800; }
  .g-opt:hover:not(:disabled) { transform: translateY(-2px); }
  .g-opt:disabled { cursor: default; opacity: .9; }
  .g-opt.ok { background: #2f9e5b; border-color: #2f9e5b; color: #fff; animation: g-bounce .5s; }
  .g-opt.no { background: #d64545; border-color: #d64545; color: #fff; animation: g-shake .45s; }
  .g-opt.ok span, .g-opt.no span { background: #fff; color: #222; }
  .g-feedback { margin-top: 14px; min-height: 1.5em; font-weight: 600; font-size: clamp(1.05rem, 2.4vmin, 1.3rem); }
  .g-trophy { font-size: clamp(4rem, 14vmin, 7rem); }
  @keyframes gtimer { to { transform: scaleX(0); } }
  @keyframes g-pop { 0% { opacity: 0; transform: scale(.4) rotate(-10deg); } 100% { opacity: 1; transform: scale(1) rotate(0deg); } }
  @keyframes g-bounce { 0% { transform: scale(1); } 40% { transform: scale(1.08); } 100% { transform: scale(1); } }
  @keyframes g-shake { 0%, 100% { transform: translateX(0); } 20%, 60% { transform: translateX(-8px); } 40%, 80% { transform: translateX(8px); } }
  @media (prefers-reduced-motion: reduce) { .g-opt { animation: none; opacity: 1; } .g-opt.ok, .g-opt.no { animation: none; } }
  @media (max-width: 640px) { .g-opts { grid-template-columns: 1fr; } }
"""

GAMES_JS = r"""
(function () {
  const box = document.getElementById('game'); if (!box) return;
  const D = JSON.parse(document.getElementById('game-data').textContent);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  let timers = [], st = null;
  const later = (fn, ms) => { const t = setTimeout(fn, ms); timers.push(t); return t; };
  const clearTimers = () => { timers.forEach(clearTimeout); timers = []; };

  function frame(html) {
    box.innerHTML = '<button class="g-close" aria-label="Закрыть игру">✕</button><div class="g-wrap">' + html + '</div>';
    box.querySelector('.g-close').onclick = close; box.scrollTop = 0;
  }
  function open() { if (typeof stopPlay === 'function') stopPlay(); box.classList.add('open'); teamSetup(); }
  function close() { clearTimers(); box.classList.remove('open'); box.innerHTML = ''; }
  document.addEventListener('click', e => { const b = e.target.closest('.gamebtn'); if (b) open(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && box.classList.contains('open')) close(); });

  /* ================= ИГРА ДЛЯ КЛАССА ================= */
  function teamSetup() {
    frame('<h2>🕵️ Игра для класса</h2><p class="g-sub">Разделите класс на 2 команды. Вопрос за вопросом: команда отвечает вслух, а на экране жмите на вариант — он покажет, верно ли, и очко команде ставьте сами (+/− у её названия).</p>' +
      '<div class="g-names"><label>Команда 1<input id="n1" value="Команда 1" maxlength="16"></label><label>Команда 2<input id="n2" value="Команда 2" maxlength="16"></label></div>' +
      '<button class="g-btn main" id="start">▶ Начать</button>');
    box.querySelector('#start').onclick = () => teamStart(box.querySelector('#n1').value.trim(), box.querySelector('#n2').value.trim());
  }
  function teamStart(n1, n2) {
    st = { names: [n1 || 'Команда 1', n2 || 'Команда 2'], score: [0, 0], i: 0,
      qs: shuffle(D.team.questions).map(q => { const order = shuffle(q.options.map((_, k) => k)); return { q: q.question, opts: order.map(k => q.options[k]), ok: order.indexOf(q.correct), why: q.explanation }; }) };
    teamQuestion();
  }
  function scoreboard() {
    return '<div class="g-teams">' + [0, 1].map(k => '<div class="g-team"><span class="g-em">' + (k === 0 ? '🔥' : '⚡') + '</span>' +
      '<input class="g-tname" id="tn' + k + '" value="' + esc(st.names[k]) + '" maxlength="16">' +
      '<button class="g-sbtn" data-t="' + k + '" data-v="-1">−</button><span class="g-sc" id="sc' + k + '">' + st.score[k] + '</span>' +
      '<button class="g-sbtn" data-t="' + k + '" data-v="1">+</button></div>').join('') + '</div>';
  }
  function bindScoreboard() {
    box.querySelectorAll('.g-tname').forEach((inp, k) => inp.oninput = () => { st.names[k] = inp.value.trim() || ('Команда ' + (k + 1)); });
    box.querySelectorAll('.g-sbtn').forEach(b => b.onclick = () => {
      const t = +b.dataset.t; st.score[t] = Math.max(0, st.score[t] + (+b.dataset.v)); box.querySelector('#sc' + t).textContent = st.score[t];
    });
  }
  function teamQuestion() {
    if (st.i >= st.qs.length) return teamEnd();
    clearTimers();
    const q = st.qs[st.i];
    frame(scoreboard() + '<div class="g-q"><div class="g-turn">Вопрос ' + (st.i + 1) + ' из ' + st.qs.length + '</div>' +
      '<div class="g-timer"><i></i></div><h3>' + esc(q.q) + '</h3><div class="g-opts">' +
      q.opts.map((o, k) => '<button class="g-opt" data-k="' + k + '" style="--d:' + (k * .12) + '"><span>' + 'ABCD'[k] + '</span>' + esc(o) + '</button>').join('') +
      '</div><div class="g-feedback"></div></div>');
    bindScoreboard();
    box.querySelectorAll('.g-opt').forEach(b => b.onclick = () => resolveTeam(+b.dataset.k));
    later(() => resolveTeam(null), 30000);
  }
  function resolveTeam(k) {
    clearTimers();
    const q = st.qs[st.i];
    box.querySelectorAll('.g-opt').forEach((b, idx) => { b.disabled = true; if (idx === q.ok) b.classList.add('ok'); else if (idx === k) b.classList.add('no'); });
    const t = box.querySelector('.g-timer'); if (t) t.style.display = 'none';
    const over = st.i + 1 >= st.qs.length;
    const fb = box.querySelector('.g-feedback');
    fb.innerHTML = (k === q.ok ? '✅ Верно! ' : (k === null ? '⏰ Время вышло. ' : '❌ Не совсем. ')) + esc(q.why || '') +
      '<div style="margin-top:12px"><button class="g-btn main" id="next">' + (over ? 'К итогам 🏆' : 'Дальше →') + '</button></div>';
    box.querySelector('#next').onclick = () => { st.i++; teamQuestion(); };
  }
  function teamEnd() {
    clearTimers();
    const [a, b] = st.score, win = a === b ? -1 : (a > b ? 0 : 1);
    const title = win < 0 ? 'Ничья! Победила дружба 🤝' : 'Победила команда «' + esc(st.names[win]) + '»! 🎉';
    frame('<h2>' + title + '</h2><div class="g-trophy">' + (win < 0 ? '🤝' : '🏆') + '</div>' + scoreboard() +
      '<div><button class="g-btn main" id="again">🔁 Сыграть ещё раз</button><button class="g-btn" id="stop">Закрыть</button></div>');
    bindScoreboard();
    box.querySelector('#again').onclick = teamSetup; box.querySelector('#stop').onclick = close;
  }
})();
"""
