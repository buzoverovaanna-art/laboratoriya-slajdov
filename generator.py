# -*- coding: utf-8 -*-
"""Генератор презентаций «Презентации».

Пока работает в демо-режиме: структура слайдов собирается по шаблону.
После подключения API Claude тексты будет писать ИИ-сценарист —
для этого достаточно заменить функцию build_deck.
"""
import json
import os
import re
import time

from styles.brawl import render as render_brawl
from styles.business import render as render_business
from styles.genshin import render as render_genshin
from styles.harry import render as render_harry
from styles.memeshow import render as render_memeshow
from styles.terminal import render as render_terminal
from styles.toca import render as render_toca

# Стили на общем движке (паспорт + раскладки) — доступны на главном экране.
STYLES = {
    "harry": {"name": "Harry Potter", "render": render_harry},
    "genshin": {"name": "Genshin Impact", "render": render_genshin},
    "brawl": {"name": "Brawl Stars", "render": render_brawl},
    "business": {"name": "Business", "render": render_business},
}

# Запасные стили: в приложении не показываются, но остались рабочими —
# «Toca Boca» сняли с полки 22.09.2026 (Анна и дочки: слишком по-детски), доигрывают старые задачи «Мем-шоу»/«Терминал».
LEGACY_STYLES = {
    "toca": {"name": "Toca Boca", "render": render_toca},
    "memeshow": {"name": "Мем-шоу", "render": render_memeshow},
    "terminal": {"name": "Терминал", "render": render_terminal},
}

WORKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "works")


MIN_SLIDES, MAX_SLIDES = 3, 20


def _middle_slide(kind: str, n: int, i: int, topic: str) -> dict:
    """Один слайд-заготовка. n — номер слайда, i — какой раз встречается эта раскладка."""
    part = "" if i == 1 else f" (часть {i})"
    if kind == "scheme":
        return {"type": "scheme", "title": f"Про «{topic}» важно понять три вещи{part}", "center": topic,
                "nodes": ["Причины — с чего всё началось", "Ход событий — что происходило", "Итоги — к чему пришло"], "facts": [FACT] * 3}
    if kind == "timeline":
        return {"type": "timeline", "title": f"Всё происходило по шагам{part}",
                "steps": [{"when": "Шаг 1", "text": "С чего всё началось"}, {"when": "Шаг 2", "text": "Что накалило обстановку"},
                          {"when": "Шаг 3", "text": "Главное событие"}, {"when": "Шаг 4", "text": "К чему это привело"}], "facts": [FACT] * 4}
    if kind == "compare":
        return {"type": "compare", "title": f"У этой темы две стороны{part}",
                "left": {"name": "За", "points": ["Первый довод — самый сильный", "Второй довод — с примером"]},
                "right": {"name": "Против", "points": ["Первое возражение", "Второе возражение — с примером"]}}
    if kind == "bignum":
        return {"type": "bignum", "title": f"Одна цифра, которую запомнят{part}", "value": "≈ 3",
                "caption": "Пример: здесь будет главная цифра доклада. Настоящие цифры ИИ добавит с пометкой «проверь по учебнику»."}
    if kind == "quote":
        return {"type": "quote", "text": "Здесь будет короткая цитата по теме", "author": "Автор цитаты · пример"}
    return {"type": "cards", "title": f"Ключевые факты{part}",
            "bullets": ["Первый факт — самый важный", "Второй факт — с датой или примером", "Третий факт — который удивит"], "facts": [FACT] * 3}


FACT = "Пример: здесь будет интересный факт по теме. ИИ найдёт его и проверит по учебнику."

LAYOUT_CYCLE = ["scheme", "timeline", "compare", "bignum", "quote", "cards"]


def build_deck(topic: str, style: str, slides: int = 8, author: str = "", source: dict = None, subject: str = "") -> dict:
    """Сценарист: строит структуру слайдов по теме.

    Демо-режим: каркас доклада с честной пометкой, что тексты напишет ИИ.
    Слайдов ровно `slides` (от 3 до 20): титульный, середина по кругу из всех
    раскладок, последний «Выводы». Позже здесь будет вызов API Claude — по правилам:
    заголовки-выводы, факты только проверяемые. `source` — откуда брать материал:
    {"mode": "topic" | "text", ...}; сейчас только запоминается.
    """
    slides = max(MIN_SLIDES, min(MAX_SLIDES, int(slides)))
    source = source or {"mode": "topic"}
    seen = {}
    middle = []
    for k in range(slides - 2):
        kind = LAYOUT_CYCLE[k % len(LAYOUT_CYCLE)]
        seen[kind] = seen.get(kind, 0) + 1
        middle.append(_middle_slide(kind, k + 2, seen[kind], topic))
    note = "демо-режим: тексты напишет ИИ"
    if source["mode"] == "text":
        note += " по вставленному тексту"
    return {
        "topic": topic, "style": style, "demo": True, "demo_note": note, "source": source, "author": author, "subject": subject,
        "slides": (
            [{"type": "title", "title": topic, "subtitle": "доклад, после которого аплодируют", "author": author, "subject": subject}]
            + middle
            + [{"type": "cards", "title": "Выводы", "cover_echo": True, "subject": subject,
                "bullets": ["Главное: что нужно запомнить", "Почему это важно для нас", "Вопрос, который стоит обсудить"]}]
        ),
    }


def flatten(deck: dict) -> dict:
    """Для запасных стилей: превращает любые раскладки в «заголовок + список»."""
    slides = []
    for s in deck["slides"]:
        kind = s["type"]
        if kind in ("title", "outro"):
            slides.append(s)
            continue
        title = s.get("title", "")
        if kind in ("cards", "content"):
            bullets = s["bullets"]
        elif kind == "timeline":
            bullets = [f"{x['when']}: {x['text']}" for x in s["steps"]]
        elif kind == "compare":
            bullets = [f"{s['left']['name']}: {x}" for x in s["left"]["points"]] + \
                      [f"{s['right']['name']}: {x}" for x in s["right"]["points"]]
        elif kind == "bignum":
            bullets = [s["value"], s["caption"]]
        elif kind == "quote":
            title, bullets = "Цитата", [s["text"], s["author"]]
        else:  # scheme
            bullets = [s["center"]] + s["nodes"]
        slides.append({"type": "content", "title": title, "emoji": "✨", "bullets": bullets})
    return dict(deck, slides=slides)


def slugify(text: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9а-яё-]+", "-", text.lower()).strip("-"))[:40] or "prezentaciya"


def save_work(deck: dict) -> dict:
    """Оформитель: собирает HTML выбранного стиля и записывает файл работы."""
    if deck["style"] in STYLES:
        style, html = STYLES[deck["style"]], STYLES[deck["style"]]["render"](deck)
    else:
        style = LEGACY_STYLES[deck["style"]]
        html = style["render"](flatten(deck))

    os.makedirs(WORKS_DIR, exist_ok=True)
    work_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{slugify(deck['topic'])}"
    filename = f"{work_id}.html"
    with open(os.path.join(WORKS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(html)

    with open(os.path.join(WORKS_DIR, f"{work_id}.json"), "w", encoding="utf-8") as f:  # данные презентации — для «＋ Игра»
        json.dump(deck, f, ensure_ascii=False)
    meta = {
        "id": work_id,
        "file": filename,
        "topic": deck["topic"],
        "style": deck["style"],
        "style_name": style["name"],
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "slides": len(deck["slides"]),
        "author": deck.get("author", ""),
        "subject": deck.get("subject", ""),
        "games": [gm for gm in ("team",) if gm in deck.get("games", {})],
    }
    index_path = os.path.join(WORKS_DIR, "index.json")
    index = []
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)
    index.insert(0, meta)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return meta


def list_works() -> list:
    index_path = os.path.join(WORKS_DIR, "index.json")
    if not os.path.exists(index_path):
        return []
    with open(index_path, encoding="utf-8") as f:
        return json.load(f)


def delete_work(work_id: str) -> bool:
    """Удаляет работу: файл презентации и запись в списке. Возвращает False, если такой работы нет.

    Путь к файлу берётся из нашего списка, а не из запроса, поэтому удалить чужой файл нельзя.
    """
    index = list_works()
    work = next((w for w in index if w["id"] == work_id), None)
    if work is None:
        return False
    path = os.path.join(WORKS_DIR, os.path.basename(work["file"]))
    if os.path.isfile(path):
        os.remove(path)
    data_path = os.path.join(WORKS_DIR, f"{work_id}.json")
    if os.path.isfile(data_path):
        os.remove(data_path)
    pdf_path = os.path.join(WORKS_DIR, f"{work_id}.pdf")
    if os.path.isfile(pdf_path):
        os.remove(pdf_path)
    with open(os.path.join(WORKS_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump([w for w in index if w["id"] != work_id], f, ensure_ascii=False, indent=2)
    return True


def load_deck(work_id: str):
    """Данные презентации (для добавления игр). None, если у старой работы их нет."""
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[\w-]*", work_id or ""):
        return None
    path = os.path.join(WORKS_DIR, f"{work_id}.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def update_work(work_id: str, deck: dict) -> dict:
    """Перезаписывает презентацию (например, после добавления игры) и обновляет запись в списке."""
    index = list_works()
    meta = next(w for w in index if w["id"] == work_id)
    style = STYLES.get(deck["style"]) or LEGACY_STYLES[deck["style"]]
    html = style["render"](deck if deck["style"] in STYLES else flatten(deck))
    with open(os.path.join(WORKS_DIR, meta["file"]), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(WORKS_DIR, f"{work_id}.json"), "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False)
    meta["slides"] = len(deck["slides"])
    meta["games"] = [gm for gm in ("team",) if gm in deck.get("games", {})]
    with open(os.path.join(WORKS_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return meta
