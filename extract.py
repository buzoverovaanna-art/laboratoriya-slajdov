# -*- coding: utf-8 -*-
"""Достаёт текст из файлов и фото, которые ученица добавила плюсиком в режиме «Вставлю текст сама».

Фото и PDF читает встроенное распознавание macOS (программа ocr.swift), TXT и DOCX — обычным чтением.
Файлы сохраняются только на время чтения и сразу удаляются — нигде не хранятся.
"""
import os
import re
import subprocess
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OCR_SRC = os.path.join(HERE, "ocr.swift")
OCR_BIN = os.path.join(HERE, "ocr")

IMAGES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp", ".gif"}


class ExtractError(Exception):
    """Понятная причина, почему файл не прочитался (можно показывать ученице)."""


def ensure_ocr():
    """Собирает программу распознавания при первом использовании (около 20 секунд)."""
    if os.path.isfile(OCR_BIN) and os.path.getmtime(OCR_BIN) >= os.path.getmtime(OCR_SRC):
        return
    r = subprocess.run(["swiftc", "-O", OCR_SRC, "-o", OCR_BIN], capture_output=True, text=True, timeout=240)
    if r.returncode != 0:
        print("[распознавание] не собралось:", r.stderr[:300])
        raise ExtractError("Не получилось подготовить распознавание текста. Вставь текст вручную.")


def _is_heading(line, nxt):
    """Короткая строка без точки перед предложением с заглавной буквы — это заголовок («§ 3. Клеточная теория»)."""
    return line.startswith("§") or (len(line) < 50 and nxt[:1].isupper())


def tidy(text):
    """Склеивает строки распознанного текста в абзацы и убирает переносы слов."""
    lines = [ln.strip() for ln in text.replace("\r", "").split("\n")]
    out, buf = [], ""
    for ln in lines:
        if not ln:
            if buf:
                out.append(buf)
                buf = ""
            continue
        if buf.endswith("-") and ln[:1].islower():           # перенос слова: «револю-» + «ция»
            buf = buf[:-1] + ln
        elif buf and not re.search(r"[.!?:;»…)]$", buf) and not _is_heading(buf, ln):  # обрыв посреди фразы — склеиваем
            buf += " " + ln
        else:
            if buf:
                out.append(buf)
            buf = ln
    if buf:
        out.append(buf)
    return "\n\n".join(out)


def _ocr(path):
    ensure_ocr()
    r = subprocess.run([OCR_BIN, path], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise ExtractError("Не получилось открыть этот файл. Попробуй другой снимок.")
    return r.stdout


def _docx(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
    except (zipfile.BadZipFile, KeyError):
        raise ExtractError("Не получилось открыть документ Word.")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    return (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"').replace("&apos;", "'"))


def _plain(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ExtractError("Не получилось прочитать текстовый файл.")


def extract_file(path, filename):
    """Текст из одного файла. Бросает ExtractError с понятным сообщением."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGES or ext == ".pdf":
        text = tidy(_ocr(path))
    elif ext in (".txt", ".md"):
        text = _plain(path).strip()
    elif ext == ".docx":
        text = tidy(_docx(path))
    else:
        raise ExtractError(f"Файлы «{ext or 'без названия типа'}» пока не читаю. Подойдут фото, PDF, TXT и DOCX.")
    if len(text) < 20:
        raise ExtractError("Текста в файле не нашла. Проверь, что снимок чёткий и страница видна целиком.")
    return text
