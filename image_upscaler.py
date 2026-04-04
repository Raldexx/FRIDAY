#!/usr/bin/env python3
"""
Image Tools Box / Goruntu Araclar Kutusu  —  Terminal UI v4.0
==============================================================
1) Image Upscaler  /  Resim Kalite Yukseltici
2) File Sorter     /  Dosya Ayirici

Install / Kurulum:
    pip install opencv-python Pillow numpy windows-curses   (Windows)
    pip install opencv-python Pillow numpy                  (Mac/Linux)

Run / Calistir:
    python image_upscaler.py
"""

import curses
import os
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

# ══════════════════════════════════════════════════
#  DİL / LANGUAGE
# ══════════════════════════════════════════════════

STRINGS = {
    "tr": {
        # general
        "app_title":        "Goruntu Araclar Kutusu  v4.0",
        "nav_hint":         "[ Yukari/Asagi: Gez ]   [ Enter: Sec ]   [ Q: Cikis ]",
        "nav_hint_folder":  "SPACE: Bu klasoru sec   Enter/Ok: Gez   Q: Iptal",
        "any_key":          "Devam etmek icin bir tusa basin...",
        "location":         "Konum",
        "back":             "[..] Ust klasore cik",
        "dir_tag":          "[D] ",
        "file_tag":         "[F] ",
        "img_count":        "{n} resim",
        "confirm_start":    "[ Enter ]  Islemi Baslat     [ Q ]  Geri Don",
        "scroll_hint":      "[ Yukari/Asagi: Kaydir ]   [ Q / Enter: Ana Menuye Don ]",
        # language selection
        "lang_title":       "Dil Secin  /  Select Language",
        "lang_tr":          "Turkce",
        "lang_en":          "English",
        # main menu
        "main_menu_sub":    "Ne yapmak istersiniz?",
        "main_step":        "Ana Menu",
        "main_opt1":        "Resim Kalite Yukseltici  (Upscaler)",
        "main_opt2":        "Dosya Ayirici  (uzantiya gore klasorlere bol)",
        "main_opt3":        "Cikis",
        "main_desc1":       "x2 / x3 / x4 buyutme, 4 farkli algoritma",
        "main_desc2":       "JPG, MP3, PDF, ZIP... hepsini otomatik siralar",
        "main_desc3":       "",
        "bye":              "Goruntu Araclar Kutusu kapatildi.",
        # image upscaler
        "up_step_method":   "Upscaler  |  Adim 1/4: Yontem",
        "up_step_scale":    "Upscaler  |  Adim 2/4: Olcek",
        "up_step_src":      "Upscaler  |  Adim 3/4: Kaynak Klasor",
        "up_step_out":      "Upscaler  |  Adim 4/4: Cikti Klasoru",
        "up_step_confirm":  "Upscaler  |  Onay",
        "up_sub_method":    "Upscale Yontemini Secin",
        "up_sub_scale":     "Buyutme Katsayisi Secin",
        "up_sub_src":       "Resim Klasorunu Secin  (SPACE ile onayla)",
        "up_sub_out":       "Cikti Klasorunu Secin",
        "up_sub_out2":      "Cikti Klasoru Secin  (SPACE ile onayla)",
        "up_sub_confirm":   "Hazirsaniz Enter'a Basin",
        "up_processing":    "Resimler Isleniyor...",
        "up_done":          "Upscaler Tamamlandi!",
        "up_no_images":     "Bu klasorde desteklenen resim yok!",
        "up_supported":     "Desteklenen: .jpg .jpeg .png .bmp .tiff .webp",
        "up_method_label":  "Yontem",
        "up_scale_label":   "Olcek",
        "up_files_label":   "Resimler",
        "up_src_label":     "Kaynak",
        "up_out_label":     "Cikti",
        "up_out_auto":      "Otomatik  ->  {name}/  (kaynak klasor icine)",
        "up_out_custom":    "Baska bir klasor sec...",
        "up_processing_file": "Isleniyor",
        "up_out_dir_info":  "Cikti kls",
        "up_processed":     "{i} / {total} dosya islendi",
        "up_method_info":   "Yontem: {method}  Olcek: x{scale}",
        "up_extra_method":  "Yontem: {method}",
        "up_extra_src":     "Kaynak: {src}   Resim: {n} adet",
        "up_scale_x":       "x{s}  --  {pct}% buyutme",
        "up_scale_desc":    ["Hizli ve kaliteli", "Orta sure, belirgin iyilestirme", "Yavas, maksimum buyutme"],
        "m_smart":  ("Smart   [Onerilen]",  "Adim adim buyutme + keskinlestirme"),
        "m_photo":  ("Photo              ", "Gurultu azaltma + renk optimize"),
        "m_sharpen":("Sharpen            ", "Guclu keskinlestirme  Metin/cizim"),
        "m_lanczos":("Lanczos            ", "Hizli klasik yontem   Genel amac"),
        # file sorter
        "so_step_src":   "Dosya Ayirici  |  Adim 1/3: Kaynak Klasor",
        "so_step_out":   "Dosya Ayirici  |  Adim 2/3: Cikti Klasoru",
        "so_step_out2":  "Dosya Ayirici  |  Adim 2/3: Cikti Klasoru",
        "so_step_op":    "Dosya Ayirici  |  Adim 3/3: Islem",
        "so_step_prev":  "Dosya Ayirici  |  Onizleme",
        "so_step_proc":  "Dosya Ayirici  |  Islem",
        "so_sub_src":    "Ayrilacak Klasoru Secin  (SPACE ile onayla)",
        "so_sub_out":    "Cikti Klasorunu Secin",
        "so_sub_out2":   "Cikti Klasoru Secin  (SPACE ile onayla)",
        "so_sub_op":     "Islem Turu Secin",
        "so_sub_prev":   "Onizleme  --  Klasor Plani",
        "so_done":       "Dosya Ayirici Tamamlandi!",
        "so_no_files":   "Bu klasorde islenecek dosya yok!",
        "so_out_auto":   "Otomatik  ->  {name}/  (kaynak icine)",
        "so_out_custom": "Baska bir klasor sec...",
        "so_op_copy":    "Kopyala  (orijinaller yerinde kalir)",
        "so_op_move":    "Tasi  (orijinaller silinir)",
        "so_op_copy_d":  "Guvenli, disk iki kat dolar",
        "so_op_move_d":  "Hizli, yer kazanir",
        "so_total":      "Toplam {total} dosya  ->  {n} klasore ayrilacak",
        "so_out_info":   "Cikti",
        "so_extra":      "Kaynak: {src}   Dosya: {total} adet   Grup: {n} klasor",
        "so_processing": "{op}",
        "so_processed":  "{i} / {total} dosya islendi",
        "so_target":     "Hedef",
        "so_files_word": "dosya",
        "so_prev_hint":  "[ Yukari/Asagi: Kaydir ]   [ Enter: Baslat ]   [ Q: Iptal ]",
        "so_copying":    "Kopyalaniyor",
        "so_moving":     "Tasinıyor",
        # summary screen
        "sum_ok":    "Basarili",
        "sum_err":   "Hatali",
        "sum_out":   "Cikti",
    },
    "en": {
        "app_title":        "Image Tools Box  v4.0",
        "nav_hint":         "[ Up/Down: Navigate ]   [ Enter: Select ]   [ Q: Quit ]",
        "nav_hint_folder":  "SPACE: Select this folder   Enter/Arrow: Browse   Q: Cancel",
        "any_key":          "Press any key to continue...",
        "location":         "Location",
        "back":             "[..] Go to parent folder",
        "dir_tag":          "[D] ",
        "file_tag":         "[F] ",
        "img_count":        "{n} images",
        "confirm_start":    "[ Enter ]  Start Process     [ Q ]  Go Back",
        "scroll_hint":      "[ Up/Down: Scroll ]   [ Q / Enter: Back to Main Menu ]",
        "lang_title":       "Dil Secin  /  Select Language",
        "lang_tr":          "Turkce",
        "lang_en":          "English",
        "main_menu_sub":    "What would you like to do?",
        "main_step":        "Main Menu",
        "main_opt1":        "Image Upscaler",
        "main_opt2":        "File Sorter  (organize by extension)",
        "main_opt3":        "Exit",
        "main_desc1":       "x2 / x3 / x4 upscale, 4 algorithms",
        "main_desc2":       "JPG, MP3, PDF, ZIP... auto-sorted into folders",
        "main_desc3":       "",
        "bye":              "Image Tools Box closed.",
        "up_step_method":   "Upscaler  |  Step 1/4: Method",
        "up_step_scale":    "Upscaler  |  Step 2/4: Scale",
        "up_step_src":      "Upscaler  |  Step 3/4: Source Folder",
        "up_step_out":      "Upscaler  |  Step 4/4: Output Folder",
        "up_step_confirm":  "Upscaler  |  Confirm",
        "up_sub_method":    "Select Upscale Method",
        "up_sub_scale":     "Select Scale Factor",
        "up_sub_src":       "Select Image Folder  (SPACE to confirm)",
        "up_sub_out":       "Select Output Folder",
        "up_sub_out2":      "Select Output Folder  (SPACE to confirm)",
        "up_sub_confirm":   "Ready? Press Enter to Start",
        "up_processing":    "Processing Images...",
        "up_done":          "Upscaler Complete!",
        "up_no_images":     "No supported images found in this folder!",
        "up_supported":     "Supported: .jpg .jpeg .png .bmp .tiff .webp",
        "up_method_label":  "Method",
        "up_scale_label":   "Scale",
        "up_files_label":   "Images",
        "up_src_label":     "Source",
        "up_out_label":     "Output",
        "up_out_auto":      "Auto  ->  {name}/  (inside source folder)",
        "up_out_custom":    "Choose a different folder...",
        "up_processing_file": "Processing",
        "up_out_dir_info":  "Output dir",
        "up_processed":     "{i} / {total} files done",
        "up_method_info":   "Method: {method}  Scale: x{scale}",
        "up_extra_method":  "Method: {method}",
        "up_extra_src":     "Source: {src}   Images: {n}",
        "up_scale_x":       "x{s}  --  {pct}% upscale",
        "up_scale_desc":    ["Fast and high quality", "Medium time, noticeable improvement", "Slow, maximum upscale"],
        "m_smart":  ("Smart   [Recommended]", "Step-by-step upscale + sharpening"),
        "m_photo":  ("Photo               ", "Noise reduction + color optimize"),
        "m_sharpen":("Sharpen             ", "Strong sharpening  Text/drawings"),
        "m_lanczos":("Lanczos             ", "Fast classic method  General use"),
        "so_step_src":   "File Sorter  |  Step 1/3: Source Folder",
        "so_step_out":   "File Sorter  |  Step 2/3: Output Folder",
        "so_step_out2":  "File Sorter  |  Step 2/3: Output Folder",
        "so_step_op":    "File Sorter  |  Step 3/3: Operation",
        "so_step_prev":  "File Sorter  |  Preview",
        "so_step_proc":  "File Sorter  |  Processing",
        "so_sub_src":    "Select Folder to Sort  (SPACE to confirm)",
        "so_sub_out":    "Select Output Folder",
        "so_sub_out2":   "Select Output Folder  (SPACE to confirm)",
        "so_sub_op":     "Select Operation Type",
        "so_sub_prev":   "Preview  --  Folder Plan",
        "so_done":       "File Sorter Complete!",
        "so_no_files":   "No files found in this folder!",
        "so_out_auto":   "Auto  ->  {name}/  (inside source folder)",
        "so_out_custom": "Choose a different folder...",
        "so_op_copy":    "Copy  (originals stay in place)",
        "so_op_move":    "Move  (originals will be deleted)",
        "so_op_copy_d":  "Safe, uses double disk space",
        "so_op_move_d":  "Fast, saves space",
        "so_total":      "Total {total} files  ->  split into {n} folders",
        "so_out_info":   "Output",
        "so_extra":      "Source: {src}   Files: {total}   Groups: {n} folders",
        "so_processing": "{op}",
        "so_processed":  "{i} / {total} files done",
        "so_target":     "Target",
        "so_files_word": "files",
        "so_prev_hint":  "[ Up/Down: Scroll ]   [ Enter: Start ]   [ Q: Cancel ]",
        "so_copying":    "Copying",
        "so_moving":     "Moving",
        "sum_ok":    "Success",
        "sum_err":   "Failed",
        "sum_out":   "Output",
    }
}

# Active language (None at start, selected on first screen)
LANG = "en"

def T(key, **kwargs):
    """Returns string in active language, {} format."""
    s = STRINGS[LANG].get(key, key)
    return s.format(**kwargs) if kwargs else s

# ══════════════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════════════

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)
    curses.init_pair(2, curses.COLOR_GREEN,   -1)
    curses.init_pair(3, curses.COLOR_YELLOW,  -1)
    curses.init_pair(4, curses.COLOR_WHITE,   -1)
    curses.init_pair(5, curses.COLOR_RED,     -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    curses.init_pair(7, curses.COLOR_BLACK,   curses.COLOR_CYAN)

def C_TITLE():  return curses.color_pair(1) | curses.A_BOLD
def C_SEL():    return curses.color_pair(7) | curses.A_BOLD
def C_OK():     return curses.color_pair(2)
def C_WARN():   return curses.color_pair(3) | curses.A_BOLD
def C_NORMAL(): return curses.color_pair(4)
def C_ERR():    return curses.color_pair(5)
def C_INFO():   return curses.color_pair(6)
def C_DIM():    return curses.color_pair(4) | curses.A_DIM

# ══════════════════════════════════════════════════
#  UPSCALE ALGORITHMS
# ══════════════════════════════════════════════════

def pil_to_cv(img):
    arr = np.array(img)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR) if arr.ndim == 3 else arr

def cv_to_pil(arr):
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

def unsharp(img, radius=1.5, pct=130, thresh=3):
    return img.filter(ImageFilter.UnsharpMask(radius=radius, percent=pct, threshold=thresh))

def upscale_lanczos(img, scale):
    return img.resize((img.width * scale, img.height * scale), Image.LANCZOS)

def upscale_smart(img, scale):
    cur = img.copy()
    tw, th = img.width * scale, img.height * scale
    while cur.width < tw or cur.height < th:
        sw = min(cur.width * 2, tw)
        sh = min(cur.height * 2, th)
        cur = cur.resize((sw, sh), Image.LANCZOS)
        cur = unsharp(cur, 1.2, 120, 3)
    return cur

def upscale_sharpen(img, scale):
    r = upscale_lanczos(img, scale)
    r = unsharp(r, 2.0, 180, 3)
    arr = pil_to_cv(r)
    arr = cv2.bilateralFilter(arr, 5, 15, 5)
    return cv_to_pil(arr)

def upscale_photo(img, scale):
    arr = pil_to_cv(img)
    arr = cv2.fastNlMeansDenoisingColored(arr, None, 7, 7, 7, 21)
    clean = cv_to_pil(arr)
    r = upscale_smart(clean, scale)
    np_r = np.array(r).astype(np.float32)
    for c in range(3):
        ch = np_r[:, :, c]
        lo, hi = np.percentile(ch, [0.5, 99.5])
        if hi > lo:
            np_r[:, :, c] = np.clip((ch - lo) / (hi - lo) * 255, 0, 255)
    return Image.fromarray(np_r.astype(np.uint8))

METHOD_FNS = {
    "smart":   upscale_smart,
    "photo":   upscale_photo,
    "sharpen": upscale_sharpen,
    "lanczos": upscale_lanczos,
}

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
SCALES   = [2, 3, 4]

# ══════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════

def safe_add(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0:
        return
    text = text[:max(0, w - x - 1)]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass

def cprint(win, y, text, attr=0):
    h, w = win.getmaxyx()
    x = max(0, (w - len(text)) // 2)
    safe_add(win, y, x, text, attr)

def draw_header(win, subtitle="", step=""):
    title = T("app_title")
    border = "+" + "-" * (len(title) + 4) + "+"
    cprint(win, 1, border, C_TITLE())
    cprint(win, 2, f"|  {title}  |", C_TITLE())
    cprint(win, 3, border, C_TITLE())
    if step:
        cprint(win, 4, step, C_DIM())
    if subtitle:
        cprint(win, 5, subtitle, C_WARN())

def draw_divider(win, y):
    h, w = win.getmaxyx()
    safe_add(win, y, 0, "-" * (w - 1), C_DIM())

# ══════════════════════════════════════════════════
#  LANGUAGE SELECTION (first screen)
# ══════════════════════════════════════════════════

def select_language(stdscr):
    global LANG
    curses.curs_set(0)
    idx = 0
    opts = [
        ("Turkce", "tr"),
        ("English", "en"),
    ]

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        cprint(stdscr, 2,  "+----------------------------------------+", C_TITLE())
        cprint(stdscr, 3,  "|   Image Tools Box  /  Goruntu Araclari  |", C_TITLE())
        cprint(stdscr, 4,  "+----------------------------------------+", C_TITLE())
        cprint(stdscr, 6,  "Dil Secin  /  Select Language", C_WARN())

        start_y = 9
        for i, (label, _) in enumerate(opts):
            arrow = ">" if i == idx else " "
            line  = f"  {arrow}  {label}"
            if i == idx:
                safe_add(stdscr, start_y + i, 0, " " * (w - 1), C_SEL())
                safe_add(stdscr, start_y + i, 2, line[:w - 3], C_SEL())
            else:
                safe_add(stdscr, start_y + i, 2, line[:w - 3], C_NORMAL())

        cprint(stdscr, start_y + 3, "[ Up/Down ]  [ Enter: Select / Sec ]", C_INFO())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(opts)
        elif k in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(opts)
        elif k in (curses.KEY_ENTER, 10, 13):
            LANG = opts[idx][1]
            return
        elif k in (ord('q'), ord('Q'), 27):
            LANG = "en"
            return

# ══════════════════════════════════════════════════
 #  OK BUTTON MENU
# ══════════════════════════════════════════════════

def arrow_menu(stdscr, subtitle, options, descriptions=None,
               extra="", step="", start_idx=0):
    curses.curs_set(0)
    idx = start_idx
    n   = len(options)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, subtitle, step)

        if extra:
            cprint(stdscr, 7, extra, C_INFO())

        start_y = 9
        for i, label in enumerate(options):
            desc  = (descriptions[i] if descriptions else "")
            arrow = ">" if i == idx else " "
            left  = f"  {arrow}  {label}"
            gap   = max(2, w - len(left) - len(desc) - 4)
            line  = left + " " * gap + desc

            if i == idx:
                safe_add(stdscr, start_y + i, 0, " " * (w - 1), C_SEL())
                safe_add(stdscr, start_y + i, 2, line[:w - 3], C_SEL())
            else:
                safe_add(stdscr, start_y + i, 2, line[:w - 3], C_NORMAL())

        draw_divider(stdscr, start_y + n + 1)
        cprint(stdscr, start_y + n + 2, T("nav_hint"), C_INFO())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % n
        elif k in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % n
        elif k in (curses.KEY_ENTER, 10, 13):
            return idx
        elif k in (ord('q'), ord('Q'), 27):
            return -1

# ══════════════════════════════════════════════════
#  FOLDER NAVIGATOR
# ══════════════════════════════════════════════════

def folder_picker(stdscr, subtitle="", step="",
                  show_img_count=False, start_path=None):
    curses.curs_set(0)
    current = Path(start_path or Path.home())
    scroll  = 0
    idx     = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, subtitle or T("nav_hint_folder"), step)

        path_str = str(current)
        if len(path_str) > w - 12:
            path_str = "..." + path_str[-(w - 15):]
        cprint(stdscr, 7, f"{T('location')}: {path_str}", C_WARN())

        try:
            entries = sorted(current.iterdir(),
                             key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            entries = []

        items = [(T("back"), None)] + [
            ((T("dir_tag") if e.is_dir() else T("file_tag")) + e.name, e)
            for e in entries
        ]

        vis_start = 9
        max_vis   = max(1, h - vis_start - 4)

        if idx < scroll:
            scroll = idx
        elif idx >= scroll + max_vis:
            scroll = idx - max_vis + 1

        for row_i, (label, path) in enumerate(items[scroll: scroll + max_vis]):
            y      = vis_start + row_i
            abs_i  = scroll + row_i
            is_sel = (abs_i == idx)
            arrow  = ">" if is_sel else " "
            line   = f"  {arrow}  {label}"
            if is_sel:
                safe_add(stdscr, y, 0, " " * (w - 1), C_SEL())
                safe_add(stdscr, y, 2, line[:w - 3], C_SEL())
            else:
                attr = C_OK() if path and path.is_dir() else C_DIM()
                safe_add(stdscr, y, 2, line[:w - 3], attr)

        if show_img_count:
            try:
                ic = sum(1 for e in current.iterdir()
                         if e.is_file() and e.suffix.lower() in IMG_EXTS)
            except Exception:
                ic = 0
            hint_extra = f"  ({T('img_count', n=ic)})"
        else:
            hint_extra = ""

        hint = T("nav_hint_folder") + hint_extra
        safe_add(stdscr, h - 2, 0, hint[:w - 1], C_INFO())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('k')):
            idx = max(0, idx - 1)
        elif k in (curses.KEY_DOWN, ord('j')):
            idx = min(len(items) - 1, idx + 1)
        elif k in (curses.KEY_ENTER, 10, 13):
            _, path = items[idx]
            if path is None:
                current = current.parent; idx = 0; scroll = 0
            elif path.is_dir():
                current = path; idx = 0; scroll = 0
        elif k == ord(' '):
            return current
        elif k in (ord('q'), ord('Q'), 27):
            return None

# ══════════════════════════════════════════════════
#  SUMMARY SCREEN
# ══════════════════════════════════════════════════

def show_summary(stdscr, results, out_dir, title=""):
    curses.curs_set(0)
    ok_n   = sum(1 for r in results if r["status"] == "ok")
    err_n  = len(results) - ok_n
    scroll = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, title)

        cprint(stdscr, 7,
               f"{T('sum_ok')}: {ok_n}   {T('sum_err')}: {err_n}   {T('sum_out')}: {str(out_dir)[:w-35]}",
               C_OK() | curses.A_BOLD)

        vis_start = 9
        max_vis   = max(1, h - vis_start - 4)

        for row_i, r in enumerate(results[scroll: scroll + max_vis]):
            y = vis_start + row_i
            if r["status"] == "ok":
                if "orig" in r:
                    line = f"  OK   {r['name']:<26}  {r['orig']} -> {r['new']}  [{r.get('elapsed','?')}s]"
                else:
                    line = f"  OK   {r['name']:<26}  -> {r.get('dest','')}"
                attr = C_OK()
            else:
                line = f"  ERR  {r['name']:<26}  {r.get('msg', '')}"
                attr = C_ERR()
            safe_add(stdscr, y, 0, line[:w - 1], attr)

        draw_divider(stdscr, h - 3)
        cprint(stdscr, h - 2, T("scroll_hint"), C_INFO())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('k')):
            scroll = max(0, scroll - 1)
        elif k in (curses.KEY_DOWN, ord('j')):
            scroll = min(max(0, len(results) - max_vis), scroll + 1)
        elif k in (ord('q'), ord('Q'), curses.KEY_ENTER, 10, 13, 27):
            break

# ══════════════════════════════════════════════════
#  UPSCALER
# ══════════════════════════════════════════════════

def upscaler_progress(stdscr, files, method_key, scale, out_dir, quality=95):
    curses.curs_set(0)
    total     = len(files)
    results   = []
    method_fn = METHOD_FNS[method_key]
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, fpath in enumerate(files):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, T("up_processing"),
                    T("up_method_info", method=method_key, scale=scale))

        pct    = int(i / total * 100)
        bar_w  = min(44, w - 12)
        filled = int(bar_w * i / total)
        bar    = "#" * filled + "-" * (bar_w - filled)

        cprint(stdscr, 7,  f"[{bar}] {pct}%", C_OK())
        cprint(stdscr, 8,  T("up_processed", i=i, total=total), C_INFO())
        cprint(stdscr, 10, f"{T('up_processing_file')}: {fpath.name[:w-20]}", C_WARN())
        cprint(stdscr, 11, f"{T('up_out_dir_info')}: {str(out_dir)[:w-20]}", C_DIM())
        stdscr.refresh()

        out_path = out_dir / f"{fpath.stem}_x{scale}_{method_key}{fpath.suffix.lower()}"
        try:
            t0     = time.time()
            img    = Image.open(fpath).convert("RGB")
            ow, oh = img.size
            res    = method_fn(img, scale)
            nw, nh = res.size
            kw     = {"quality": quality, "optimize": True}
            if fpath.suffix.lower() in (".jpg", ".jpeg"):
                kw["subsampling"] = 0
            res.save(out_path, **kw)
            elapsed = round(time.time() - t0, 2)
            results.append({"name": fpath.name, "status": "ok",
                            "orig": f"{ow}x{oh}", "new": f"{nw}x{nh}",
                            "elapsed": elapsed})
        except Exception as e:
            results.append({"name": fpath.name, "status": "err", "msg": str(e)})

    return results


def run_upscaler(stdscr):
    method_keys = list(METHOD_FNS.keys())

    # 1. Method
    method_labels = [T(f"m_{k}")[0] for k in method_keys]
    method_descs  = [T(f"m_{k}")[1] for k in method_keys]
    m_idx = arrow_menu(stdscr, T("up_sub_method"), method_labels, method_descs,
                       step=T("up_step_method"))
    if m_idx < 0:
        return
    method_key = method_keys[m_idx]

    # 2. Scale
    scale_labels = [T("up_scale_x", s=s, pct=s*100) for s in SCALES]
    scale_descs  = T("up_scale_desc")
    s_idx = arrow_menu(stdscr, T("up_sub_scale"), scale_labels, scale_descs,
                       extra=T("up_extra_method", method=method_key),
                       step=T("up_step_scale"))
    if s_idx < 0:
        return
    scale = SCALES[s_idx]

        # 3. Source folder
    src_folder = folder_picker(stdscr, T("up_sub_src"), T("up_step_src"),
                               show_img_count=True)
    if src_folder is None:
        return

    files = sorted([f for f in src_folder.iterdir()
                    if f.is_file() and f.suffix.lower() in IMG_EXTS])
    if not files:
        stdscr.clear()
        draw_header(stdscr, T("up_no_images"))
        cprint(stdscr, 8, T("up_no_images"), C_ERR() | curses.A_BOLD)
        cprint(stdscr, 10, T("up_supported"), C_INFO())
        cprint(stdscr, 12, T("any_key"), C_NORMAL())
        stdscr.refresh(); stdscr.getch()
        return

    # 4. Output folder
    default_out = src_folder / f"upscaled_x{scale}_{method_key}"
    out_opts = [
        T("up_out_auto", name=default_out.name),
        T("up_out_custom"),
    ]
    o_idx = arrow_menu(stdscr, T("up_sub_out"), out_opts,
                       extra=T("up_extra_src", src=str(src_folder)[:50], n=len(files)),
                       step=T("up_step_out"))
    if o_idx < 0:
        return

    if o_idx == 0:
        out_dir = default_out
    else:
        picked = folder_picker(stdscr, T("up_sub_out2"), T("up_step_out"),
                               start_path=str(src_folder))
        if picked is None:
            return
        out_dir = picked / f"upscaled_x{scale}_{method_key}"

    # Confirmation
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, T("up_sub_confirm"), T("up_step_confirm"))
        rows = [
            (T("up_method_label"), method_key),
            (T("up_scale_label"),  f"x{scale}"),
            (T("up_files_label"),  f"{len(files)}"),
            (T("up_src_label"),    str(src_folder)[:w-20]),
            (T("up_out_label"),    str(out_dir)[:w-20]),
        ]
        for ri, (k, v) in enumerate(rows):
            cprint(stdscr, 8 + ri, f"{k:<12}: {v}", C_OK())
        draw_divider(stdscr, 8 + len(rows) + 1)
        cprint(stdscr, 8 + len(rows) + 2, T("confirm_start"), C_WARN())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_ENTER, 10, 13):
            break
        elif k in (ord('q'), ord('Q'), 27):
            return

    results = upscaler_progress(stdscr, files, method_key, scale, out_dir)
    show_summary(stdscr, results, out_dir, title=T("up_done"))

# ══════════════════════════════════════════════════
#  FILE SORTER  
# ══════════════════════════════════════════════════

EXT_GROUPS_TR = {
    ".jpg":"Resimler",".jpeg":"Resimler",".png":"Resimler",".gif":"Resimler",
    ".bmp":"Resimler",".webp":"Resimler",".tiff":"Resimler",".tif":"Resimler",
    ".heic":"Resimler",".svg":"Resimler",".ico":"Resimler",".raw":"Resimler",
    ".mp4":"Videolar",".mkv":"Videolar",".avi":"Videolar",".mov":"Videolar",
    ".wmv":"Videolar",".flv":"Videolar",".webm":"Videolar",".m4v":"Videolar",
    ".mp3":"Muzik",".flac":"Muzik",".wav":"Muzik",".aac":"Muzik",
    ".ogg":"Muzik",".m4a":"Muzik",".wma":"Muzik",
    ".pdf":"Belgeler",".doc":"Belgeler",".docx":"Belgeler",".xls":"Belgeler",
    ".xlsx":"Belgeler",".ppt":"Belgeler",".pptx":"Belgeler",".txt":"Belgeler",
    ".rtf":"Belgeler",".odt":"Belgeler",".ods":"Belgeler",".csv":"Belgeler",
    ".py":"Kod",".js":"Kod",".ts":"Kod",".html":"Kod",".css":"Kod",
    ".java":"Kod",".cpp":"Kod",".c":"Kod",".h":"Kod",".go":"Kod",
    ".rs":"Kod",".php":"Kod",".rb":"Kod",".sh":"Kod",".bat":"Kod",
    ".json":"Kod",".xml":"Kod",".yaml":"Kod",".yml":"Kod",".sql":"Kod",
    ".zip":"Arsivler",".rar":"Arsivler",".7z":"Arsivler",
    ".tar":"Arsivler",".gz":"Arsivler",".bz2":"Arsivler",
    ".exe":"Uygulamalar",".msi":"Uygulamalar",".dmg":"Uygulamalar",
    ".apk":"Uygulamalar",".deb":"Uygulamalar",".rpm":"Uygulamalar",
    ".ttf":"Fontlar",".otf":"Fontlar",".woff":"Fontlar",
}

EXT_GROUPS_EN = {
    ".jpg":"Images",".jpeg":"Images",".png":"Images",".gif":"Images",
    ".bmp":"Images",".webp":"Images",".tiff":"Images",".tif":"Images",
    ".heic":"Images",".svg":"Images",".ico":"Images",".raw":"Images",
    ".mp4":"Videos",".mkv":"Videos",".avi":"Videos",".mov":"Videos",
    ".wmv":"Videos",".flv":"Videos",".webm":"Videos",".m4v":"Videos",
    ".mp3":"Music",".flac":"Music",".wav":"Music",".aac":"Music",
    ".ogg":"Music",".m4a":"Music",".wma":"Music",
    ".pdf":"Documents",".doc":"Documents",".docx":"Documents",
    ".xls":"Documents",".xlsx":"Documents",".ppt":"Documents",
    ".pptx":"Documents",".txt":"Documents",".rtf":"Documents",
    ".odt":"Documents",".ods":"Documents",".csv":"Documents",
    ".py":"Code",".js":"Code",".ts":"Code",".html":"Code",".css":"Code",
    ".java":"Code",".cpp":"Code",".c":"Code",".h":"Code",".go":"Code",
    ".rs":"Code",".php":"Code",".rb":"Code",".sh":"Code",".bat":"Code",
    ".json":"Code",".xml":"Code",".yaml":"Code",".yml":"Code",".sql":"Code",
    ".zip":"Archives",".rar":"Archives",".7z":"Archives",
    ".tar":"Archives",".gz":"Archives",".bz2":"Archives",
    ".exe":"Applications",".msi":"Applications",".dmg":"Applications",
    ".apk":"Applications",".deb":"Applications",".rpm":"Applications",
    ".ttf":"Fonts",".otf":"Fonts",".woff":"Fonts",
}

def get_ext_groups():
    return EXT_GROUPS_TR if LANG == "tr" else EXT_GROUPS_EN

def analyze_folder(folder):
    groups = defaultdict(list)
    EXT_GROUPS = get_ext_groups()
    for f in folder.iterdir():
        if not f.is_file():
            continue
        ext   = f.suffix.lower()
        other = ("Diger_" if LANG == "tr" else "Other_") + (ext.lstrip(".").upper() or "NOEXT")
        group = EXT_GROUPS.get(ext, other)
        groups[group].append(f)
    return dict(groups)


def sorter_preview(stdscr, groups, out_dir):
    curses.curs_set(0)
    items  = sorted(groups.items())
    scroll = 0
    total  = sum(len(v) for v in groups.values())
    files_word = T("so_files_word")

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, T("so_sub_prev"), T("so_step_prev"))

        cprint(stdscr, 7,
               T("so_total", total=total, n=len(items)),
               C_OK() | curses.A_BOLD)
        cprint(stdscr, 8, f"{T('so_out_info')}: {str(out_dir)[:w-12]}", C_INFO())

        vis_start = 10
        max_vis   = max(1, h - vis_start - 4)

        flat = []
        for grp, flist in items:
            flat.append(("header", grp, len(flist)))
            for f in flist:
                flat.append(("file", f.name, grp))

        for row_i, entry in enumerate(flat[scroll: scroll + max_vis]):
            y = vis_start + row_i
            if entry[0] == "header":
                line = f"  [ {entry[1]} ]  ({entry[2]} {files_word})"
                safe_add(stdscr, y, 0, line[:w-1], C_WARN() | curses.A_BOLD)
            else:
                safe_add(stdscr, y, 0, f"      {entry[1]}"[:w-1], C_DIM())

        draw_divider(stdscr, h - 3)
        cprint(stdscr, h - 2, T("so_prev_hint"), C_INFO())
        stdscr.refresh()

        k = stdscr.getch()
        if k in (curses.KEY_UP, ord('k')):
            scroll = max(0, scroll - 1)
        elif k in (curses.KEY_DOWN, ord('j')):
            scroll = min(max(0, len(flat) - max_vis), scroll + 1)
        elif k in (curses.KEY_ENTER, 10, 13):
            return True
        elif k in (ord('q'), ord('Q'), 27):
            return False


def sorter_process(stdscr, groups, out_dir, move=False):
    curses.curs_set(0)
    all_files = [(grp, f) for grp, flist in groups.items() for f in flist]
    total     = len(all_files)
    results   = []
    op_fn     = shutil.move if move else shutil.copy2
    op_name   = T("so_moving") if move else T("so_copying")

    for i, (grp, fpath) in enumerate(all_files):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, f"{op_name}...", T("so_step_proc"))

        pct    = int(i / total * 100)
        bar_w  = min(44, w - 12)
        filled = int(bar_w * i / total)
        bar    = "#" * filled + "-" * (bar_w - filled)

        cprint(stdscr, 7,  f"[{bar}] {pct}%", C_OK())
        cprint(stdscr, 8,  T("so_processed", i=i, total=total), C_INFO())
        cprint(stdscr, 10, f"{op_name}: {fpath.name[:w-20]}", C_WARN())
        cprint(stdscr, 11, f"{T('so_target')}: {grp}", C_DIM())
        stdscr.refresh()

        dest_dir = out_dir / grp
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / fpath.name

        counter = 1
        while dest.exists():
            dest = dest_dir / f"{fpath.stem}_{counter}{fpath.suffix}"
            counter += 1

        try:
            op_fn(str(fpath), str(dest))
            results.append({"name": fpath.name, "status": "ok", "dest": grp})
        except Exception as e:
            results.append({"name": fpath.name, "status": "err", "msg": str(e)})

    return results


def run_sorter(stdscr):
    # 1. Source folder
    src_folder = folder_picker(stdscr, T("so_sub_src"), T("so_step_src"))
    if src_folder is None:
        return

    groups = analyze_folder(src_folder)
    if not groups:
        stdscr.clear()
        draw_header(stdscr, T("so_no_files"))
        cprint(stdscr, 8, T("so_no_files"), C_ERR() | curses.A_BOLD)
        cprint(stdscr, 10, T("any_key"), C_NORMAL())
        stdscr.refresh(); stdscr.getch()
        return

    total = sum(len(v) for v in groups.values())

    # 2. Output folder
    default_out = src_folder / ("Ayrilmis" if LANG == "tr" else "Sorted")
    out_opts = [
        T("so_out_auto", name=default_out.name),
        T("so_out_custom"),
    ]
    o_idx = arrow_menu(stdscr, T("so_sub_out"), out_opts,
                       extra=T("so_extra", src=str(src_folder)[:50],
                               total=total, n=len(groups)),
                       step=T("so_step_out"))
    if o_idx < 0:
        return

    if o_idx == 0:
        out_dir = default_out
    else:
        picked = folder_picker(stdscr, T("so_sub_out2"), T("so_step_out2"),
                               start_path=str(src_folder))
        if picked is None:
            return
        out_dir = picked / ("Ayrilmis" if LANG == "tr" else "Sorted")

    # 3. Copy / Move
    op_idx = arrow_menu(stdscr, T("so_sub_op"),
                        [T("so_op_copy"), T("so_op_move")],
                        [T("so_op_copy_d"), T("so_op_move_d")],
                        step=T("so_step_op"))
    if op_idx < 0:
        return
    move = (op_idx == 1)

    go = sorter_preview(stdscr, groups, out_dir)
    if not go:
        return

    results = sorter_process(stdscr, groups, out_dir, move=move)
    show_summary(stdscr, results, out_dir, title=T("so_done"))

# ══════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════

def main(stdscr):
    curses.curs_set(0)
    init_colors()

    # Language selection
    select_language(stdscr)

    while True:
        choice = arrow_menu(
            stdscr,
            subtitle=T("main_menu_sub"),
            options=[T("main_opt1"), T("main_opt2"), T("main_opt3")],
            descriptions=[T("main_desc1"), T("main_desc2"), T("main_desc3")],
            step=T("main_step"),
        )

        if choice == 0:
            run_upscaler(stdscr)
        elif choice == 1:
            run_sorter(stdscr)
        elif choice == 2 or choice < 0:
            break


def run():
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print(f"\n{T('bye')}\n")


# ══════════════════════════════════════════════════
#  START
# ══════════════════════════════════════════════════
if __name__ == "__main__":
    missing = []
    try:    import cv2
    except: missing.append("opencv-python")
    try:    from PIL import Image
    except: missing.append("Pillow")
    try:    import numpy
    except: missing.append("numpy")

    if missing:
        print("Missing packages / Eksik paketler:", ", ".join(missing))
        print(f"Run / Calistir: pip install {' '.join(missing)}")
        sys.exit(1)

    run()
