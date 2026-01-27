# editor_ops.py
import tkinter as tk
from tkinter import messagebox
import json
import re


# -----------------------------
# FONT SIZE
# -----------------------------
def increase_font_size(text, font_family, font_size_state):
    """Increase font size by 1."""
    font_size_state["size"] += 1
    text.config(font=(font_family, font_size_state["size"]))


def decrease_font_size(text, font_family, font_size_state):
    """Decrease font size by 1 (minimum 8)."""
    if font_size_state["size"] > 8:
        font_size_state["size"] -= 1
        text.config(font=(font_family, font_size_state["size"]))


def zoom_with_wheel(event, text, font_family, font_size_state):
    if event.delta > 0:
        increase_font_size(text, font_family, font_size_state)
    else:
        decrease_font_size(text, font_family, font_size_state)


# -----------------------------
# SEARCH BAR
# -----------------------------
def show_search_bar(search_frame, search_entry):
    search_frame.pack(fill="x")
    search_entry.focus()


def hide_search_bar(search_frame, text):
    search_frame.pack_forget()
    clear_search_highlight(text)


def search_text(event, text, search_entry):
    query = search_entry.get()
    clear_search_highlight(text)

    if not query:
        return

    start = "1.0"
    while True:
        pos = text.search(query, start, stopindex="end")
        if not pos:
            break

        end = f"{pos}+{len(query)}c"
        text.tag_add("search_highlight", pos, end)

        if start == "1.0":
            text.mark_set("insert", pos)
            text.see(pos)

        start = end


def clear_search_highlight(text):
    text.tag_remove("search_highlight", "1.0", "end")

# -----------------------------
# COLOR TAGS
# -----------------------------
def apply_color(text, tag):
    try:
        start = text.index("sel.first")
        end = text.index("sel.last")
    except tk.TclError:
        return

    for t in ["color_red", "color_blue", "color_green", "color_yellow", "color_white"]:
        text.tag_remove(t, start, end)

    text.tag_add(tag, start, end)

def change_text_color(text, color):
    """Apply a unique color tag to selected text."""
    try:
        if text.tag_ranges(tk.SEL):
            start = text.index(tk.SEL_FIRST)
            end = text.index(tk.SEL_LAST)

            for tag in text.tag_names(start):
                if tag.startswith("color_"):
                    text.tag_remove(tag, start, end)

            tag_name = f"color_{color}_{start}_{end}".replace(".", "_")
            text.tag_add(tag_name, start, end)
            text.tag_config(tag_name, foreground=color)
        else:
            messagebox.showinfo("No Selection", "Please select some text first.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not change text color: {e}")

def change_text_to_white(text):
    change_text_color(text, "#CCCCCC")


def change_text_to_blue(text):
    change_text_color(text, "#8AB5FF")


def change_text_to_red(text):
    change_text_color(text, "#DE3B28")


def change_text_to_green(text):
    change_text_color(text, "#4CB562")


def change_text_to_yellow(text):
    change_text_color(text, "#F0E197")

# -----------------------------
# COLOR EXPORT / IMPORT
# -----------------------------
def has_color_tags(text):
    return any(tag.startswith("color_") for tag in text.tag_names())


def export_with_colors(text):
    content = text.get("1.0", tk.END + "-1c")

    color_tags = [tag for tag in text.tag_names() if tag.startswith("color_")]
    tag_info = []

    for tag in color_tags:
        ranges = text.tag_ranges(tag)
        match = re.match(r"color_(#[0-9A-Fa-f]{6})_", tag)
        if match:
            color_hex = match.group(1)
            for i in range(0, len(ranges), 2):
                start = str(ranges[i])
                end = str(ranges[i + 1])
                tag_info.append({
                    "color": color_hex,
                    "start": start,
                    "end": end
                })

    document = {
        "content": content,
        "format": "np100",
        "tags": tag_info
    }

    return json.dumps(document, ensure_ascii=False, indent=2)


def import_with_colors(text, json_content):
    try:
        document = json.loads(json_content)
        content = document.get("content", "")
        tags = document.get("tags", [])

        text.delete("1.0", tk.END)
        text.insert("1.0", content)

        for tag_data in tags:
            color = tag_data.get("color")
            start = tag_data.get("start")
            end = tag_data.get("end")

            if color and start and end:
                tag_name = f"color_{color}_{start}_{end}".replace(".", "_")
                text.tag_add(tag_name, start, end)
                text.tag_config(tag_name, foreground=color)

        return True
    except json.JSONDecodeError:
        return False
