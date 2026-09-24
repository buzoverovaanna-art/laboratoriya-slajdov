# -*- coding: utf-8 -*-
"""Приложение «Лаборатория слайдов»: главный экран, создание, полка «мои работы».

Запуск:  .venv/bin/python app.py
Открывается на компьютере и на планшете по домашнему Wi-Fi.
"""
import json
import os
import socket
import subprocess
import tempfile

from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory

import ai
import extract
import games
import generator
import pdf

APP_NAME = "Лаборатория слайдов"
PORT = 5050  # не 5000: этот порт на Mac занимает AirPlay
MAX_TOPIC = 120
MAX_TEXT = 40000  # около 15 страниц
MAX_FILES = 20
MAX_FILE_MB = 25
HERE = os.path.dirname(os.path.abspath(__file__))

SUBJECTS = ["История", "Обществознание", "География", "Биология", "Литература", "Русский язык",
            "Физика", "Химия", "Математика", "Английский язык"]
MAX_SUBJECT = 40

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # все файлы за раз

# Карточки стилей. «Готов» = у стиля есть оформитель в generator.STYLES.
CARDS = [
    {"id": "harry", "name": "Harry Potter", "emoji": "🕯️",
     "tagline": "В стиле фильма: старый пергамент, золото, свет свечи."},
    {"id": "genshin", "name": "Genshin Impact", "emoji": "🔮",
     "tagline": "В стиле игры: золото, ночное небо, значки стихий."},
    {"id": "brawl", "name": "Brawl Stars", "emoji": "🏆",
     "tagline": "В стиле игры: яркие цвета, толстые контуры, крупные надписи."},
    {"id": "business", "name": "Business", "emoji": "💼",
     "tagline": "Чётко и по-деловому: строгие цвета, ничего лишнего."},
]

BACK_BUTTON = (
    '<a href="/" onclick="event.stopPropagation()" style="position:fixed;top:12px;left:12px;'
    "z-index:99999;padding:10px 16px;border-radius:999px;background:rgba(20,16,40,.72);"
    "color:#fff;font:600 15px -apple-system,system-ui,sans-serif;text-decoration:none;"
    'backdrop-filter:blur(6px)">← к работам</a>'
)


def load_students():
    """Ученицы лежат в students.json (он только на этом компьютере, в GitHub не попадает).
    Нет файла — берём students.example.json с придуманными именами."""
    for name in ("students.json", "students.example.json"):
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return []


def author_line(st):
    fio = " ".join(x for x in (st["surname"], st["name"], st.get("patronymic", "")) if x)
    return f"{fio}, {st['class']}" if st.get("class") else fio


def cards():
    return [dict(c, ready=c["id"] in generator.STYLES) for c in CARDS]


def _grade_of(student):
    c = student.get("class", "")
    return c[:1] if c[:1].isdigit() else c


def render_plan(outline, form, error=None):
    """Экран-подтверждение плана: заголовки будущих слайдов, можно поправить перед полной генерацией."""
    return render_template("index.html", app_name=APP_NAME, plan=outline, f=form, error=error)


def render_index(error=None, form=None, status=200):
    form = form or {}
    works = generator.list_works()
    for w in works:  # «＋ Игра» и «↻ Слайд» доступны только у работ с сохранёнными данными
        deck = generator.load_deck(w["id"])
        w["can_add"] = deck is not None
        w["middle_slides"] = [(i, s.get("title") or f"Слайд {i + 1}") for i, s in enumerate(deck["slides"])][1:-1] \
            if deck and len(deck["slides"]) > 2 else []
    page = render_template(
        "index.html", app_name=APP_NAME,
        cards=cards(), students=load_students(), subjects=SUBJECTS, works=works,
        games_checked=form.get("games", []), error=error, f=form, selected=form.get("style", "business"),
        slides=form.get("slides", 8), source=form.get("source", "topic"),
        ai_ready=ai.ai_ready(), ai_name={"gigachat": "GigaChat", "claude": "Claude"}.get(ai.provider()), min_slides=generator.MIN_SLIDES, max_slides=generator.MAX_SLIDES,
    )
    return page, status


@app.get("/")
def index():
    return render_index()


@app.get("/create")
def create_reload():
    """Пока презентация создаётся, в адресе браузера — /create. Если в этот момент обновить
    страницу, вместо пугающей ошибки просто возвращаем на главную."""
    return redirect("/")


@app.post("/create")
def create():
    form = {k: " ".join(request.form.get(k, "").split()) for k in
            ("student", "source", "topic", "subject", "subject_other", "style", "slides")}
    form["text"] = request.form.get("text", "").strip()
    form["games"] = [g for g in request.form.getlist("games") if g in games.GAME_NAMES]

    def fail(msg):
        return render_index(msg, form, 400)

    student = next((s for s in load_students() if s["id"] == form["student"]), None)
    if not student:
        return fail("Выбери, кто делает презентацию.")
    subject = form["subject_other"] if form["subject"] == "__other" else form["subject"]
    if not subject:
        return fail("Выбери предмет или впиши свой.")
    if len(subject) > MAX_SUBJECT:
        return fail(f"Название предмета слишком длинное — не больше {MAX_SUBJECT} знаков.")
    mode = form["source"] if form["source"] in ("topic", "text") else "topic"
    form["source"] = mode
    try:
        count = int(form["slides"])
    except ValueError:
        count = 8
    count = max(generator.MIN_SLIDES, min(generator.MAX_SLIDES, count))
    form["slides"] = count
    if form["style"] not in generator.STYLES:
        return fail("Выбери стиль из готовых карточек.")

    topic, source = form["topic"], {"mode": mode}
    if mode == "text":
        if len(form["text"]) < 40:
            return fail("Вставь текст параграфа — хотя бы несколько предложений.")
        if len(form["text"]) > MAX_TEXT:
            return fail(f"Текст слишком длинный — не больше {MAX_TEXT} знаков (около 15 страниц). Вставь его частями.")
        source["text"] = form["text"]
        if not topic:
            return fail("Напиши тему — о чём этот текст.")
    elif not topic:
        return fail("Напиши тему — о чём будет презентация.")
    if len(topic) > MAX_TOPIC:
        return fail(f"Тема слишком длинная — не больше {MAX_TOPIC} знаков.")

    def demo_redirect():  # без ИИ или если ИИ не ответил — не бросаем ученицу ни с чем, даём заготовку
        deck = generator.build_deck(topic, form["style"], count, author_line(student), source, subject)
        if form["games"]:
            games.add_games(deck, form["games"], None)
        meta = generator.save_work(deck)
        return redirect(f"/w/{meta['file']}")

    if not ai.ai_ready():
        return demo_redirect()

    form["subject"] = subject  # предмет уже определён (мог быть «свой вариант») — несём его дальше как есть
    try:
        outline = ai.make_outline(topic, form["style"], count, subject, source, _grade_of(student))
    except ai.AIError:
        return demo_redirect()
    return render_plan(outline, form)


@app.post("/create/confirm")
def create_confirm():
    """Шаг 2: ученица одобрила (или поправила) план — теперь пишем презентацию целиком."""
    form = {k: " ".join(request.form.get(k, "").split()) for k in
            ("student", "source", "topic", "subject", "style", "slides")}
    form["text"] = request.form.get("text", "").strip()
    form["games"] = [g for g in request.form.getlist("games") if g in games.GAME_NAMES]

    student = next((s for s in load_students() if s["id"] == form["student"]), None)
    topic, subject = form["topic"], form["subject"]
    if not student or not subject or not topic or form["style"] not in generator.STYLES:
        return redirect("/")  # план потерялся (например, страницу открыли заново) — начинаем сначала
    mode = form["source"] if form["source"] in ("topic", "text") else "topic"
    try:
        count = int(form["slides"])
    except ValueError:
        count = 8
    count = max(generator.MIN_SLIDES, min(generator.MAX_SLIDES, count))
    source = {"mode": mode}
    if mode == "text":
        source["text"] = form["text"]

    material_text = request.form.get("material", "").strip()
    material_override = {"material": material_text, "sources": request.form.getlist("material_sources")} if material_text else None
    outline = {
        "title": " ".join(request.form.get("plan_title", "").split()) or topic,
        "subtitle": " ".join(request.form.get("plan_subtitle", "").split()),
        "slides": [t for t in (" ".join(x.split()) for x in request.form.getlist("plan_slide")) if t],
    }

    def demo_redirect():
        deck = generator.build_deck(topic, form["style"], count, author_line(student), source, subject)
        if form["games"]:
            games.add_games(deck, form["games"], None)
        meta = generator.save_work(deck)
        return redirect(f"/w/{meta['file']}")

    try:
        deck = ai.make_deck(topic, form["style"], count, author_line(student), source, subject, _grade_of(student),
                             material_override=material_override, outline=outline)
    except ai.AIError:
        return demo_redirect()
    if form["games"]:
        games.add_games(deck, form["games"], ai.make_quiz if ai.ai_ready() else None)
    meta = generator.save_work(deck)
    return redirect(f"/w/{meta['file']}")


@app.post("/works/<work_id>/regenerate")
def regenerate_work_slide(work_id):
    """«↻ Слайд» на полке работ: переписывает один средний слайд, без пересоздания всей презентации."""
    deck = generator.load_deck(work_id)
    if deck is None:
        abort(404)
    try:
        index = int(request.form.get("slide", ""))
    except ValueError:
        index = -1
    try:
        deck = ai.regenerate_slide(deck, index)
    except ai.AIError as e:
        return render_index(str(e), None, 400)
    meta = generator.update_work(work_id, deck)
    return redirect(f"/w/{meta['file']}#{index + 1}")


@app.post("/games/<work_id>")
def add_game(work_id):
    """Кнопка «＋ Игра» у готовой работы: добавляет игру и перезаписывает презентацию."""
    deck = generator.load_deck(work_id)
    meta = next((w for w in generator.list_works() if w["id"] == work_id), None)
    if deck is None or meta is None:
        abort(404)
    wanted = [g for g in request.form.getlist("game") if g in games.GAME_NAMES]
    have = [g for g in ("team",) if g in deck.get("games", {})]
    games.add_games(deck, have + [g for g in wanted if g not in have], ai.make_quiz if ai.ai_ready() else None)
    meta = generator.update_work(work_id, deck)
    at = next((i + 1 for i, s in enumerate(deck["slides"]) if s.get("type") == "games"), 1)
    return redirect(f"/w/{meta['file']}#{at}")


@app.post("/delete/<work_id>")
def delete_work(work_id):
    """Удаление старой презентации (кнопка с подтверждением на главной странице)."""
    if not generator.delete_work(work_id):
        abort(404)
    return redirect("/")


@app.post("/extract")
def extract_route():
    """Плюсик в режиме «Вставлю текст сама»: достаёт текст из фото и файлов. Файлы сразу удаляются."""
    files = request.files.getlist("files")[:MAX_FILES]
    parts, report = [], []
    for f in files:
        name = os.path.basename(f.filename or "файл")
        try:
            with tempfile.TemporaryDirectory() as tmp:  # сохраняется на секунду, потом удаляется
                path = os.path.join(tmp, "in" + os.path.splitext(name)[1].lower())
                f.save(path)
                if os.path.getsize(path) > MAX_FILE_MB * 1024 * 1024:
                    raise extract.ExtractError(f"Файл больше {MAX_FILE_MB} МБ. Выбери поменьше.")
                text = extract.extract_file(path, name)
            parts.append(text)
            report.append({"name": name, "chars": len(text)})
        except extract.ExtractError as e:
            report.append({"name": name, "error": str(e)})
        except Exception as e:  # не роняем страницу из-за одного файла
            print(f"[файлы] {name}: {type(e).__name__}: {e}")
            report.append({"name": name, "error": "Не получилось прочитать этот файл."})
    return jsonify(text="\n\n".join(parts), files=report)


@app.errorhandler(413)
def too_large(_):
    return jsonify(text="", files=[{"name": "файлы", "error": "Слишком много данных за один раз. Добавь файлы по частям."}]), 413


@app.get("/w/<path:filename>")
def show_work(filename):
    """Отдаёт презентацию, добавляя кнопку «← к работам» (сам файл на диске не меняется)."""
    if os.path.basename(filename) != filename or not filename.endswith(".html"):
        abort(404)
    path = os.path.join(generator.WORKS_DIR, filename)
    if not os.path.isfile(path):
        abort(404)
    with open(path, encoding="utf-8") as f:
        html = f.read()
    html = html.replace("</body>", BACK_BUTTON + "</body>", 1) if "</body>" in html else html + BACK_BUTTON
    return html


@app.get("/dl/<path:filename>")
def download_work(filename):
    """Отдаёт презентацию как файл для скачивания (не для просмотра): один HTML-файл,
    внутри уже все картинки и стили — на компьютере учителя откроется без интернета и без сервера."""
    if os.path.basename(filename) != filename or not filename.endswith(".html"):
        abort(404)
    if not os.path.isfile(os.path.join(generator.WORKS_DIR, filename)):
        abort(404)
    return send_from_directory(generator.WORKS_DIR, filename, as_attachment=True)


@app.get("/pdf/<path:filename>")
def pdf_work(filename):
    """PDF презентации — для сдачи учителю. Собирается при первом нажатии (до минуты) и запоминается."""
    if os.path.basename(filename) != filename or not filename.endswith(".html"):
        abort(404)
    html_path = os.path.join(generator.WORKS_DIR, filename)
    if not os.path.isfile(html_path):
        abort(404)
    pdf_name = filename[:-len(".html")] + ".pdf"
    pdf_path = os.path.join(generator.WORKS_DIR, pdf_name)
    if not os.path.isfile(pdf_path) or os.path.getmtime(pdf_path) < os.path.getmtime(html_path):
        if not pdf.make_pdf(html_path, pdf_path):
            return "Не получилось собрать PDF. Для него нужен браузер Google Chrome на этом компьютере.", 500
    return send_from_directory(generator.WORKS_DIR, pdf_name, as_attachment=True)


@app.get("/manifest.webmanifest")
def manifest():
    data = {
        "name": APP_NAME,
        "short_name": "Лаборатория",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f4f8f1",
        "theme_color": "#b9d8ad",
        "lang": "ru",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    resp = jsonify(data)
    resp.mimetype = "application/manifest+json"
    return resp


def wifi_address():
    """Адрес Mac в домашней сети.

    Сначала спрашиваем у macOS про Wi-Fi (en0/en1): при включённом VPN
    запасной способ ниже возвращает адрес VPN, а он планшету не подходит.
    """
    for iface in ("en0", "en1"):
        try:
            ip = subprocess.run(["ipconfig", "getifaddr", iface], capture_output=True,
                                text=True, timeout=3).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            ip = ""
        if ip:
            return ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


if __name__ == "__main__":
    ip = wifi_address()
    print(f"\n  {APP_NAME} запущена.")
    print(f"  На этом компьютере:  http://localhost:{PORT}")
    if ip:
        print(f"  На планшете (тот же Wi-Fi):  http://{ip}:{PORT}")
    print("  Остановить: Ctrl+C\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
