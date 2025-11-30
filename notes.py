import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import ctypes
import os
import json
import re


# Track original content to detect changes
original_content = None
file_format = None  # 'txt' or 'np100' to track format


def get_current_content():
    """Get the current content of the text widget."""
    content = text.get("1.0", tk.END)
    # Remove trailing newline if present (Text widget always ends with newline)
    if content.endswith('\n'):
        content = content[:-1]
    return content


def has_color_tags():
    """Check if the text widget has any color tags."""
    all_tags = text.tag_names()
    return any(tag.startswith("color_") for tag in all_tags)


def export_with_colors():
    """Export text widget content with color tags to custom format (JSON)."""
    content = text.get("1.0", tk.END + "-1c")  # Get content without trailing newline
    
    # Collect all color tags with their ranges
    color_tags = [tag for tag in text.tag_names() if tag.startswith("color_")]
    tag_info = []
    
    for tag in color_tags:
        # Get all ranges for this tag
        ranges = text.tag_ranges(tag)
        # Extract color from tag name
        match = re.match(r"color_(#[0-9A-Fa-f]{6})_", tag)
        if match:
            color_hex = match.group(1)
            # Store ranges as index strings
            for i in range(0, len(ranges), 2):
                start = str(ranges[i])
                end = str(ranges[i + 1])
                tag_info.append({
                    "color": color_hex,
                    "start": start,
                    "end": end
                })
    
    # Create document structure
    document = {
        "content": content,
        "format": "np100",
        "tags": tag_info
    }
    
    return json.dumps(document, ensure_ascii=False, indent=2)


def import_with_colors(json_content):
    """Import content from custom format and restore color tags."""
    try:
        document = json.loads(json_content)
        content = document.get("content", "")
        tags = document.get("tags", [])
        
        # Clear existing content
        text.delete("1.0", tk.END)
        
        # Insert content
        text.insert("1.0", content)
        
        # Restore color tags
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


def has_unsaved_changes():
    """Check if there are unsaved changes by comparing current content with original."""
    if original_content is None:
        return False
    
    # Determine format to use for comparison
    # If original content is JSON format, use that format; otherwise check for colors
    use_colored_format = False
    if file_format == 'np100':
        use_colored_format = True
    elif original_content.strip().startswith('{') and '"format":"np100"' in original_content:
        use_colored_format = True
    elif has_color_tags():
        use_colored_format = True
    
    # Get current content in the same format as original
    if use_colored_format:
        current = export_with_colors()
    else:
        current = get_current_content()
    
    return current != original_content


def reset_original_content():
    """Reset the original content to the current content (after save/open)."""
    global original_content
    if file_format == 'np100' or has_color_tags():
        original_content = export_with_colors()
    else:
        original_content = get_current_content()


def mark_as_modified(event=None):
    """Mark that the document has been modified (called on text changes)."""
    # This function can be used for future enhancements like showing * in title
    pass


def open_file():
    global original_content, file_format
    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=[("Text Files", "*.txt"), ("NP100 Files", "*.np100"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                
                # Try to detect if it's a custom format file
                if file_path.endswith('.np100') or (content.strip().startswith('{') and '"format":"np100"' in content):
                    # Load custom format with colors
                    if import_with_colors(content):
                        file_format = 'np100'
                        original_content = export_with_colors()  # Store in same format
                    else:
                        messagebox.showerror("Error", "Could not parse file format.")
                else:
                    # Load as plain text
                    text.delete("1.0", tk.END)
                    text.insert(tk.END, content)
                    file_format = 'txt'
                    original_content = content
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")


def save_file():
    global original_content, file_format
    file_path = filedialog.asksaveasfilename(
        title="Save File",
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("NP100 Files", "*.np100"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            # Check if document has colors
            has_colors = has_color_tags()
            
            # Determine format based on file extension or presence of colors
            if file_path.endswith('.np100') or has_colors:
                # Save with color information
                content = export_with_colors()
                file_format = 'np100'
                if not file_path.endswith('.np100'):
                    # Replace existing extension with .np100 or add it
                    base_path = os.path.splitext(file_path)[0]
                    file_path = base_path + '.np100'
            else:
                # Save as plain text
                content = get_current_content()
                file_format = 'txt'
            
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            original_content = content  # Reset original content after saving
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False
    return False


def change_text_color(color):
    """Change the color of selected text to the specified color."""
    try:
        if text.tag_ranges(tk.SEL):
            # Get the selected text range
            start = text.index(tk.SEL_FIRST)
            end = text.index(tk.SEL_LAST)
            
            # Remove any existing color tags from the selection
            for tag in text.tag_names(start):
                if tag.startswith("color_"):
                    text.tag_remove(tag, start, end)
            
            # Create a unique tag name based on color and position
            tag_name = f"color_{color}_{start}_{end}".replace(".", "_")
            
            # Apply the tag to the selected text
            text.tag_add(tag_name, start, end)
            text.tag_config(tag_name, foreground=color)
        else:
            messagebox.showinfo("No Selection", "Please select some text first.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not change text color: {e}")


def change_text_to_red():
    change_text_color("#DE3B28") #DE3F1F


def change_text_to_green():
    change_text_color("#4CB562")


def change_text_to_yellow():
    change_text_color("#F0E197")


def on_closing():
    if has_unsaved_changes():
        response = messagebox.askyesnocancel(
            "Confirm Exit",
            "Do you want to save changes before closing?"
        )
        if response is None:
            return
        if response:
            if not save_file():
                return
    root.destroy()


def enable_dark_title_bar(window):
    if sys.platform != "win32":
        return
    try:
        hwnd = ctypes.windll.user32.GetAncestor(window.winfo_id(), 2)
        attribute = ctypes.c_int(20)  # DWMWA_USE_IMMERSIVE_DARK_MODE
        value = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            attribute.value,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
    except Exception:
        pass


POWERSHELL_BG = "#0D0C0C"
POWERSHELL_FG = "#CCCCCC"
POWERSHELL_ACCENT = "#5f87ff"
RETRO_FONT = ("Cascadia Code", 13)

root = tk.Tk()
root.title("NP_100")
root.configure(bg=POWERSHELL_BG)
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.join(base_path, "NP_100.ico")


root.iconbitmap(icon_path)
root.update_idletasks()
enable_dark_title_bar(root)
root.option_add("*Menu.background", POWERSHELL_BG)
root.option_add("*Menu.foreground", POWERSHELL_FG)
root.option_add("*Menu.activeBackground", POWERSHELL_ACCENT)
root.option_add("*Menu.activeForeground", POWERSHELL_FG)
root.option_add("*Menu.relief", "flat")

menubar_frame = tk.Frame(root, bg="#4A4A4A")
menubar_frame.pack(fill="x")



file_btn = tk.Menubutton(menubar_frame, text="File", bg="#4A4A4A", fg=POWERSHELL_FG)
file_dropdown = tk.Menu(file_btn, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
file_dropdown.add_command(label="Open", command=open_file)
file_dropdown.add_command(label="Save", command=save_file)
file_btn.config(menu=file_dropdown)
file_btn.pack(side="left", padx=5)

format_btn = tk.Menubutton(menubar_frame, text="Format", bg="#4A4A4A", fg=POWERSHELL_FG)
format_dropdown = tk.Menu(format_btn, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
color_submenu = tk.Menu(format_dropdown, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
color_submenu.add_command(label="Red", command=change_text_to_red)
color_submenu.add_command(label="Green", command=change_text_to_green)
color_submenu.add_command(label="Yellow", command=change_text_to_yellow)
format_dropdown.add_cascade(label="Text Color", menu=color_submenu)
format_btn.config(menu=format_dropdown)
format_btn.pack(side="left", padx=5)

text = tk.Text(
    root,
    wrap="word",
    bg=POWERSHELL_BG,
    fg=POWERSHELL_FG,
    insertbackground=POWERSHELL_FG,
    selectbackground=POWERSHELL_ACCENT,
    selectforeground=POWERSHELL_BG,
    highlightthickness=0,
    font=RETRO_FONT
)
text.pack(expand=1, fill="both")

if len(sys.argv) > 1:
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Try to detect if it's a custom format file
            if file_path.endswith('.np100') or (content.strip().startswith('{') and '"format":"np100"' in content):
                # Load custom format with colors
                if import_with_colors(content):
                    file_format = 'np100'
                    original_content = export_with_colors()  # Store in same format
                else:
                    error_msg = "Error: No se pudo analizar el formato del archivo."
                    text.insert("1.0", error_msg)
                    original_content = error_msg
            else:
                # Load as plain text
                text.insert("1.0", content)
                file_format = 'txt'
                original_content = content
    except Exception as e:
        error_msg = f"Error al abrir archivo: {e}"
        text.insert("1.0", error_msg)
        original_content = error_msg
        file_format = 'txt'
else:
    default_text = "Nuevo documento..."
    text.insert("1.0", default_text)
    original_content = default_text
    file_format = 'txt'

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
