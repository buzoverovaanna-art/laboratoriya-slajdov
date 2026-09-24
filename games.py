# -*- coding: utf-8 -*-
"""Данные для игры «Игра для класса»: собираются из готовой презентации и добавляют слайд «Игровая зона».

Вопросы пишет ИИ (ai.make_quiz), а код оставляет только те, у которых есть цитата-доказательство
из текста презентации.

Сама игра (что видит и нажимает класс) — в styles/games_ui.py.
"""
import random
import re

GAME_NAMES = {"team": "Игра для класса"}
META = re.compile(r"(презентаци|слайд|в тексте|по тексту|текст пр|рассказ|сказано|автор)", re.I)


def _norm(s):
    return " ".join(re.sub(r"[^\w]+", " ", str(s).lower().replace("ё", "е")).split())


def deck_text(deck):
    """Весь текст презентации одной строкой — по нему составляются вопросы и проверяются цитаты-доказательства."""
    parts = []
    for s in deck.get("slides", []):
        if s.get("type") == "games":
            continue
        # На титульном слайде «author» — имя ученицы: в ИИ и в вопросы оно не попадает никогда.
        keys = ("title", "subtitle", "notes") if s.get("type") == "title" else ("title", "subtitle", "value", "caption", "text", "author", "center", "notes")
        for key in keys:
            if s.get(key):
                parts.append(str(s[key]))
        for key in ("bullets", "nodes", "facts"):
            parts += [str(x) for x in s.get(key, []) if x]
        parts += [f"{x.get('when', '')} {x.get('text', '')}" for x in s.get("steps", [])]
        for side in ("left", "right"):
            if s.get(side):
                parts.append(str(s[side].get("name", "")))
                parts += [str(x) for x in s[side].get("points", [])]
    return "\n".join(p for p in parts if p.strip())


# ------------------------------------------------------------------ «Игра для класса»
def validate_quiz(raw, text, seed=None):
    """Оставляет только правильно составленные вопросы, у которых цитата-доказательство есть в тексте презентации."""
    rng = random.Random(seed)
    base = _norm(text)
    out = []
    for q in (raw or {}).get("questions", []):
        try:
            question = " ".join(str(q["question"]).split())
            options = [" ".join(str(o).split()) for o in q["options"]]
            idx = int(q["correct_index"])
            evidence = " ".join(str(q.get("evidence", "")).split())
            why = " ".join(str(q.get("explanation", "")).split())
        except (KeyError, TypeError, ValueError):
            continue
        if len(options) != 4 or not (0 <= idx < 4) or not question or len(question) > 200:
            continue
        if len({_norm(o) for o in options}) != 4 or not all(0 < len(o) <= 90 for o in options):
            continue
        if re.search(r"(все вышеперечисленное|ничего из перечисленного|все ответы верны)", " ".join(options).lower()):
            continue
        if len(_norm(evidence)) < 12 or _norm(evidence) not in base:  # доказательство должно быть в презентации
            continue
        if META.search(question):  # вопрос не должен ссылаться на «презентацию» или «текст»
            continue
        if META.search(why):
            why = f"Верный ответ: {options[idx]}."
        order = list(range(4))
        rng.shuffle(order)  # верный ответ не всегда под одной буквой
        out.append({"question": question, "options": [options[k] for k in order], "correct": order.index(idx), "explanation": why[:220]})
    return out


# ------------------------------------------------------------------ добавление игры в презентацию
def _set_games_slide(deck, failed):
    slides = [s for s in deck["slides"] if s.get("type") != "games"]
    available = [g for g in ("team",) if g in deck.get("games", {})]
    if not available and not failed:
        deck["slides"] = slides
        return
    games_slide = {"type": "games", "title": "Игровая зона", "available": available, "failed": failed,
                   "notes": "Здесь можно сыграть по теме презентации: разбить класс на 2 команды и проверить, что запомнили."}
    deck["slides"] = slides[:-1] + [games_slide] + slides[-1:]  # перед слайдом «Выводы», он остаётся последним


def add_games(deck, wanted, quiz_maker=None):
    """Добавляет игру, если она нужна. Возвращает словарь {игра: причина}, если не получилось (презентация при этом целая)."""
    deck.setdefault("games", {})
    failed = {}
    for game in wanted:
        if game == "team":
            try:
                if quiz_maker is None:
                    raise ValueError("ИИ не подключён")
                questions = quiz_maker(deck)
                deck["games"]["team"] = {"questions": questions}
            except Exception as e:  # игра не получилась — презентация всё равно остаётся
                failed["team"] = str(e) or "не получилось составить вопросы"
    deck["games_failed"] = failed
    _set_games_slide(deck, [GAME_NAMES[g] for g in failed])
    return failed
