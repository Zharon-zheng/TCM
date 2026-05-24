import json
import math
import os
import re
import shutil
import subprocess
import sys
import html
import webbrowser
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


APP_TITLE = "中医门诊系统"
DATA_FILE_NAME = "data.json"
PATIENT_FILE_NAME = "patients.json"
BACKUP_DIR_NAME = "backup"
EXPORT_DIR_NAME = "exports"
PRINT_DIR_NAME = "prints"
ALL_OPTION = "全部"
DISCLAIMER = "本系统用于门诊资料记录、患者档案管理与知识库检索。"
COLOR_BG = "#f4f7f5"
COLOR_SURFACE = "#ffffff"
COLOR_PANEL = "#edf3ef"
COLOR_TEXT = "#17211c"
COLOR_MUTED = "#66746c"
COLOR_BORDER = "#cfd8d2"
COLOR_ACCENT = "#1f7a6d"
COLOR_ACCENT_DARK = "#155c52"
COLOR_ACCENT_SOFT = "#dcefeb"
COLOR_WARNING = "#9a5b13"
FONT_MAIN = ("Microsoft YaHei UI", 10)
FONT_TITLE = ("Microsoft YaHei UI", 18, "bold")
FONT_PAGE_TITLE = ("Microsoft YaHei UI", 15, "bold")
FONT_SECTION = ("Microsoft YaHei UI", 11, "bold")


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
DATA_PATH = BASE_DIR / DATA_FILE_NAME
PATIENT_PATH = BASE_DIR / PATIENT_FILE_NAME
BACKUP_DIR = BASE_DIR / BACKUP_DIR_NAME
EXPORT_DIR = BASE_DIR / EXPORT_DIR_NAME
PRINT_DIR = EXPORT_DIR / PRINT_DIR_NAME


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_text():
    return datetime.now().strftime("%Y-%m-%d")


def timestamp_for_file():
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def normalize_text(value):
    return str(value or "").strip()


def split_keywords(text):
    parts = re.split(r"[\s,，、;；\n\r]+", text or "")
    result = []
    seen = set()
    for part in parts:
        item = part.strip()
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def formula_names(record):
    names = []
    for formula in record.get("formulas", []) or []:
        name = normalize_text(formula.get("name"))
        if name:
            names.append(name)
    return "、".join(names)


def sanitize_filename(value):
    name = re.sub(r'[\\/:*?"<>|]+', "_", normalize_text(value))
    return name or "未命名"


def write_json(path, data):
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def backup_file(path, prefix):
    path = Path(path)
    if not path.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    backup_path = BACKUP_DIR / f"{prefix}_{timestamp_for_file()}.json"
    shutil.copy2(path, backup_path)
    return backup_path


def setup_theme(root):
    root.configure(bg=COLOR_BG)
    root.option_add("*Font", FONT_MAIN)
    root.option_add("*Listbox.Font", FONT_MAIN)
    root.option_add("*Listbox.background", COLOR_SURFACE)
    root.option_add("*Listbox.foreground", COLOR_TEXT)
    root.option_add("*Listbox.selectBackground", COLOR_ACCENT)
    root.option_add("*Listbox.selectForeground", "#ffffff")
    root.option_add("*Listbox.highlightThickness", 1)
    root.option_add("*Listbox.highlightColor", COLOR_ACCENT)
    root.option_add("*Listbox.highlightBackground", COLOR_BORDER)
    root.option_add("*Text.Font", FONT_MAIN)
    root.option_add("*Text.background", COLOR_SURFACE)
    root.option_add("*Text.foreground", COLOR_TEXT)
    root.option_add("*Text.insertBackground", COLOR_TEXT)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", font=FONT_MAIN, background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Surface.TFrame", background=COLOR_SURFACE, relief=tk.SOLID, borderwidth=1)
    style.configure("Panel.TFrame", background=COLOR_PANEL)
    style.configure("Header.TFrame", background=COLOR_SURFACE)
    style.configure("Footer.TFrame", background=COLOR_BG)
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure("Title.TLabel", background=COLOR_SURFACE, foreground=COLOR_TEXT, font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=COLOR_SURFACE, foreground=COLOR_MUTED)
    style.configure("PageTitle.TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_PAGE_TITLE)
    style.configure("Section.TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=FONT_SECTION)
    style.configure("Muted.TLabel", background=COLOR_BG, foreground=COLOR_MUTED)
    style.configure("Footer.TLabel", background=COLOR_BG, foreground=COLOR_MUTED)
    style.configure("TButton", padding=(12, 7), background="#eef2ef", foreground=COLOR_TEXT, bordercolor=COLOR_BORDER, focusthickness=1, focuscolor=COLOR_ACCENT)
    style.map("TButton", background=[("active", "#e2e9e5"), ("pressed", "#d5e0da")])
    style.configure("Accent.TButton", padding=(14, 7), background=COLOR_ACCENT, foreground="#ffffff", bordercolor=COLOR_ACCENT_DARK)
    style.map("Accent.TButton", background=[("active", COLOR_ACCENT_DARK), ("pressed", COLOR_ACCENT_DARK)], foreground=[("disabled", "#e4ece9")])
    style.configure("Ghost.TButton", padding=(12, 7), background=COLOR_SURFACE, foreground=COLOR_ACCENT, bordercolor=COLOR_BORDER)
    style.map("Ghost.TButton", background=[("active", COLOR_ACCENT_SOFT), ("pressed", COLOR_ACCENT_SOFT)])
    style.configure("Danger.TButton", padding=(12, 7), background="#fff1eb", foreground="#8f2f18", bordercolor="#e9c2b4")
    style.map("Danger.TButton", background=[("active", "#ffe2d6"), ("pressed", "#ffd5c4")])
    style.configure("TEntry", fieldbackground=COLOR_SURFACE, foreground=COLOR_TEXT, bordercolor=COLOR_BORDER, lightcolor=COLOR_ACCENT, darkcolor=COLOR_BORDER, padding=5)
    style.configure("TCombobox", fieldbackground=COLOR_SURFACE, foreground=COLOR_TEXT, bordercolor=COLOR_BORDER, arrowcolor=COLOR_ACCENT, padding=5)
    style.configure("TPanedwindow", background=COLOR_BG)
    style.configure("Vertical.TScrollbar", background="#dce5df", troughcolor=COLOR_BG, bordercolor=COLOR_BG, arrowcolor=COLOR_ACCENT)
    style.configure("Horizontal.TScrollbar", background="#dce5df", troughcolor=COLOR_BG, bordercolor=COLOR_BG, arrowcolor=COLOR_ACCENT)


def default_records():
    created = "2026-05-24 00:00:00"
    return [
        {
            "id": 1,
            "system": "六经辨证",
            "category": "太阳病证",
            "sub_category": "太阳经证",
            "syndrome_name": "太阳中风",
            "symptoms": ["恶风发热", "汗出", "头项强痛", "鼻鸣", "干呕", "舌苔薄白", "脉浮缓"],
            "symptom_description": "恶风发热，汗出，头项强痛，或见鼻鸣，干呕，舌苔薄白，脉浮缓。",
            "formulas": [{"name": "桂枝汤", "composition": "桂枝、芍药、生姜、大枣、甘草", "usage": "", "note": "对应太阳中风证。"}],
            "treatment_plan": "可参考桂枝汤方案，由专业人员结合实际情况辨证使用。",
            "notes": "仅作为知识库检索内容。",
            "created_at": created,
            "updated_at": created
        },
        {
            "id": 2,
            "system": "六经辨证",
            "category": "太阳病证",
            "sub_category": "太阳经证",
            "syndrome_name": "太阳伤寒",
            "symptoms": ["恶寒发热", "头项强痛", "身体疼痛", "无汗而喘", "脉浮紧"],
            "symptom_description": "恶寒发热，头项强痛，身体疼痛，无汗而喘，脉浮紧。",
            "formulas": [{"name": "麻黄汤", "composition": "麻黄、桂枝、杏仁、甘草", "usage": "", "note": "示例方剂。"}],
            "treatment_plan": "可参考麻黄汤方案，由专业人员结合实际情况辨证使用。",
            "notes": "仅作为知识库检索内容。",
            "created_at": created,
            "updated_at": created
        },
        {
            "id": 3,
            "system": "六经辨证",
            "category": "少阳病证",
            "sub_category": "",
            "syndrome_name": "少阳病证",
            "symptoms": ["寒热往来", "胸胁苦满", "默默不欲饮食", "心烦喜呕", "口苦", "咽干", "目眩", "脉弦"],
            "symptom_description": "寒热往来，胸胁苦满，默默不欲饮食，心烦喜呕，口苦，咽干，目眩，脉弦。",
            "formulas": [{"name": "小柴胡汤", "composition": "柴胡、黄芩、人参、半夏、生姜、大枣、甘草", "usage": "", "note": "示例方剂。"}],
            "treatment_plan": "可参考小柴胡汤方案，由专业人员结合实际情况辨证使用。",
            "notes": "仅作为知识库检索内容。",
            "created_at": created,
            "updated_at": created
        },
        {
            "id": 4,
            "system": "脏腑辨证",
            "category": "脾胃病证",
            "sub_category": "",
            "syndrome_name": "脾胃虚寒",
            "symptoms": ["胃脘隐痛", "喜温喜按", "食少", "便溏", "四肢不温"],
            "symptom_description": "胃脘隐痛，喜温喜按，食少，便溏，四肢不温。",
            "formulas": [{"name": "理中汤", "composition": "人参、干姜、白术、甘草", "usage": "", "note": "示例方剂。"}],
            "treatment_plan": "可参考理中汤方案，由专业人员结合实际情况辨证使用。",
            "notes": "仅作为知识库检索内容。",
            "created_at": created,
            "updated_at": created
        },
        {
            "id": 5,
            "system": "自定义病症",
            "category": "合并病症",
            "sub_category": "",
            "syndrome_name": "太阳少阳合病",
            "symptoms": ["恶寒发热", "头项强痛", "寒热往来", "胸胁苦满", "口苦", "咽干"],
            "symptom_description": "恶寒发热，头项强痛，寒热往来，胸胁苦满，口苦，咽干。",
            "formulas": [{"name": "柴胡桂枝汤", "composition": "柴胡、黄芩、人参、半夏、桂枝、芍药、生姜、大枣、甘草", "usage": "", "note": "示例方剂。"}],
            "treatment_plan": "由医生或专业人员根据具体情况调整，仅作为知识库资料参考。",
            "notes": "复杂病症可作为独立记录录入，程序只负责检索展示。",
            "created_at": created,
            "updated_at": created
        }
    ]


def validate_records(data):
    if not isinstance(data, list):
        raise ValueError("JSON 顶层结构必须是记录列表。")
    used_ids = set()
    next_id = 1
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 条记录不是有效对象。")
        item_id = item.get("id")
        if not isinstance(item_id, int) or item_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            item_id = next_id
        item["id"] = item_id
        used_ids.add(item_id)
        for key, default in [
            ("system", ""),
            ("category", ""),
            ("sub_category", ""),
            ("syndrome_name", ""),
            ("symptoms", []),
            ("symptom_description", ""),
            ("formulas", []),
            ("treatment_plan", ""),
            ("notes", ""),
            ("created_at", now_text()),
            ("updated_at", now_text())
        ]:
            item.setdefault(key, default)
        if isinstance(item.get("symptoms"), str):
            item["symptoms"] = split_keywords(item["symptoms"])
        if not isinstance(item.get("symptoms"), list):
            item["symptoms"] = []
        if not isinstance(item.get("formulas"), list):
            item["formulas"] = []
    return data


def validate_patients(data):
    if not isinstance(data, list):
        raise ValueError("患者档案 JSON 顶层结构必须是列表。")
    used_ids = set()
    next_id = 1
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 个患者档案不是有效对象。")
        item_id = item.get("id")
        if not isinstance(item_id, int) or item_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            item_id = next_id
        item["id"] = item_id
        used_ids.add(item_id)
        for key, default in [
            ("name", ""),
            ("gender", ""),
            ("age", ""),
            ("phone", ""),
            ("address", ""),
            ("allergy_history", ""),
            ("past_history", ""),
            ("notes", ""),
            ("visits", []),
            ("created_at", now_text()),
            ("updated_at", now_text())
        ]:
            item.setdefault(key, default)
        if not isinstance(item.get("visits"), list):
            item["visits"] = []
        used_visit_ids = set()
        next_visit_id = 1
        clean_visits = []
        for visit in item["visits"]:
            if not isinstance(visit, dict):
                continue
            visit_id = visit.get("id")
            if not isinstance(visit_id, int) or visit_id in used_visit_ids:
                while next_visit_id in used_visit_ids:
                    next_visit_id += 1
                visit_id = next_visit_id
            visit["id"] = visit_id
            used_visit_ids.add(visit_id)
            for key, default in [
                ("visit_date", today_text()),
                ("chief_complaint", ""),
                ("present_illness", ""),
                ("tongue_pulse", ""),
                ("syndrome_record", ""),
                ("formula_reference", ""),
                ("treatment_plan", ""),
                ("advice", ""),
                ("notes", ""),
                ("selected_syndromes", []),
                ("created_at", now_text()),
                ("updated_at", now_text())
            ]:
                visit.setdefault(key, default)
            if not isinstance(visit.get("selected_syndromes"), list):
                visit["selected_syndromes"] = []
            clean_visits.append(visit)
        item["visits"] = clean_visits
    return data


class MainWindowApp:
    def __init__(self, root):
        self.root = root
        self.records = []
        self.patients = []
        self.data_dirty = False
        self.patient_dirty = False
        self.current_page = ""

        self.selected_record = None
        self.knowledge_results = []
        self.patient_results = []
        self.selected_patient = None
        self.selected_visit = None

        self.root.title(APP_TITLE)
        self.root.geometry("1260x820")
        self.root.minsize(1080, 680)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        BACKUP_DIR.mkdir(exist_ok=True)
        EXPORT_DIR.mkdir(exist_ok=True)
        PRINT_DIR.mkdir(parents=True, exist_ok=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.build_shell()
        self.load_data()
        self.load_patients()
        self.show_patient_list_page()

    def build_shell(self):
        header = ttk.Frame(self.root, padding=(18, 14, 18, 12), style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        title_box = ttk.Frame(header, style="Header.TFrame")
        title_box.grid(row=0, column=0, sticky="w")
        ttk.Label(title_box, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(title_box, text="患者档案、门诊病历与方剂知识库一体化管理", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(3, 0))

        nav = ttk.Frame(header, style="Header.TFrame")
        nav.grid(row=0, column=1, sticky="e")
        ttk.Button(nav, text="患者档案", command=self.show_patient_list_page, style="Ghost.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(nav, text="知识库管理", command=self.show_knowledge_page, style="Ghost.TButton").pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(nav, text="保存全部", command=self.save_all, style="Accent.TButton").pack(side=tk.LEFT)

        self.content = ttk.Frame(self.root, padding=(18, 14, 18, 10))
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        footer = ttk.Frame(self.root, padding=(18, 2, 18, 10), style="Footer.TFrame")
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.status_var = tk.StringVar(value=DISCLAIMER)
        ttk.Label(footer, textvariable=self.status_var, style="Footer.TLabel").grid(row=0, column=0, sticky="w")

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def set_status(self, text):
        self.status_var.set(f"{text}。{DISCLAIMER}")

    def display_value(self, value):
        value = normalize_text(value)
        return value if value else "未填写"

    def add_display_section(self, lines, label, value):
        value = normalize_text(value)
        if value:
            lines.extend([f"{label}：", value])
        else:
            lines.append(f"{label}：未填写")

    def update_title(self):
        mark = "*" if self.data_dirty or self.patient_dirty else ""
        self.root.title(f"{APP_TITLE}{mark}")

    def set_data_dirty(self, dirty):
        self.data_dirty = dirty
        self.update_title()

    def set_patient_dirty(self, dirty):
        self.patient_dirty = dirty
        self.update_title()

    def load_data(self):
        if not DATA_PATH.exists():
            self.records = default_records()
            try:
                write_json(DATA_PATH, self.records)
            except OSError as exc:
                messagebox.showerror("错误", f"默认知识库创建失败：\n{exc}")
            return
        try:
            with DATA_PATH.open("r", encoding="utf-8") as file:
                self.records = validate_records(json.load(file))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("数据文件格式错误", f"知识库数据文件格式错误，请检查 data.json，或从备份文件恢复。\n\n错误信息：{exc}")
            self.records = default_records()
            self.set_data_dirty(True)

    def load_patients(self):
        if not PATIENT_PATH.exists():
            self.patients = []
            try:
                write_json(PATIENT_PATH, self.patients)
            except OSError as exc:
                messagebox.showerror("错误", f"患者档案文件创建失败：\n{exc}")
            return
        try:
            with PATIENT_PATH.open("r", encoding="utf-8") as file:
                self.patients = validate_patients(json.load(file))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("患者档案格式错误", f"患者档案文件格式错误，请检查 patients.json，或从备份文件恢复。\n\n错误信息：{exc}")
            self.patients = []
            self.set_patient_dirty(True)

    def save_data(self):
        try:
            backup_file(DATA_PATH, "data")
            write_json(DATA_PATH, self.records)
        except OSError as exc:
            messagebox.showerror("保存失败", f"知识库保存失败，请检查文件权限或磁盘空间。\n\n错误信息：{exc}")
            return False
        self.set_data_dirty(False)
        self.set_status(f"知识库已保存：{now_text()}")
        return True

    def save_patients(self):
        try:
            backup_file(PATIENT_PATH, "patients")
            write_json(PATIENT_PATH, self.patients)
        except OSError as exc:
            messagebox.showerror("保存失败", f"患者档案保存失败，请检查文件权限或磁盘空间。\n\n错误信息：{exc}")
            return False
        self.set_patient_dirty(False)
        self.set_status(f"患者档案已保存：{now_text()}")
        return True

    def save_all(self):
        ok = True
        if self.data_dirty:
            ok = self.save_data() and ok
        if self.patient_dirty:
            ok = self.save_patients() and ok
        if ok:
            messagebox.showinfo("保存完成", "所有未保存的数据已保存，并已自动备份。")

    def next_record_id(self):
        return max([item.get("id", 0) for item in self.records if isinstance(item.get("id", 0), int)], default=0) + 1

    def next_patient_id(self):
        return max([item.get("id", 0) for item in self.patients if isinstance(item.get("id", 0), int)], default=0) + 1

    def next_visit_id(self, patient):
        return max([item.get("id", 0) for item in patient.get("visits", []) if isinstance(item.get("id", 0), int)], default=0) + 1

    def entry_row(self, parent, row, key, label, values, width=52):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        var = tk.StringVar(value=values.get(key, ""))
        entry = ttk.Entry(parent, textvariable=var, width=width)
        entry.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=5, ipady=2)
        return var

    def estimate_text_rows(self, text, max_rows=6, widget=None):
        content = normalize_text(text)
        if not content:
            return 1
        if widget is not None and widget.winfo_width() > 40:
            approx_chars = max(24, int((widget.winfo_width() - 32) / 8))
        else:
            approx_chars = 58
        rows = 0
        for line in content.splitlines() or [""]:
            rows += max(1, math.ceil(len(line) / approx_chars))
        return max(1, min(max_rows, rows))

    def resize_text_widget_height(self, widget):
        max_rows = getattr(widget, "_max_display_rows", 6)
        rows = self.estimate_text_rows(self.text_get(widget), max_rows=max_rows, widget=widget)
        if str(widget.cget("height")) != str(rows):
            widget.configure(height=rows)

    def text_row(self, parent, row, key, label, values, height=4):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="nw", pady=4)
        value = values.get(key, "") or ""
        text = ScrolledText(parent, width=68, height=self.estimate_text_rows(value, max_rows=height), wrap=tk.WORD)
        text._max_display_rows = height
        self.style_text_widget(text)
        text.grid(row=row, column=1, sticky="nsew", padx=(12, 0), pady=5)
        text.insert("1.0", value)
        text.bind("<KeyRelease>", lambda event, widget=text: self.resize_text_widget_height(widget))
        text.bind("<FocusOut>", lambda event, widget=text: self.resize_text_widget_height(widget))
        text.bind("<Configure>", lambda event, widget=text: widget.after_idle(lambda: self.resize_text_widget_height(widget)))
        parent.rowconfigure(row, weight=0)
        return text

    def style_text_widget(self, widget, readonly=False):
        widget.configure(
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT,
            insertbackground=COLOR_TEXT,
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_ACCENT,
            padx=8,
            pady=6,
            font=FONT_MAIN
        )
        if readonly:
            widget.configure(background="#fbfcfb")

    def style_listbox(self, widget):
        widget.configure(
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT,
            selectbackground=COLOR_ACCENT,
            selectforeground="#ffffff",
            relief=tk.SOLID,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_ACCENT,
            activestyle="none",
            font=FONT_MAIN
        )

    def text_get(self, widget):
        return widget.get("1.0", tk.END).strip()

    def text_set(self, widget, value):
        widget.delete("1.0", tk.END)
        widget.insert("1.0", value or "")
        if hasattr(widget, "_max_display_rows"):
            widget.after_idle(lambda: self.resize_text_widget_height(widget))

    def append_text(self, widget, text):
        text = normalize_text(text)
        if not text:
            return
        current = self.text_get(widget)
        if text in current:
            return
        self.text_set(widget, f"{current}\n\n{text}".strip() if current else text)

    def sync_canvas_window_width(self, canvas, window_id):
        def resize_inner(event):
            window_name = canvas.itemcget(window_id, "window")
            inner = canvas.nametowidget(window_name)
            inner.update_idletasks()
            canvas.itemconfigure(window_id, width=event.width, height=max(inner.winfo_reqheight(), event.height))
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", resize_inner)

    # ---------------- Knowledge pages ----------------

    def show_knowledge_page(self):
        self.current_page = "knowledge"
        self.clear_content()
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)

        title = ttk.Frame(page)
        title.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(title, text="知识库管理", style="PageTitle.TLabel").pack(side=tk.LEFT)

        controls = ttk.Frame(page)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="检索内容").grid(row=0, column=0, sticky="w")
        self.k_query = tk.StringVar()
        query_entry = ttk.Entry(controls, textvariable=self.k_query)
        query_entry.grid(row=0, column=1, sticky="ew", padx=8)
        query_entry.bind("<Return>", lambda event: self.refresh_knowledge_results())
        ttk.Button(controls, text="搜索", command=self.refresh_knowledge_results).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(controls, text="清空", command=lambda: (self.k_query.set(""), self.k_system.set(ALL_OPTION), self.k_category.set(ALL_OPTION), self.refresh_knowledge_results())).grid(row=0, column=3)

        systems = sorted({normalize_text(item.get("system")) for item in self.records if normalize_text(item.get("system"))})
        categories = sorted({normalize_text(item.get("category")) for item in self.records if normalize_text(item.get("category"))})
        self.k_system = tk.StringVar(value=ALL_OPTION)
        self.k_category = tk.StringVar(value=ALL_OPTION)
        ttk.Label(controls, text="辨证体系").grid(row=1, column=0, sticky="w", pady=(8, 0))
        system_box = ttk.Combobox(controls, textvariable=self.k_system, state="readonly", width=22, values=[ALL_OPTION] + systems)
        system_box.grid(row=1, column=1, sticky="w", padx=8, pady=(8, 0))
        system_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_knowledge_results())
        ttk.Label(controls, text="一级分类").grid(row=1, column=2, sticky="e", pady=(8, 0))
        category_box = ttk.Combobox(controls, textvariable=self.k_category, state="readonly", width=22, values=[ALL_OPTION] + categories)
        category_box.grid(row=1, column=3, sticky="w", pady=(8, 0))
        category_box.bind("<<ComboboxSelected>>", lambda event: self.refresh_knowledge_results())

        paned = ttk.PanedWindow(page, orient=tk.HORIZONTAL)
        paned.grid(row=2, column=0, sticky="nsew")
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="匹配结果").grid(row=0, column=0, sticky="w")
        self.k_list = tk.Listbox(left)
        self.style_listbox(self.k_list)
        self.k_list.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.k_list.bind("<<ListboxSelect>>", self.on_knowledge_selected)
        k_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.k_list.yview)
        k_scroll.grid(row=1, column=1, sticky="ns", pady=(4, 0))
        self.k_list.configure(yscrollcommand=k_scroll.set)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        ttk.Label(right, text="详情").grid(row=0, column=0, sticky="w")
        self.k_detail = ScrolledText(right, wrap=tk.WORD)
        self.style_text_widget(self.k_detail, readonly=True)
        self.k_detail.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.k_detail.configure(state=tk.DISABLED)

        buttons = ttk.Frame(page)
        buttons.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        for text, command in [
            ("新增知识库记录", lambda: self.show_knowledge_edit_page()),
            ("编辑当前记录", self.edit_current_knowledge),
            ("删除当前记录", self.delete_current_knowledge),
            ("保存知识库", lambda: messagebox.showinfo("保存成功", "知识库数据已保存，并已自动备份。") if self.save_data() else None),
            ("导入知识库", self.import_data),
            ("导出知识库", self.export_data)
        ]:
            style = "Accent.TButton" if "新增" in text or "保存" in text else ("Danger.TButton" if "删除" in text else "TButton")
            ttk.Button(buttons, text=text, command=command, style=style).pack(side=tk.LEFT, padx=(0, 8))

        self.refresh_knowledge_results()

    def score_record(self, record, tokens, raw_query):
        score = 0
        matched = set()
        syndrome = normalize_text(record.get("syndrome_name"))
        raw = normalize_text(raw_query)
        if raw and syndrome == raw:
            score += 30
            matched.add(raw)
        text_fields = [normalize_text(record.get("system")), normalize_text(record.get("category")), normalize_text(record.get("sub_category"))]
        description = normalize_text(record.get("symptom_description"))
        treatment_notes = f"{normalize_text(record.get('treatment_plan'))} {normalize_text(record.get('notes'))}"
        symptoms = [normalize_text(item) for item in record.get("symptoms", []) or []]
        for token in tokens:
            if not token:
                continue
            if syndrome and token in syndrome and syndrome != raw:
                score += 15
                matched.add(token)
            for symptom in symptoms:
                if token == symptom or token in symptom or symptom in token:
                    score += 6
                    matched.add(token)
                    break
            if description and token in description:
                score += 3
                matched.add(token)
            for value in text_fields:
                if value and token in value:
                    score += 3
                    matched.add(token)
                    break
            for formula in record.get("formulas", []) or []:
                name = normalize_text(formula.get("name"))
                if name and (token in name or name in token):
                    score += 8
                    matched.add(token)
                    break
            if treatment_notes and token in treatment_notes:
                score += 1
                matched.add(token)
        return score, sorted(matched)

    def refresh_knowledge_results(self):
        query = self.k_query.get()
        tokens = split_keywords(query)
        selected_system = self.k_system.get()
        selected_category = self.k_category.get()
        results = []
        for record in self.records:
            if selected_system != ALL_OPTION and record.get("system") != selected_system:
                continue
            if selected_category != ALL_OPTION and record.get("category") != selected_category:
                continue
            if not tokens:
                results.append((0, record, ["全部记录"]))
                continue
            score, matched = self.score_record(record, tokens, query)
            if score > 0:
                results.append((score, record, matched))
        results.sort(key=lambda item: (-item[0], normalize_text(item[1].get("syndrome_name"))))
        self.knowledge_results = results
        self.k_list.delete(0, tk.END)
        for score, record, _matched in results:
            prefix = f"分数 {score} | " if tokens else ""
            self.k_list.insert(tk.END, f"{prefix}{record.get('syndrome_name', '')} | {formula_names(record) or '未填写方剂'} | {record.get('system', '')}")
        if results:
            self.k_list.selection_set(0)
            self.show_knowledge_detail(results[0][1], results[0][2], results[0][0])
        else:
            self.selected_record = None
            self.set_text_readonly(self.k_detail, "未找到匹配记录。")
        self.set_status(f"知识库共找到 {len(results)} 条记录")

    def set_text_readonly(self, widget, content):
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        self.style_text_widget(widget, readonly=True)
        widget.configure(state=tk.DISABLED)

    def on_knowledge_selected(self, _event=None):
        selection = self.k_list.curselection()
        if not selection:
            return
        score, record, matched = self.knowledge_results[selection[0]]
        self.show_knowledge_detail(record, matched, score)

    def show_knowledge_detail(self, record, matched, score):
        self.selected_record = record
        lines = [
            f"匹配分数：{score}",
            f"匹配关键词：{'、'.join(matched) if matched else '无'}",
            "",
            f"辨证体系：{record.get('system', '')}",
            f"一级分类：{record.get('category', '')}",
            f"二级分类：{record.get('sub_category', '')}",
            f"证型/病症名称：{record.get('syndrome_name', '')}",
            "",
            "症状关键词：",
            "、".join(record.get("symptoms", []) or []),
            "",
            "完整症状描述：",
            record.get("symptom_description", ""),
            "",
            "对应方剂参考："
        ]
        formulas = record.get("formulas", []) or []
        if formulas:
            for index, formula in enumerate(formulas, start=1):
                lines.extend([
                    f"{index}. {formula.get('name', '')}",
                    f"   方剂组成：{formula.get('composition', '')}",
                    f"   用法或说明：{formula.get('usage', '')}",
                    f"   方剂备注：{formula.get('note', '')}"
                ])
        else:
            lines.append("未填写")
        lines.extend(["", "治疗方案说明：", record.get("treatment_plan", ""), "", "备注：", record.get("notes", ""), "", DISCLAIMER])
        self.set_text_readonly(self.k_detail, "\n".join(lines))

    def edit_current_knowledge(self):
        if not self.selected_record:
            messagebox.showinfo("提示", "请先选择一条知识库记录。")
            return
        self.show_knowledge_edit_page(self.selected_record)

    def delete_current_knowledge(self):
        if not self.selected_record:
            messagebox.showinfo("提示", "请先选择一条知识库记录。")
            return
        name = self.selected_record.get("syndrome_name", "")
        if not messagebox.askyesno("确认删除", f"确定删除“{name}”这条知识库记录吗？"):
            return
        self.records = [item for item in self.records if item is not self.selected_record and item.get("id") != self.selected_record.get("id")]
        self.selected_record = None
        self.set_data_dirty(True)
        self.show_knowledge_page()

    def show_knowledge_edit_page(self, record=None):
        self.current_page = "knowledge_edit"
        self.clear_content()
        record = record or {}
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        ttk.Label(page, text="编辑知识库记录" if record else "新增知识库记录", style="PageTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        canvas = tk.Canvas(page, highlightthickness=0, background=COLOR_BG)
        scroll = ttk.Scrollbar(page, orient=tk.VERTICAL, command=canvas.yview)
        form = ttk.Frame(canvas)
        form.columnconfigure(1, weight=1)
        form.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")
        self.sync_canvas_window_width(canvas, form_window)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        scroll.grid(row=1, column=1, sticky="ns")

        row = 0
        vars_map = {}
        for key, label in [
            ("system", "辨证体系/知识分类"),
            ("category", "一级分类"),
            ("sub_category", "二级分类"),
            ("syndrome_name", "证型/病症名称")
        ]:
            vars_map[key] = self.entry_row(form, row, key, label, record)
            row += 1
        text_map = {}
        symptoms_value = dict(record)
        symptoms_value["symptoms"] = "、".join(record.get("symptoms", []) or [])
        text_map["symptoms"] = self.text_row(form, row, "symptoms", "症状关键词", symptoms_value, 4)
        row += 1
        text_map["symptom_description"] = self.text_row(form, row, "symptom_description", "完整症状描述", record, 4)
        row += 1
        formula = (record.get("formulas", []) or [{}])[0] if record.get("formulas") else {}
        formula_values = {
            "formula_name": formula.get("name", ""),
            "composition": formula.get("composition", ""),
            "usage": formula.get("usage", ""),
            "formula_note": formula.get("note", "")
        }
        vars_map["formula_name"] = self.entry_row(form, row, "formula_name", "对应方剂名称", formula_values)
        row += 1
        text_map["composition"] = self.text_row(form, row, "composition", "方剂组成", formula_values, 3)
        row += 1
        text_map["usage"] = self.text_row(form, row, "usage", "用法或说明", formula_values, 3)
        row += 1
        text_map["formula_note"] = self.text_row(form, row, "formula_note", "方剂备注", formula_values, 3)
        row += 1
        text_map["treatment_plan"] = self.text_row(form, row, "treatment_plan", "治疗方案说明", record, 4)
        row += 1
        text_map["notes"] = self.text_row(form, row, "notes", "总备注", record, 3)

        buttons = ttk.Frame(page)
        buttons.grid(row=2, column=0, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="返回", command=self.show_knowledge_page, style="Ghost.TButton").pack(side=tk.RIGHT, padx=(8, 0))

        def save_form():
            syndrome_name = vars_map["syndrome_name"].get().strip()
            if not syndrome_name:
                messagebox.showwarning("提示", "请填写证型/病症名称。")
                return
            formula_obj = {
                "name": vars_map["formula_name"].get().strip(),
                "composition": self.text_get(text_map["composition"]),
                "usage": self.text_get(text_map["usage"]),
                "note": self.text_get(text_map["formula_note"])
            }
            new_record = {
                "id": record.get("id") or self.next_record_id(),
                "system": vars_map["system"].get().strip(),
                "category": vars_map["category"].get().strip(),
                "sub_category": vars_map["sub_category"].get().strip(),
                "syndrome_name": syndrome_name,
                "symptoms": split_keywords(self.text_get(text_map["symptoms"])),
                "symptom_description": self.text_get(text_map["symptom_description"]),
                "formulas": [formula_obj] if any(formula_obj.values()) else [],
                "treatment_plan": self.text_get(text_map["treatment_plan"]),
                "notes": self.text_get(text_map["notes"]),
                "created_at": record.get("created_at") or now_text(),
                "updated_at": now_text()
            }
            if record:
                for index, item in enumerate(self.records):
                    if item is record or item.get("id") == record.get("id"):
                        self.records[index] = new_record
                        break
            else:
                self.records.append(new_record)
            self.set_data_dirty(True)
            self.show_knowledge_page()

        ttk.Button(buttons, text="保存并返回", command=save_form, style="Accent.TButton").pack(side=tk.RIGHT)

    def export_data(self):
        EXPORT_DIR.mkdir(exist_ok=True)
        path = filedialog.asksaveasfilename(
            title="导出知识库",
            initialdir=str(EXPORT_DIR),
            initialfile=f"data_export_{timestamp_for_file()}.json",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            write_json(Path(path), self.records)
        except OSError as exc:
            messagebox.showerror("导出失败", f"知识库导出失败：\n{exc}")
            return
        messagebox.showinfo("导出成功", f"知识库已导出到：\n{path}")

    def import_data(self):
        path = filedialog.askopenfilename(title="导入知识库", filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        choice = messagebox.askyesnocancel("导入知识库", "导入会替换当前知识库，是否先备份当前知识库？")
        if choice is None:
            return
        try:
            with Path(path).open("r", encoding="utf-8") as file:
                imported = validate_records(json.load(file))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("导入失败", f"导入文件格式错误或无法读取：\n{exc}")
            return
        if choice:
            try:
                backup_file(DATA_PATH, "data")
            except OSError as exc:
                if not messagebox.askyesno("备份失败", f"备份当前知识库失败：\n{exc}\n\n是否继续导入？"):
                    return
        self.records = imported
        self.set_data_dirty(True)
        self.show_knowledge_page()

    # ---------------- Patient pages ----------------

    def show_patient_list_page(self):
        self.current_page = "patient_list"
        self.clear_content()
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)

        title = ttk.Frame(page)
        title.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(title, text="患者档案", style="PageTitle.TLabel").pack(side=tk.LEFT)

        controls = ttk.Frame(page)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        controls.columnconfigure(1, weight=1)
        ttk.Label(controls, text="患者检索").grid(row=0, column=0, sticky="w")
        self.p_query = tk.StringVar()
        entry = ttk.Entry(controls, textvariable=self.p_query)
        entry.grid(row=0, column=1, sticky="ew", padx=8)
        entry.bind("<Return>", lambda event: self.refresh_patient_results())
        ttk.Button(controls, text="搜索患者", command=self.refresh_patient_results).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(controls, text="清空", command=lambda: (self.p_query.set(""), self.refresh_patient_results())).grid(row=0, column=3)

        paned = ttk.PanedWindow(page, orient=tk.HORIZONTAL)
        paned.grid(row=2, column=0, sticky="nsew")
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="患者列表").grid(row=0, column=0, sticky="w")
        self.p_list = tk.Listbox(left)
        self.style_listbox(self.p_list)
        self.p_list.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.p_list.bind("<<ListboxSelect>>", self.on_patient_list_selected)
        p_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.p_list.yview)
        p_scroll.grid(row=1, column=1, sticky="ns", pady=(4, 0))
        self.p_list.configure(yscrollcommand=p_scroll.set)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        ttk.Label(right, text="档案摘要").grid(row=0, column=0, sticky="w")
        self.p_detail = ScrolledText(right, wrap=tk.WORD)
        self.style_text_widget(self.p_detail, readonly=True)
        self.p_detail.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.p_detail.configure(state=tk.DISABLED)

        buttons = ttk.Frame(page)
        buttons.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        for text, command in [
            ("新增患者", lambda: self.show_patient_edit_page()),
            ("查看患者详情", self.open_selected_patient),
            ("编辑患者", self.edit_selected_patient_from_list),
            ("删除患者", self.delete_selected_patient),
            ("保存患者档案", lambda: messagebox.showinfo("保存成功", "患者档案已保存，并已自动备份。") if self.save_patients() else None),
            ("导入患者档案", self.import_patients),
            ("导出患者档案", self.export_patients)
        ]:
            style = "Accent.TButton" if "新增" in text or "保存" in text else ("Danger.TButton" if "删除" in text else "TButton")
            ttk.Button(buttons, text=text, command=command, style=style).pack(side=tk.LEFT, padx=(0, 8))
        self.refresh_patient_results()

    def patient_matches(self, patient, tokens):
        if not tokens:
            return True
        searchable = [
            patient.get("name", ""),
            patient.get("gender", ""),
            patient.get("age", ""),
            patient.get("phone", ""),
            patient.get("address", ""),
            patient.get("allergy_history", ""),
            patient.get("past_history", ""),
            patient.get("notes", "")
        ]
        for visit in patient.get("visits", []) or []:
            searchable.extend([
                visit.get("visit_date", ""),
                visit.get("chief_complaint", ""),
                visit.get("present_illness", ""),
                visit.get("tongue_pulse", ""),
                visit.get("syndrome_record", ""),
                visit.get("formula_reference", ""),
                visit.get("treatment_plan", ""),
                visit.get("advice", ""),
                visit.get("notes", "")
            ])
            for selected in visit.get("selected_syndromes", []) or []:
                if isinstance(selected, dict):
                    searchable.extend([
                        selected.get("syndrome_name", ""),
                        selected.get("formula_names", ""),
                        selected.get("formula_reference", ""),
                        selected.get("treatment_plan", "")
                    ])
        text = "\n".join(normalize_text(item) for item in searchable)
        return all(token in text for token in tokens)

    def refresh_patient_results(self):
        tokens = split_keywords(self.p_query.get())
        self.patient_results = [patient for patient in self.patients if self.patient_matches(patient, tokens)]
        self.patient_results.sort(key=lambda item: (normalize_text(item.get("name")), normalize_text(item.get("phone"))))
        self.p_list.delete(0, tk.END)
        for patient in self.patient_results:
            self.p_list.insert(tk.END, f"{patient.get('name', '')} | {patient.get('gender', '')} {patient.get('age', '')} | {patient.get('phone', '')} | 就诊 {len(patient.get('visits', []) or [])} 次")
        if self.patient_results:
            self.p_list.selection_set(0)
            self.show_patient_summary(self.patient_results[0])
        else:
            self.selected_patient = None
            self.set_text_readonly(self.p_detail, "未找到患者档案。")
        self.set_status(f"共找到 {len(self.patient_results)} 个患者档案")

    def on_patient_list_selected(self, _event=None):
        selection = self.p_list.curselection()
        if not selection:
            return
        self.show_patient_summary(self.patient_results[selection[0]])

    def show_patient_summary(self, patient):
        self.selected_patient = patient
        visits = sorted(patient.get("visits", []) or [], key=lambda item: normalize_text(item.get("visit_date")), reverse=True)
        lines = [
            f"姓名：{self.display_value(patient.get('name'))}",
            f"性别：{self.display_value(patient.get('gender'))}",
            f"年龄：{self.display_value(patient.get('age'))}",
            f"联系电话：{self.display_value(patient.get('phone'))}",
            f"联系地址：{self.display_value(patient.get('address'))}",
            "",
            f"就诊次数：{len(visits)}",
            f"最近就诊：{visits[0].get('visit_date', '') if visits else '暂无'}",
        ]
        self.add_display_section(lines, "过敏史", patient.get("allergy_history"))
        self.add_display_section(lines, "既往史", patient.get("past_history"))
        lines.extend(["", "最近就诊摘要："])
        if visits:
            visit = visits[0]
            self.add_display_section(lines, "主诉", visit.get("chief_complaint"))
            self.add_display_section(lines, "辨证记录", visit.get("syndrome_record"))
            self.add_display_section(lines, "方剂参考", visit.get("formula_reference"))
        else:
            lines.append("暂无就诊记录。")
        self.set_text_readonly(self.p_detail, "\n".join(lines))

    def open_selected_patient(self):
        if not self.selected_patient:
            messagebox.showinfo("提示", "请先选择一个患者。")
            return
        self.show_patient_detail_page(self.selected_patient)

    def edit_selected_patient_from_list(self):
        if not self.selected_patient:
            messagebox.showinfo("提示", "请先选择一个患者。")
            return
        self.show_patient_edit_page(self.selected_patient)

    def show_patient_detail_page(self, patient):
        self.current_page = "patient_detail"
        self.selected_patient = patient
        self.clear_content()
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)

        head = ttk.Frame(page)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(head, text=f"患者详情：{patient.get('name', '')}", style="PageTitle.TLabel").pack(side=tk.LEFT)
        ttk.Button(head, text="返回患者列表", command=self.show_patient_list_page, style="Ghost.TButton").pack(side=tk.RIGHT)

        paned = ttk.PanedWindow(page, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew")
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=2)

        left.columnconfigure(0, weight=1)
        left.rowconfigure(3, weight=1)
        profile_text = self.patient_profile_text(patient)
        profile_height = min(10, max(5, len(profile_text.splitlines())))
        profile = ScrolledText(left, height=profile_height, wrap=tk.WORD)
        self.style_text_widget(profile, readonly=True)
        profile.grid(row=0, column=0, sticky="ew")
        profile.insert("1.0", profile_text)
        profile.configure(state=tk.DISABLED)
        btns1 = ttk.Frame(left)
        btns1.grid(row=1, column=0, sticky="ew", pady=8)
        ttk.Button(btns1, text="编辑患者信息", command=lambda: self.show_patient_edit_page(patient)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns1, text="新增就诊记录", command=lambda: self.show_visit_edit_page(patient), style="Accent.TButton").pack(side=tk.LEFT)

        ttk.Label(left, text="历史就诊").grid(row=2, column=0, sticky="sw")
        self.visit_list = tk.Listbox(left, height=12)
        self.style_listbox(self.visit_list)
        self.visit_list.grid(row=3, column=0, sticky="nsew", pady=(4, 0))
        self.visit_list.bind("<<ListboxSelect>>", self.on_visit_selected)
        visits = sorted(patient.get("visits", []) or [], key=lambda item: normalize_text(item.get("visit_date")), reverse=True)
        self.visible_visits = visits
        for visit in visits:
            summary = normalize_text(visit.get("chief_complaint")) or normalize_text(visit.get("syndrome_record")) or "未填写主诉"
            self.visit_list.insert(tk.END, f"{visit.get('visit_date', '')} | {summary[:40]}")

        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        ttk.Label(right, text="就诊详情").grid(row=0, column=0, sticky="w")
        self.visit_detail = ScrolledText(right, wrap=tk.WORD)
        self.style_text_widget(self.visit_detail, readonly=True)
        self.visit_detail.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.visit_detail.configure(state=tk.DISABLED)
        visit_buttons = ttk.Frame(right)
        visit_buttons.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        for text, command in [
            ("编辑当前就诊", self.edit_current_visit),
            ("删除当前就诊", self.delete_current_visit),
            ("打印当前病历", self.print_current_visit),
            ("保存患者档案", lambda: messagebox.showinfo("保存成功", "患者档案已保存，并已自动备份。") if self.save_patients() else None)
        ]:
            style = "Accent.TButton" if "打印" in text or "保存" in text else ("Danger.TButton" if "删除" in text else "TButton")
            ttk.Button(visit_buttons, text=text, command=command, style=style).pack(side=tk.LEFT, padx=(0, 8))

        if visits:
            self.visit_list.selection_set(0)
            self.show_visit_detail(visits[0])
        else:
            self.selected_visit = None
            self.set_text_readonly(self.visit_detail, "当前患者暂无就诊记录。")

    def patient_profile_text(self, patient):
        lines = [
            f"姓名：{self.display_value(patient.get('name'))}",
            f"性别：{self.display_value(patient.get('gender'))}",
            f"年龄：{self.display_value(patient.get('age'))}",
            f"联系电话：{self.display_value(patient.get('phone'))}",
            f"联系地址：{self.display_value(patient.get('address'))}"
        ]
        self.add_display_section(lines, "过敏史", patient.get("allergy_history"))
        self.add_display_section(lines, "既往史", patient.get("past_history"))
        self.add_display_section(lines, "患者备注", patient.get("notes"))
        lines.extend([
            f"建档时间：{self.display_value(patient.get('created_at'))}",
            f"更新时间：{self.display_value(patient.get('updated_at'))}"
        ])
        return "\n".join(lines)

    def on_visit_selected(self, _event=None):
        selection = self.visit_list.curselection()
        if not selection:
            return
        self.show_visit_detail(self.visible_visits[selection[0]])

    def show_visit_detail(self, visit):
        self.selected_visit = visit
        self.set_text_readonly(self.visit_detail, self.visit_text(self.selected_patient, visit, include_patient=False))

    def visit_text(self, patient, visit, include_patient=True):
        def add_section(target, label, value):
            value = normalize_text(value)
            target.append(f"{label}：{value if value else '未填写'}" if "\n" not in value else f"{label}：\n{value}")

        lines = []
        if include_patient:
            lines.extend([
                APP_TITLE,
                "门诊病历记录",
                "",
                f"打印时间：{now_text()}",
                "",
                "患者信息",
                f"姓名：{self.display_value(patient.get('name'))}",
                f"性别：{self.display_value(patient.get('gender'))}",
                f"年龄：{self.display_value(patient.get('age'))}",
                f"联系电话：{self.display_value(patient.get('phone'))}",
                f"联系地址：{self.display_value(patient.get('address'))}"
            ])
        lines.extend([
            "就诊记录",
            f"就诊日期：{self.display_value(visit.get('visit_date'))}"
        ])
        for label, key in [
            ("主诉", "chief_complaint"),
            ("现病情况/症状记录", "present_illness"),
            ("辨证记录/病症记录", "syndrome_record"),
            ("方剂参考/处理方案", "formula_reference"),
            ("治疗方案说明", "treatment_plan"),
            ("既往史", "past_history"),
            ("过敏史", "allergy_history"),
            ("随访与注意事项", "advice"),
            ("本次备注", "notes")
        ]:
            source = patient if key in {"past_history", "allergy_history"} else visit
            add_section(lines, label, source.get(key, ""))
        lines.append("")
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def html_value(self, value):
        return html.escape(self.display_value(value)).replace("\n", "<br>")

    def html_section(self, title, value):
        value = normalize_text(value)
        body = html.escape(value).replace("\n", "<br>") if value else '<span class="empty">未填写</span>'
        return f"""
        <section class="section">
          <h2>{html.escape(title)}</h2>
          <div class="section-body">{body}</div>
        </section>
        """

    def build_print_html(self, patient, visit):
        rows = [
            ("姓名", patient.get("name"), "性别", patient.get("gender")),
            ("年龄", patient.get("age"), "联系电话", patient.get("phone")),
            ("联系地址", patient.get("address"), "就诊日期", visit.get("visit_date")),
            ("打印时间", now_text(), "病历编号", f"P{patient.get('id', '')}-V{visit.get('id', '')}")
        ]
        table_rows = "\n".join(
            f"<tr><th>{html.escape(a)}</th><td>{self.html_value(b)}</td><th>{html.escape(c)}</th><td>{self.html_value(d)}</td></tr>"
            for a, b, c, d in rows
        )
        sections = "\n".join([
            self.html_section("主诉", visit.get("chief_complaint")),
            self.html_section("现病情况 / 症状记录", visit.get("present_illness")),
            self.html_section("辨证记录 / 病症记录", visit.get("syndrome_record")),
            self.html_section("方剂参考 / 处理方案", visit.get("formula_reference")),
            self.html_section("治疗方案说明", visit.get("treatment_plan")),
            self.html_section("既往史", patient.get("past_history")),
            self.html_section("过敏史", patient.get("allergy_history")),
            self.html_section("随访与注意事项", visit.get("advice")),
            self.html_section("本次备注", visit.get("notes"))
        ])
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>门诊病历_{html.escape(self.display_value(patient.get('name')))}</title>
  <style>
    @page {{ size: A4; margin: 11mm; }}
    body {{ font-family: "Microsoft YaHei", "SimSun", sans-serif; color: #17211c; font-size: 12px; line-height: 1.38; }}
    .title {{ text-align: center; font-size: 20px; font-weight: 700; margin: 0 0 2px; }}
    .subtitle {{ text-align: center; color: #66746c; margin: 0 0 8px; font-size: 11px; }}
    table.info {{ width: 100%; border-collapse: collapse; margin-bottom: 7px; table-layout: fixed; }}
    table.info th, table.info td {{ border: 1px solid #9fb7ad; padding: 4px 6px; vertical-align: top; }}
    table.info th {{ width: 16%; background: #edf3ef; text-align: right; font-weight: 700; }}
    table.info td {{ width: 34%; }}
    .section {{ margin-top: 6px; break-inside: avoid; }}
    .section h2 {{ font-size: 13px; border-left: 3px solid #1f7a6d; padding-left: 6px; margin: 0 0 3px; }}
    .section-body {{ border: 1px solid #cfd8d2; padding: 5px 7px; min-height: 14px; white-space: normal; }}
    .empty {{ color: #88958e; }}
    .notice {{ margin-top: 8px; padding-top: 5px; border-top: 1px solid #cfd8d2; color: #66746c; font-size: 10px; }}
    .signature {{ margin-top: 18px; text-align: right; font-size: 13px; }}
    .signature span {{ display: inline-block; min-width: 120px; border-bottom: 1px solid #17211c; margin-left: 6px; }}
  </style>
</head>
<body>
  <h1 class="title">门诊病历单</h1>
  <p class="subtitle">{html.escape(APP_TITLE)}</p>
  <table class="info">{table_rows}</table>
  {sections}
  <div class="signature">门诊医生：<span></span> 日期：<span></span></div>
  <div class="notice">{html.escape(DISCLAIMER)}</div>
</body>
</html>"""

    def show_patient_edit_page(self, patient=None):
        self.current_page = "patient_edit"
        self.clear_content()
        patient = patient or {}
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        ttk.Label(page, text="编辑患者信息" if patient else "新增患者", style="PageTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        form = ttk.Frame(page)
        form.grid(row=1, column=0, sticky="nsew")
        form.columnconfigure(1, weight=1)
        vars_map = {}
        row = 0
        for key, label in [
            ("name", "患者姓名"),
            ("gender", "性别"),
            ("age", "年龄"),
            ("phone", "联系电话"),
            ("address", "联系地址")
        ]:
            vars_map[key] = self.entry_row(form, row, key, label, patient)
            row += 1
        text_map = {}
        text_map["allergy_history"] = self.text_row(form, row, "allergy_history", "过敏史", patient, 3)
        row += 1
        text_map["past_history"] = self.text_row(form, row, "past_history", "既往史", patient, 4)
        row += 1
        text_map["notes"] = self.text_row(form, row, "notes", "患者备注", patient, 4)

        buttons = ttk.Frame(page)
        buttons.grid(row=2, column=0, sticky="e", pady=(8, 0))
        back_cmd = (lambda: self.show_patient_detail_page(patient)) if patient else self.show_patient_list_page
        ttk.Button(buttons, text="返回", command=back_cmd, style="Ghost.TButton").pack(side=tk.RIGHT, padx=(8, 0))

        def save_form():
            name = vars_map["name"].get().strip()
            if not name:
                messagebox.showwarning("提示", "请填写患者姓名。")
                return
            new_patient = {
                "id": patient.get("id") or self.next_patient_id(),
                "name": name,
                "gender": vars_map["gender"].get().strip(),
                "age": vars_map["age"].get().strip(),
                "phone": vars_map["phone"].get().strip(),
                "address": vars_map["address"].get().strip(),
                "allergy_history": self.text_get(text_map["allergy_history"]),
                "past_history": self.text_get(text_map["past_history"]),
                "notes": self.text_get(text_map["notes"]),
                "visits": patient.get("visits", []) or [],
                "created_at": patient.get("created_at") or now_text(),
                "updated_at": now_text()
            }
            if patient:
                for index, item in enumerate(self.patients):
                    if item is patient or item.get("id") == patient.get("id"):
                        self.patients[index] = new_patient
                        break
            else:
                self.patients.append(new_patient)
            self.set_patient_dirty(True)
            self.show_patient_detail_page(new_patient)

        ttk.Button(buttons, text="保存并进入档案", command=save_form, style="Accent.TButton").pack(side=tk.RIGHT)

    def delete_selected_patient(self):
        if not self.selected_patient:
            messagebox.showinfo("提示", "请先选择一个患者。")
            return
        name = self.selected_patient.get("name", "")
        if not messagebox.askyesno("确认删除", f"确定删除“{name}”的患者档案及全部就诊记录吗？"):
            return
        self.patients = [item for item in self.patients if item is not self.selected_patient and item.get("id") != self.selected_patient.get("id")]
        self.selected_patient = None
        self.selected_visit = None
        self.set_patient_dirty(True)
        self.show_patient_list_page()

    # ---------------- Visit edit and linkage ----------------

    def show_visit_edit_page(self, patient, visit=None):
        self.current_page = "visit_edit"
        self.selected_patient = patient
        self.clear_content()
        visit = visit or {}
        selected_syndromes = list(visit.get("selected_syndromes", []) or [])

        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        ttk.Label(page, text=f"{patient.get('name', '')} - {'编辑就诊记录' if visit else '新增就诊记录'}", style="PageTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        paned = ttk.PanedWindow(page, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew")
        form_frame = ttk.Frame(paned)
        link_frame = ttk.Frame(paned)
        paned.add(form_frame, weight=2)
        paned.add(link_frame, weight=1)

        form_frame.columnconfigure(0, weight=1)
        form_frame.rowconfigure(0, weight=1)
        canvas = tk.Canvas(form_frame, highlightthickness=0, background=COLOR_BG)
        scroll = ttk.Scrollbar(form_frame, orient=tk.VERTICAL, command=canvas.yview)
        form = ttk.Frame(canvas)
        form.columnconfigure(1, weight=1)
        form.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        form_window = canvas.create_window((0, 0), window=form, anchor="nw")
        self.sync_canvas_window_width(canvas, form_window)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        row = 0
        vars_map = {"visit_date": self.entry_row(form, row, "visit_date", "就诊日期", {"visit_date": visit.get("visit_date") or today_text()})}
        row += 1
        text_map = {}
        for key, label, height in [
            ("chief_complaint", "主诉", 3),
            ("present_illness", "现病情况/症状记录", 5),
            ("syndrome_record", "辨证记录/病症记录", 5),
            ("formula_reference", "方剂参考/处理方案", 5),
            ("treatment_plan", "治疗方案说明", 4),
            ("advice", "随访与注意事项", 3),
            ("notes", "本次备注", 3)
        ]:
            text_map[key] = self.text_row(form, row, key, label, visit, height)
            row += 1

        link_frame.columnconfigure(0, weight=1)
        link_frame.rowconfigure(4, weight=2)
        link_frame.rowconfigure(6, weight=2)
        link_frame.rowconfigure(8, weight=1)
        ttk.Label(link_frame, text="知识库联动", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(link_frame, text="先点击结果查看详情，再勾选加入本次病历。", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 8))
        link_query = tk.StringVar()
        link_entry = ttk.Entry(link_frame, textvariable=link_query)
        link_entry.grid(row=2, column=0, sticky="ew")
        buttons = ttk.Frame(link_frame)
        buttons.grid(row=3, column=0, sticky="ew", pady=6)
        link_list = tk.Listbox(link_frame, selectmode=tk.SINGLE, exportselection=False)
        self.style_listbox(link_list)
        link_list.grid(row=4, column=0, sticky="nsew")
        link_scroll = ttk.Scrollbar(link_frame, orient=tk.VERTICAL, command=link_list.yview)
        link_scroll.grid(row=4, column=1, sticky="ns")
        link_list.configure(yscrollcommand=link_scroll.set)
        ttk.Label(link_frame, text="病症详情", style="Section.TLabel").grid(row=5, column=0, sticky="w", pady=(8, 2))
        link_detail = ScrolledText(link_frame, height=8, wrap=tk.WORD)
        self.style_text_widget(link_detail, readonly=True)
        link_detail.grid(row=6, column=0, sticky="nsew")
        link_detail.configure(state=tk.DISABLED)
        ttk.Label(link_frame, text="已加入本次病历", style="Section.TLabel").grid(row=7, column=0, sticky="w", pady=(8, 2))
        selected_list = tk.Listbox(link_frame, height=5, exportselection=False)
        self.style_listbox(selected_list)
        selected_list.grid(row=8, column=0, sticky="nsew")
        selected_scroll = ttk.Scrollbar(link_frame, orient=tk.VERTICAL, command=selected_list.yview)
        selected_scroll.grid(row=8, column=1, sticky="ns")
        selected_list.configure(yscrollcommand=selected_scroll.set)
        selected_buttons = ttk.Frame(link_frame)
        selected_buttons.grid(row=9, column=0, sticky="ew", pady=(6, 0))

        link_results = []
        link_labels = []
        checked = set()

        def reset_link_list():
            link_results.clear()
            link_labels.clear()
            checked.clear()
            link_list.delete(0, tk.END)
            set_link_detail("请先检索并点击某条结果查看详情。")

        def add_link_item(item, label):
            link_results.append(item)
            link_labels.append(label)
            link_list.insert(tk.END, f"[ ] {label}")

        def set_link_detail(content):
            link_detail.configure(state=tk.NORMAL)
            link_detail.delete("1.0", tk.END)
            link_detail.insert(tk.END, content)
            link_detail.configure(state=tk.DISABLED)

        def selected_to_detail(selected):
            lines = [
                f"证型/病症名称：{selected.get('syndrome_name', '')}",
                f"辨证体系：{selected.get('system', '')}",
                f"一级分类：{selected.get('category', '')}",
                f"二级分类：{selected.get('sub_category', '')}",
                "",
                "症状关键词：",
                "、".join(selected.get("symptoms", []) or []),
                "",
                "症状描述：",
                selected.get("symptom_description", ""),
                "",
                "方剂参考：",
                selected.get("formula_reference", "") or selected.get("formula_names", ""),
                "",
                "治疗方案说明：",
                selected.get("treatment_plan", "")
            ]
            return "\n".join(lines)

        def record_detail_text(item):
            if item["kind"] == "history":
                return selected_to_detail(item["history"])
            record = item["record"]
            formula_lines = []
            for index, formula in enumerate(record.get("formulas", []) or [], start=1):
                formula_lines.extend([
                    f"{index}. {formula.get('name', '')}",
                    f"   组成：{formula.get('composition', '')}",
                    f"   说明：{formula.get('usage', '')}",
                    f"   备注：{formula.get('note', '')}"
                ])
            lines = [
                f"匹配分数：{item.get('score', '')}",
                f"匹配关键词：{'、'.join(item.get('matched', [])) if item.get('matched') else '无'}",
                "",
                f"证型/病症名称：{record.get('syndrome_name', '')}",
                f"辨证体系：{record.get('system', '')}",
                f"一级分类：{record.get('category', '')}",
                f"二级分类：{record.get('sub_category', '')}",
                "",
                "症状关键词：",
                "、".join(record.get("symptoms", []) or []),
                "",
                "完整症状描述：",
                record.get("symptom_description", ""),
                "",
                "对应方剂参考：",
                "\n".join(formula_lines) if formula_lines else "未填写",
                "",
                "治疗方案说明：",
                record.get("treatment_plan", ""),
                "",
                "备注：",
                record.get("notes", "")
            ]
            return "\n".join(lines)

        def show_link_detail(_event=None):
            selection = link_list.curselection()
            if not selection:
                return
            index = selection[0]
            if 0 <= index < len(link_results):
                set_link_detail(record_detail_text(link_results[index]))

        def toggle_checked_index(index):
            if not link_results:
                return
            if index < 0 or index >= len(link_results):
                return
            if index in checked:
                checked.remove(index)
                prefix = "[ ]"
            else:
                checked.add(index)
                prefix = "[√]"
            link_list.delete(index)
            link_list.insert(index, f"{prefix} {link_labels[index]}")
            link_list.selection_clear(0, tk.END)
            link_list.selection_set(index)
            show_link_detail()

        def toggle_current_checked():
            selection = link_list.curselection()
            if not selection:
                messagebox.showinfo("提示", "请先点击一条检索结果查看详情。")
                return
            toggle_checked_index(selection[0])

        def toggle_checked_by_double_click(event):
            toggle_checked_index(link_list.nearest(event.y))

        def refresh_selected_list():
            selected_list.delete(0, tk.END)
            for item in selected_syndromes:
                if not isinstance(item, dict):
                    continue
                name = normalize_text(item.get("syndrome_name"))
                formula = normalize_text(item.get("formula_names")) or normalize_text(item.get("formula_reference"))
                selected_list.insert(tk.END, f"{name} | {formula[:36]}")

        def remove_named_block(widget, name):
            marker = f"【{name}】"
            content = self.text_get(widget)
            if marker not in content:
                return
            blocks = re.split(r"\n\s*\n", content)
            kept = [block.strip() for block in blocks if marker not in block]
            self.text_set(widget, "\n\n".join(block for block in kept if block))

        def remove_selected_syndrome():
            selection = selected_list.curselection()
            if not selection:
                messagebox.showinfo("提示", "请先在“已加入本次病历”中选择一个病症。")
                return
            index = selection[0]
            if index < 0 or index >= len(selected_syndromes):
                return
            item = selected_syndromes.pop(index)
            name = normalize_text(item.get("syndrome_name")) if isinstance(item, dict) else ""
            if name:
                remove_named_block(text_map["syndrome_record"], name)
                remove_named_block(text_map["formula_reference"], name)
                remove_named_block(text_map["treatment_plan"], name)
            refresh_selected_list()
            set_link_detail(f"已移除：{name}\n\n如果病历正文中有医生手动补充的相关内容，请按需要再检查调整。")

        link_list.bind("<<ListboxSelect>>", show_link_detail)
        link_list.bind("<Double-Button-1>", toggle_checked_by_double_click)

        def search_links():
            raw_query = link_query.get().strip()
            if not raw_query:
                raw_query = f"{self.text_get(text_map['chief_complaint'])} {self.text_get(text_map['present_illness'])}".strip()
            tokens = split_keywords(raw_query)
            reset_link_list()
            if not tokens:
                messagebox.showinfo("提示", "请先输入症状关键词，或填写主诉/症状记录。")
                return
            found = []
            for record in self.records:
                score, matched = self.score_record(record, tokens, raw_query)
                if score > 0:
                    found.append({"kind": "record", "record": record, "score": score, "matched": matched})
            found.sort(key=lambda item: (-item["score"], normalize_text(item["record"].get("syndrome_name"))))
            for item in found:
                record = item["record"]
                matched = "、".join(item["matched"]) if item["matched"] else "无"
                add_link_item(item, f"分数 {item['score']} | {record.get('syndrome_name', '')} | {formula_names(record) or '未填写方剂'} | 匹配：{matched}")
            if not found:
                messagebox.showinfo("提示", "未检索到匹配病症，可调整关键词或先维护知识库。")

        def history_links():
            reset_link_list()
            seen = set()
            for old_visit in patient.get("visits", []) or []:
                if visit and old_visit.get("id") == visit.get("id"):
                    continue
                selected = old_visit.get("selected_syndromes", []) or []
                for item in selected:
                    if not isinstance(item, dict):
                        continue
                    name = normalize_text(item.get("syndrome_name"))
                    if not name or name in seen:
                        continue
                    seen.add(name)
                    add_link_item({"kind": "history", "history": item}, f"历史 | {name} | {item.get('formula_names', '') or item.get('formula_reference', '')} | {old_visit.get('visit_date', '')}")
                if not selected and normalize_text(old_visit.get("syndrome_record")):
                    name = normalize_text(old_visit.get("syndrome_record")).splitlines()[0].replace("【", "").replace("】", "")
                    if name and name not in seen:
                        seen.add(name)
                        item = {
                            "syndrome_name": name,
                            "formula_reference": old_visit.get("formula_reference", ""),
                            "treatment_plan": old_visit.get("treatment_plan", "")
                        }
                        add_link_item({"kind": "history", "history": item}, f"历史 | {name} | {old_visit.get('formula_reference', '')[:24]} | {old_visit.get('visit_date', '')}")
            if not link_results:
                messagebox.showinfo("提示", "当前患者暂无可复用的历史病症。")

        def record_to_selected(record):
            formula_lines = []
            for formula in record.get("formulas", []) or []:
                parts = [normalize_text(formula.get("name"))]
                if normalize_text(formula.get("composition")):
                    parts.append(f"组成：{normalize_text(formula.get('composition'))}")
                if normalize_text(formula.get("usage")):
                    parts.append(f"说明：{normalize_text(formula.get('usage'))}")
                if normalize_text(formula.get("note")):
                    parts.append(f"备注：{normalize_text(formula.get('note'))}")
                formula_lines.append("；".join(part for part in parts if part))
            return {
                "record_id": record.get("id"),
                "syndrome_name": record.get("syndrome_name", ""),
                "system": record.get("system", ""),
                "category": record.get("category", ""),
                "sub_category": record.get("sub_category", ""),
                "symptoms": record.get("symptoms", []) or [],
                "symptom_description": record.get("symptom_description", ""),
                "formula_names": formula_names(record),
                "formula_reference": "\n".join(formula_lines),
                "treatment_plan": record.get("treatment_plan", "")
            }

        def apply_checked():
            if not checked:
                messagebox.showinfo("提示", "请先在列表中勾选一个或多个病症。")
                return
            existing = {normalize_text(item.get("syndrome_name")) for item in selected_syndromes if isinstance(item, dict)}
            added = 0
            for index in sorted(checked):
                item = link_results[index]
                selected = record_to_selected(item["record"]) if item["kind"] == "record" else dict(item["history"])
                name = normalize_text(selected.get("syndrome_name"))
                if not name or name in existing:
                    continue
                existing.add(name)
                selected_syndromes.append(selected)
                syndrome_line = f"【{name}】{selected.get('system', '')} {selected.get('category', '')} {selected.get('sub_category', '')}".strip()
                symptoms = selected.get("symptoms", []) or []
                if symptoms:
                    syndrome_line += f"\n症状关键词：{'、'.join(symptoms)}"
                if selected.get("symptom_description"):
                    syndrome_line += f"\n症状描述：{selected.get('symptom_description')}"
                self.append_text(text_map["syndrome_record"], syndrome_line)
                formula_text = selected.get("formula_reference") or selected.get("formula_names") or ""
                if formula_text:
                    self.append_text(text_map["formula_reference"], f"【{name}】\n{formula_text}")
                if selected.get("treatment_plan"):
                    self.append_text(text_map["treatment_plan"], f"【{name}】\n{selected.get('treatment_plan')}")
                added += 1
            refresh_selected_list()
            messagebox.showinfo("已加入", f"已将 {added} 个病症及对应方剂加入本次就诊记录。" if added else "勾选的病症已在本次就诊记录中。")

        ttk.Button(buttons, text="检索病症", command=search_links, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="显示历史病症", command=history_links).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="勾选/取消当前", command=toggle_current_checked).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="加入勾选", command=apply_checked, style="Accent.TButton").pack(side=tk.LEFT)
        ttk.Button(selected_buttons, text="移除已加入", command=remove_selected_syndrome, style="Danger.TButton").pack(side=tk.LEFT)
        refresh_selected_list()
        set_link_detail("请先检索并点击某条结果查看详情。")

        bottom = ttk.Frame(page)
        bottom.grid(row=2, column=0, sticky="e", pady=(8, 0))
        ttk.Button(bottom, text="返回患者详情", command=lambda: self.show_patient_detail_page(patient), style="Ghost.TButton").pack(side=tk.RIGHT, padx=(8, 0))

        def save_visit():
            new_visit = {
                "id": visit.get("id") or self.next_visit_id(patient),
                "visit_date": vars_map["visit_date"].get().strip() or today_text(),
                "chief_complaint": self.text_get(text_map["chief_complaint"]),
                "present_illness": self.text_get(text_map["present_illness"]),
                "tongue_pulse": visit.get("tongue_pulse", ""),
                "syndrome_record": self.text_get(text_map["syndrome_record"]),
                "formula_reference": self.text_get(text_map["formula_reference"]),
                "treatment_plan": self.text_get(text_map["treatment_plan"]),
                "advice": self.text_get(text_map["advice"]),
                "notes": self.text_get(text_map["notes"]),
                "selected_syndromes": selected_syndromes,
                "created_at": visit.get("created_at") or now_text(),
                "updated_at": now_text()
            }
            if visit:
                visits = patient.get("visits", []) or []
                for index, item in enumerate(visits):
                    if item is visit or item.get("id") == visit.get("id"):
                        visits[index] = new_visit
                        break
                patient["visits"] = visits
            else:
                patient.setdefault("visits", []).append(new_visit)
            patient["updated_at"] = now_text()
            self.set_patient_dirty(True)
            self.show_patient_detail_page(patient)

        ttk.Button(bottom, text="保存并返回", command=save_visit, style="Accent.TButton").pack(side=tk.RIGHT)

        seed_query = f"{visit.get('chief_complaint', '')} {visit.get('present_illness', '')}".strip()
        link_query.set(seed_query)

    def edit_current_visit(self):
        if not self.selected_patient or not self.selected_visit:
            messagebox.showinfo("提示", "请先选择一条就诊记录。")
            return
        self.show_visit_edit_page(self.selected_patient, self.selected_visit)

    def delete_current_visit(self):
        if not self.selected_patient or not self.selected_visit:
            messagebox.showinfo("提示", "请先选择一条就诊记录。")
            return
        if not messagebox.askyesno("确认删除", "确定删除当前就诊记录吗？"):
            return
        self.selected_patient["visits"] = [
            item for item in self.selected_patient.get("visits", []) or []
            if item is not self.selected_visit and item.get("id") != self.selected_visit.get("id")
        ]
        self.selected_patient["updated_at"] = now_text()
        self.selected_visit = None
        self.set_patient_dirty(True)
        self.show_patient_detail_page(self.selected_patient)

    # ---------------- Print and patient import/export ----------------

    def print_current_visit(self):
        if not self.selected_patient or not self.selected_visit:
            messagebox.showinfo("提示", "请先选择一条就诊记录。")
            return
        self.show_print_preview_page(self.selected_patient, self.selected_visit)

    def show_print_preview_page(self, patient, visit):
        self.current_page = "print_preview"
        self.clear_content()
        page = ttk.Frame(self.content)
        page.grid(row=0, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        ttk.Label(page, text="打印预览", style="PageTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        preview = ScrolledText(page, wrap=tk.WORD)
        self.style_text_widget(preview)
        preview.grid(row=1, column=0, sticky="nsew")
        preview.insert("1.0", self.visit_text(patient, visit, include_patient=True))
        preview.configure(state=tk.DISABLED)

        buttons = ttk.Frame(page)
        buttons.grid(row=2, column=0, sticky="e", pady=(8, 0))
        ttk.Button(buttons, text="返回患者详情", command=lambda: self.show_patient_detail_page(patient), style="Ghost.TButton").pack(side=tk.RIGHT, padx=(8, 0))

        def create_print_file():
            PRINT_DIR.mkdir(parents=True, exist_ok=True)
            print_path = PRINT_DIR / f"门诊病历_{sanitize_filename(patient.get('name'))}_{timestamp_for_file()}.html"
            try:
                print_path.write_text(self.build_print_html(patient, visit), encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("打印失败", f"打印文件生成失败：\n{exc}")
                return None
            return print_path

        def open_print_file(print_path):
            if not print_path:
                return
            print_path = Path(print_path).resolve()
            errors = []
            try:
                if webbrowser.open_new_tab(print_path.as_uri()):
                    return True
            except Exception as exc:
                errors.append(f"浏览器打开失败：{exc}")
            if hasattr(os, "startfile"):
                try:
                    os.startfile(str(print_path), "open")
                    return True
                except OSError as exc:
                    errors.append(f"系统打开失败：{exc}")
            try:
                subprocess.Popen(["explorer", f"/select,{print_path}"])
            except OSError as exc:
                errors.append(f"打开所在文件夹失败：{exc}")
            messagebox.showwarning(
                "打开提示",
                "病历单文件已生成，但未能自动用浏览器打开。\n\n"
                f"文件位置：\n{print_path}\n\n"
                "已尝试打开所在文件夹，请双击该 HTML 文件后按 Ctrl+P 打印。\n\n"
                + "\n".join(errors)
            )
            return False

        def open_record_file():
            print_path = create_print_file()
            if open_print_file(print_path):
                messagebox.showinfo("病历单已打开", "病历单已在浏览器中打开，可按 Ctrl+P 打印。")

        def do_print():
            print_path = create_print_file()
            if not print_path:
                return
            if hasattr(os, "startfile"):
                try:
                    os.startfile(str(print_path), "print")
                    messagebox.showinfo("打印", f"已生成打印文件，并尝试发送到默认打印机。\n\n文件位置：\n{print_path}")
                except OSError as exc:
                    opened = open_print_file(print_path)
                    extra = "\n\n已自动打开病历单，请在浏览器中按 Ctrl+P 打印。" if opened else f"\n\n请手动打开文件打印：\n{print_path}"
                    messagebox.showwarning("打印提示", f"打印文件已生成，但调用默认打印机失败：\n{exc}{extra}")
            else:
                open_print_file(print_path)

        def open_print_folder():
            PRINT_DIR.mkdir(parents=True, exist_ok=True)
            if hasattr(os, "startfile"):
                try:
                    os.startfile(str(PRINT_DIR))
                    return
                except OSError as exc:
                    messagebox.showwarning("打开失败", f"无法打开打印文件夹：\n{exc}\n\n文件夹位置：\n{PRINT_DIR}")
                    return
            messagebox.showinfo("打印文件夹", f"请手动打开文件夹：\n{PRINT_DIR}")

        ttk.Button(buttons, text="直接打印", command=do_print, style="Accent.TButton").pack(side=tk.RIGHT)
        ttk.Button(buttons, text="打开病历单", command=open_record_file).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(buttons, text="打开打印文件夹", command=open_print_folder).pack(side=tk.RIGHT, padx=(0, 8))

    def export_patients(self):
        EXPORT_DIR.mkdir(exist_ok=True)
        path = filedialog.asksaveasfilename(
            title="导出患者档案",
            initialdir=str(EXPORT_DIR),
            initialfile=f"patients_export_{timestamp_for_file()}.json",
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            write_json(Path(path), self.patients)
        except OSError as exc:
            messagebox.showerror("导出失败", f"患者档案导出失败：\n{exc}")
            return
        messagebox.showinfo("导出成功", f"患者档案已导出到：\n{path}")

    def import_patients(self):
        path = filedialog.askopenfilename(title="导入患者档案", filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")])
        if not path:
            return
        choice = messagebox.askyesnocancel("导入患者档案", "导入会替换当前患者档案，是否先备份当前患者档案？")
        if choice is None:
            return
        try:
            with Path(path).open("r", encoding="utf-8") as file:
                imported = validate_patients(json.load(file))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("导入失败", f"导入文件格式错误或无法读取：\n{exc}")
            return
        if choice:
            try:
                backup_file(PATIENT_PATH, "patients")
            except OSError as exc:
                if not messagebox.askyesno("备份失败", f"备份当前患者档案失败：\n{exc}\n\n是否继续导入？"):
                    return
        self.patients = imported
        self.set_patient_dirty(True)
        self.show_patient_list_page()

    def on_close(self):
        if self.data_dirty:
            choice = messagebox.askyesnocancel("知识库未保存", "知识库数据有未保存修改，是否先保存？")
            if choice is None:
                return
            if choice and not self.save_data():
                return
        if self.patient_dirty:
            choice = messagebox.askyesnocancel("患者档案未保存", "患者档案有未保存修改，是否先保存？")
            if choice is None:
                return
            if choice and not self.save_patients():
                return
        self.root.destroy()


def main():
    root = tk.Tk()
    setup_theme(root)
    MainWindowApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
