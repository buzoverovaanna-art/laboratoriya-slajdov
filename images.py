# -*- coding: utf-8 -*-
"""Картинка на каждый слайд: тематическая (история, литература…) или мем/гифка — для настроения.

Как работает: Сценарист (ai.py) для каждого слайда придумывает короткий поисковый запрос
(image_query) и решает, что нужно — 'photo' (настоящая картина/фото по теме) или 'meme'
(мем/гифка по эмоции слайда). Мы ищем через тот же Google-поиск (Serper), что и research.py,
скачиваем первую подходящую картинку и вшиваем её прямо в файл (base64) — презентация потом
работает без интернета. Ключа нет, поиск недоступен или ничего не подошло — слайд остаётся
без картинки, презентация всё равно работает.

Ключ Serper — тот же файл, что и в research.py: ~/.config/klyuchi-zakrytye/serper.key.
"""
import base64
import concurrent.futures as cf
import io
import re
import time
from urllib.parse import urlparse

import httpx

import research

IMG_TIMEOUT = 8          # секунд на запрос поиска картинок
DL_TIMEOUT = 8           # секунд на скачивание одной картинки
MAX_CANDIDATES = 5       # сколько картинок из выдачи пробуем, пока не найдём подходящую
MIN_SIDE = 220           # меньше — скорее всего значок или логотип, пропускаем
MAX_BYTES_RAW = 4_000_000    # совсем большие картинки не скачиваем даже ради сжатия
MAX_BYTES_STATIC = 450_000   # предел для обычной картинки после сжатия
MAX_BYTES_GIF = 2_500_000    # гифки не сжимаем (сломается анимация) — только ограничиваем вес
TIME_BUDGET = 40         # секунд на все картинки презентации разом (не зависит от числа слайдов)
WORKERS = 6              # сколько картинок ищем и грузим одновременно

# Фотостоки отдают мутные превью с водяными знаками и подписью вида «Illustration 279794505» — не берём
STOCK_HOSTS = ["dreamstime.com", "shutterstock.com", "istockphoto.com", "gettyimages.com", "alamy.com",
               "123rf.com", "depositphotos.com", "stock.adobe.com", "fotolia.com", "canstockphoto.com",
               "vecteezy.com", "stockcake.com", "freepik.com"]
JUNK_TITLE = re.compile(r"^(download|free)\b", re.I)  # заголовки-кнопки со стоков («Download ... Image») — не подпись


def _stock_photo(url):
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in STOCK_HOSTS)


def _search_images(query, key, animated=False):
    body = {"q": query, "gl": "ru", "num": MAX_CANDIDATES + 4}
    if animated:
        body["tbs"] = "itp:animated"  # просим у Google только анимированные — для мемов и гифок
    r = httpx.post("https://google.serper.dev/images", headers={"X-API-KEY": key}, json=body, timeout=IMG_TIMEOUT)
    r.raise_for_status()
    return r.json().get("images", [])


def _download(url):
    r = httpx.get(url, headers=research.UA, timeout=DL_TIMEOUT, follow_redirects=True)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "").split(";")[0].strip().lower()
    if not ctype.startswith("image/"):
        raise ValueError("не картинка")
    return r.content, ctype


def _shrink(data, ctype):
    """Ужимает крупную обычную картинку до разумного веса. Гифки не трогаем — иначе пропадёт анимация."""
    if ctype == "image/gif" or len(data) <= MAX_BYTES_STATIC:
        return data, ctype
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail((900, 900))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=80)
        return buf.getvalue(), "image/jpeg"
    except Exception as e:
        print(f"[картинки] не сжалось: {type(e).__name__}", flush=True)
        return data, ctype


CREDIT_TITLE_MAX = 60  # длинные заголовки статей («Кто такие бояре и почему...») не годятся в подпись


def _credit(item):
    """Подпись для серьёзной картинки: название и источник (как «Вермеер — Рийксмузеум»)."""
    title = (item.get("title") or "").strip().split("|")[0].strip(" .,]")  # на сайтах-каталогах после | — их меню, не название
    if JUNK_TITLE.match(title):
        title = ""
    if len(title) > CREDIT_TITLE_MAX:
        title = title[:CREDIT_TITLE_MAX - 1].rstrip() + "…"
    source = (item.get("source") or "").strip()
    bits = [title] if title else []
    if source and source.lower() not in title.lower():  # источник часто уже упомянут в названии — не повторяем
        bits.append(source)
    return " — ".join(bits)[:140]


def find_image(query, kind, key=None):
    """Ищет и скачивает одну картинку по запросу. None, если ключа нет, запроса нет или ничего не подошло."""
    key = key or research.serper_key()
    query = (query or "").strip()
    if not key or not query:
        return None
    animated = kind == "meme"
    try:
        items = _search_images(query, key, animated=animated)
    except (httpx.HTTPError, ValueError, KeyError) as e:
        print(f"[картинки] поиск «{query[:40]}»: {type(e).__name__}", flush=True)
        return None
    for item in items[:MAX_CANDIDATES]:
        url = item.get("imageUrl") or item.get("link")
        if not url or research.blocked_host(url) or _stock_photo(url):
            continue
        w, h = item.get("imageWidth") or 0, item.get("imageHeight") or 0
        if w and h and (w < MIN_SIDE or h < MIN_SIDE):
            continue
        try:
            data, ctype = _download(url)
        except Exception as e:
            print(f"[картинки] загрузка не удалась ({url[:60]}): {type(e).__name__}", flush=True)
            continue
        if len(data) > MAX_BYTES_RAW:
            continue
        data, ctype = _shrink(data, ctype)
        limit = MAX_BYTES_GIF if ctype == "image/gif" else MAX_BYTES_STATIC
        if len(data) > limit:
            continue
        b64 = base64.b64encode(data).decode("ascii")
        return {
            "data": f"data:{ctype};base64,{b64}",
            "alt": query[:140],
            "credit": _credit(item) if kind == "photo" else "",
            "kind": kind,
        }
    return None


def illustrate_deck(deck):
    """Добавляет deck['slides'][i]['image'] везде, где Сценарист попросил картинку (image_query).

    Ищет и скачивает параллельно (несколько слайдов разом), чтобы не растягивать создание презентации
    надолго. Нет ключа Serper или не успели за отведённое время — часть слайдов остаётся без картинки,
    презентация всё равно готова и работает.
    """
    key = research.serper_key()
    jobs = [(i, s["image_query"], s.get("image_kind") or "photo")
            for i, s in enumerate(deck.get("slides", [])) if s.get("image_query")]
    if not key or not jobs:
        return deck
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(find_image, q, k, key): i for i, q, k in jobs}
        try:
            for fut in cf.as_completed(futures, timeout=TIME_BUDGET):
                i = futures[fut]
                try:
                    img = fut.result()
                except Exception as e:
                    print(f"[картинки] слайд {i}: {type(e).__name__}", flush=True)
                    continue
                if img:
                    deck["slides"][i]["image"] = img
        except cf.TimeoutError:
            print("[картинки] не успела до конца — часть слайдов останется без картинок", flush=True)
    found = sum(1 for s in deck["slides"] if s.get("image"))
    print(f"[картинки] готово за {time.time() - t0:.1f} с: {found}/{len(jobs)}", flush=True)
    return deck
