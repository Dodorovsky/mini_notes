# file_ops.py
import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from locks import is_file_already_open, remove_file_lock



# -----------------------------
# RESOURCE PATH (PyInstaller)
# -----------------------------
def resource_path(*paths):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *paths)


# -----------------------------
# CONTENT HELPERS
# -----------------------------
def get_current_content(text):
    """Return text content without trailing newline."""
    content = text.get("1.0", tk.END)
    if content.endswith("\n"):
        content = content[:-1]
    return content


def has_unsaved_changes(text):
    return text.edit_modified()


def reset_original_content(state, text, export_with_colors, has_color_tags):
    """Update original_content after save/open."""
    if state["file_format"] == "np100" or has_color_tags(text):
        state["original_content"] = export_with_colors(text)
    else:
        state["original_content"] = get_current_content(text)


# -----------------------------
# LOAD FILE
# -----------------------------
def load_file(file_path, text, root, state, import_with_colors, export_with_colors):


    """
    state = {
        "original_content": ...,
        "file_format": ...,
        "current_file_path": ...
    }
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        ext = os.path.splitext(file_path)[1].lower()

        is_mini = (
            ext in (".mini", ".np100")
            or (content.strip().startswith("{") and '"format":"np100"' in content)
        )

        if is_mini:
            if import_with_colors(text, content):
                state["file_format"] = "np100"
                state["original_content"] = export_with_colors(text)
            else:
                raise ValueError("Could not parse NP100/MINI file.")
        else:
            text.delete("1.0", tk.END)
            text.insert("1.0", content)
            state["file_format"] = "txt"
            state["original_content"] = content

        state["current_file_path"] = file_path
        root.title(f"mini_notes - {os.path.basename(file_path)}")
        text.edit_modified(False)

    except Exception as e:
        text.delete("1.0", tk.END)
        text.insert("1.0", f"Error opening file: {e}")
        state["original_content"] = ""
        state["file_format"] = "txt"
        state["current_file_path"] = None


def open_file(text, root, state, import_with_colors, export_with_colors):
    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=[
            ("All Supported Files", "*.mini *.np100 *.txt"),
            ("Mini Notes Files", "*.mini *.np100"),
            ("Mini Files", "*.mini"),
            ("Legacy NP100 Files", "*.np100"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*"),
        ],
    )

    if file_path:
        load_file(file_path, text, root, state, import_with_colors, export_with_colors)


# -----------------------------
# SAVE FILE
# -----------------------------
def _perform_save(
    file_path, text, state, export_with_colors, get_current_content
):
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            content = get_current_content(text)
            state["file_format"] = "txt"

        elif ext in (".mini", ".np100"):
            content = export_with_colors(text)
            state["file_format"] = "np100"

        else:
            base_path = os.path.splitext(file_path)[0]
            file_path = base_path + ".mini"
            content = export_with_colors(text)
            state["file_format"] = "np100"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        state["original_content"] = content
        state["current_file_path"] = file_path

        return True

    except Exception as e:
        messagebox.showerror("Error", f"Could not save file: {e}")
        return False


def save_file_as(text, state, export_with_colors, get_current_content):
    initial_dir = os.path.expanduser("~/Documents")

    file_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        defaultextension=".mini",
        filetypes=[
            ("Mini Notes", "*.mini"),
            ("NP100 Notes", "*.np100"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ],
        title="Save notes as...",
    )

    if not file_path:
        return False

    result = _perform_save(
        file_path, text, state, export_with_colors, get_current_content
    )
    text.edit_modified(False)
    return result


def save_file(text, state, export_with_colors, get_current_content):
    if state["current_file_path"] and os.path.exists(state["current_file_path"]):
        result = _perform_save(
            state["current_file_path"],
            text,
            state,
            export_with_colors,
            get_current_content,
        )
        text.edit_modified(False)
        return result
    else:
        return save_file_as(text, state, export_with_colors, get_current_content)


# -----------------------------
# WINDOW CLOSE HANDLING
# -----------------------------
def on_closing(root, text, state, save_file, has_unsaved_changes):
    

    if state["current_file_path"]:
        remove_file_lock(state["current_file_path"])

    if has_unsaved_changes(text):
        response = messagebox.askyesnocancel(
            "Confirm Exit", "Do you want to save changes before closing?"
        )

        if response is None:
            return

        if response:
            if save_file():
                root.after(10, root.destroy)
            return
        else:
            root.destroy()
            return

    root.destroy()
