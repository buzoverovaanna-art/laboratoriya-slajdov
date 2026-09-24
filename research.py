# -*- coding: utf-8 -*-
"""Поиск материала по всему интернету для режима «Своя тема».

Как работает: ищем через Google (сервис Serper), отсеиваем «мусорные» сайты (ГДЗ и решебники, видео, соцсети,
магазины, азартные игры, взрослые сайты), читаем текст 2–4 подходящих страниц и отдаём Сценаристу как <material>.
Надёжные сайты (Википедия, энциклопедии, РЭШ, образовательные порталы) стоят в выдаче выше, но не обязательны.
Цитаты и цифры потом проверяются по этому тексту (ai.py), а на слайде «Выводы» стоят реальные ссылки.

Ключ Serper лежит в ~/.config/klyuchi-zakrytye/serper.key. Нет ключа или ничего не нашлось —
презентация делается «по знаниям ИИ» с пометкой «проверь по учебнику».
"""
import ipaddress
import os
import re
import time
from urllib.parse import unquote, urlparse

import httpx

SERPER_KEY_FILE = os.path.expanduser("~/.config/klyuchi-zakrytye/serper.key")
UA = {"User-Agent": "LaboratoriaSlaydov/1.0 (family school project; reads articles for presentations)"}  # заголовок только латиницей
MAX_SOURCES = 4        # сколько страниц читаем
MAX_PER_HOST = 2       # не больше двух с одного сайта
MAX_PER_SOURCE = 6000  # знаков с одной страницы
TIME_BUDGET = 45       # секунд на всё чтение
TAIL_SECTIONS = {"См. также", "Примечания", "Литература", "Ссылки", "Источники", "Комментарии", "Библиография"}

# Сайты, которым доверяем больше: стоят выше в выдаче
PREFERRED = ["ru.wikipedia.org", "bigenc.ru", "resh.edu.ru", "histrf.ru", "history.ru", "arzamas.academy", "school-collection.edu.ru",
             "interneturok.ru", "foxford.ru", "postnauka.ru", "nauka.tass.ru", "gramota.ru", "krugosvet.ru"]
# Сайты, которые не берём никогда: видео, соцсети, магазины, ответы на задания, чужие книги, форумы
BLOCKED = ["youtube.com", "youtu.be", "rutube.ru", "vk.com", "vkvideo.ru", "ok.ru", "dzen.ru", "t.me", "facebook.com", "instagram.com",
           "tiktok.com", "pinterest.com", "twitter.com", "x.com", "litres.ru", "ozon.ru", "wildberries.ru", "avito.ru", "market.yandex.ru",
           "otvet.mail.ru", "yandex.ru", "google.com", "mail.ru", "pikabu.ru", "livejournal.com", "wiki2.org"]
BLOCKED_PARTS = ["gdz", "reshebnik", "resheba", "reshak", "spishy", "spishi", "megaresh", "gotovye", "otvety", "referat", "kursovik",
                 "diplom", "bestreferat", "sochinenie", "porn", "xxx", "sex", "casino", "kazino", "1xbet", "vulkan", "slot", "poker"]
# Страницы, где нет пересказа темы: тесты, викторины, сценарии уроков, готовые презентации, видео
TITLE_SKIP = re.compile(r"(^|\s)(тест|тесты|викторина|кроссворд|сценарий|сценарии|контрольная|презентация|видеоурок|видео)(\s|:|$)|тест по|тест на тему|вопросы$", re.I)
BAD_WORDS = re.compile(r"(порно|секс|эротик|казино|ставки на спорт|интим|18\+|ГДЗ|решебник|готовые домашние)", re.I)


def serper_key():
    if os.path.isfile(SERPER_KEY_FILE):
        with open(SERPER_KEY_FILE, encoding="utf-8") as f:
            return f.read().strip()
    return ""


def _host(url):
    return (urlparse(url).hostname or "").lower()


def _in(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


def _allowed(url, title=""):
    """Можно ли читать эту страницу: обычный сайт, не мусорный, не файл и не адрес внутри домашней сети."""
    p = urlparse(url)
    host = _host(url)
    if p.scheme not in ("http", "https") or not host or "." not in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False  # голые IP-адреса (в том числе домашняя сеть) не открываем
    except ValueError:
        pass
    if _in(host, BLOCKED) or any(part in host for part in BLOCKED_PARTS):
        return False
    if re.search(r"\.(pdf|docx?|pptx?|xlsx?|zip|rar|mp3|mp4|jpg|png)$", p.path.lower()):
        return False
    return not BAD_WORDS.search(unquote(url) + " " + title) and not TITLE_SKIP.search(title)


def blocked_host(url):
    """Тот же список запрещённых сайтов, что и для чтения статей — пригождается и для картинок (images.py)."""
    host = _host(url)
    return not host or _in(host, BLOCKED) or any(part in host for part in BLOCKED_PARTS)


def _rank(url):
    host = _host(url)
    if _in(host, PREFERRED):
        return 0
    if host.endswith(".edu.ru") or ".edu." in host or host.endswith(".gov.ru"):
        return 1
    return 2


def _serper(q, key):
    r = httpx.post("https://google.serper.dev/search", headers={"X-API-KEY": key},
                   json={"q": q, "gl": "ru", "hl": "ru", "num": 15}, timeout=20)
    r.raise_for_status()
    return [(x["link"], x.get("title", "")) for x in r.json().get("organic", [])]


def search(topic, subject, grade):
    """Список (адрес, заголовок): сначала надёжные сайты, потом остальные. Пусто, если поиск недоступен.

    Два запроса: по всему интернету и отдельно по энциклопедиям, чтобы хорошая статья не потерялась среди школьных порталов.
    """
    key = serper_key()
    if not key:
        return []
    base = f"{topic} {subject} {grade + ' класс' if grade else ''}".replace("  ", " ")
    queries = [f"{base} -ГДЗ -решебник -реферат -скачать", f"{topic} Википедия"]  # оператор site: бесплатный Serper не принимает
    found = []
    for q in queries:
        try:
            found += _serper(q, key)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            print(f"[поиск] запрос не получился: {type(e).__name__}", flush=True)
    seen, out = set(), []
    for url, title in found:
        clean = url.split("#")[0]
        if clean not in seen and _allowed(clean, title):
            seen.add(clean)
            out.append((clean, title))
    out.sort(key=lambda x: _rank(x[0]))  # сортировка устойчивая: порядок Google внутри групп сохраняется
    return out


def _trim(text, limit):
    """Обрезает по границе абзаца, чтобы не рвать мысль."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    k = cut.rfind("\n")
    return (cut[:k] if k > limit * 0.6 else cut).strip()


def _wiki_text(url):
    title = unquote(urlparse(url).path.split("/wiki/", 1)[-1]).replace("_", " ")
    r = httpx.get("https://ru.wikipedia.org/w/api.php", headers=UA, timeout=20, params={
        "action": "query", "prop": "extracts", "explaintext": 1, "redirects": 1, "format": "json", "titles": title})
    r.raise_for_status()
    page = next(iter(r.json()["query"]["pages"].values()))
    out = []
    for line in page.get("extract", "").split("\n"):
        if line.strip("= ").strip() in TAIL_SECTIONS and out:
            break
        out.append(re.sub(r"={2,}\s*(.+?)\s*={2,}", r"\1", line))
    return "\n".join(out)


def _page_text(url):
    from bs4 import BeautifulSoup
    r = httpx.get(url, headers=UA, timeout=20, follow_redirects=True)
    r.raise_for_status()
    if "html" not in r.headers.get("content-type", "html"):
        raise ValueError("не страница")
    soup = BeautifulSoup(r.content, "html.parser")  # сам определяет кодировку (в том числе windows-1251)
    for bad in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "iframe"]):
        bad.decompose()
    root = soup.find("article") or soup.find("main") or soup.body or soup
    parts = []
    for el in root.find_all(["h2", "h3", "p"]):
        t = " ".join(el.get_text(" ").split())
        if el.name == "p" and len(t) < 60:
            continue
        if t:
            parts.append(t)
    return "\n".join(parts)


def _read(url):
    return _wiki_text(url) if _host(url).endswith("ru.wikipedia.org") and "/wiki/" in url else _page_text(url)


def _russian(text):
    """Текст должен быть по-русски: не меньше 60% букв — кириллица."""
    letters = re.findall(r"[A-Za-zА-Яа-яЁё]", text)
    return bool(letters) and len(re.findall(r"[А-Яа-яЁё]", text)) / len(letters) >= 0.6


def _stems(text):
    """Корни значимых слов (первые 5 букв), чтобы «Фотосинтез» находил «фотосинтеза»."""
    return {w[:5] for w in re.findall(r"[а-яёa-z]{4,}", text.lower())}


def _related(text, topic):
    return bool(_stems(text) & _stems(topic))


def _clean_title(title):
    title = re.sub(r"\s*[-—–|•]\s*[^-—–|•]{2,40}$", "", title).strip() if len(title) > 60 else title
    return re.sub(r"\s*[-—–|]\s*(Википедия|БРЭ.*|Arzamas|Рувики).*$", "", title).strip() or title


def find_material(topic, subject, grade):
    """Ищет и читает страницы. Возвращает {'material': текст с пометками об источниках, 'sources': [«Название — адрес»]} или None."""
    hits = search(topic, subject, grade)
    chunks, sources, per_host, t0 = [], [], {}, time.time()
    for url, title in hits:
        if len(chunks) >= MAX_SOURCES or time.time() - t0 > TIME_BUDGET:
            break
        host = _host(url)
        if per_host.get(host, 0) >= MAX_PER_HOST:
            continue
        try:
            text = _trim(_read(url), MAX_PER_SOURCE)
        except Exception as e:
            print(f"[поиск] не прочитала {url[:60]}: {type(e).__name__}", flush=True)
            continue
        if len(text) < 600 or not _russian(text):
            continue
        if chunks and not _related(title + " " + text[:800], topic):  # первую берём всегда, остальные — только по теме
            continue
        per_host[host] = per_host.get(host, 0) + 1
        label = f"{_clean_title(title)} — {unquote(url)}"
        chunks.append(f"[Источник {len(chunks) + 1}: {label}]\n{text}")
        sources.append(label)
    if not chunks:
        return None
    return {"material": "\n\n".join(chunks), "sources": sources}
