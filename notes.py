import sys, os, json, ctypes, re
import os
import json

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

FONT_SIZE = 14 
FONT_FAMILY = "Consolas"

POWERSHELL_BG = "#0D0C0C"
POWERSHELL_FG = "#CCCCCC"
POWERSHELL_ACCENT = "#5fe2ff"#5f87ff
FONT_FAMILY = "Cascadia Code"
FONT_SIZE = 13  # Initial font size

# Track original content to detect changes
original_content = None
file_format = None  # 'txt' or 'np100' to track format
current_file_path = None  # Track the currently open file path

def resource_path(*paths):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *paths)

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
    return text.edit_modified()

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

def load_file(file_path):
    global original_content, file_format, current_file_path

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Detect format
        ext = os.path.splitext(file_path)[1].lower()

        is_mini = (
            ext == ".mini"
            or ext == ".np100"
            or (content.strip().startswith("{") and '"format":"np100"' in content)
        )

        if is_mini:
            if import_with_colors(content):
                file_format = "np100"
                original_content = export_with_colors()
            else:
                raise ValueError("Could not parse NP100/MINI file.")
        else:
            text.delete("1.0", tk.END)
            text.insert("1.0", content)
            file_format = "txt"
            original_content = content

        # Update state
        current_file_path = file_path
        root.title(f"mini_notes - {os.path.basename(file_path)}")
        text.edit_modified(False)


    except Exception as e:
        text.delete("1.0", tk.END)
        text.insert("1.0", f"Error opening file: {e}")
        original_content = ""
        file_format = "txt"
        current_file_path = None

def open_file():
    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=[
            ("All Supported Files", "*.mini *.np100 *.txt"),
            ("Mini Notes Files", "*.mini *.np100"),
            ("Mini Files", "*.mini"),
            ("Legacy NP100 Files", "*.np100"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]

    )

    if file_path:
        load_file(file_path)

def save_file_as():
    file_path = filedialog.asksaveasfilename(...)
    if not file_path:
        return False

    result = _perform_save(file_path)
    text.edit_modified(False)
    return result

def _perform_save(file_path):
    """Internal function to perform the actual save operation."""
    global original_content, file_format, current_file_path

    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            # Save as plain text
            content = get_current_content()
            file_format = "txt"

        elif ext in (".mini", ".np100"):
            # Save in mini_notes JSON format (with colors)
            content = export_with_colors()
            file_format = "np100"  # internal format stays np100

        else:
            # Unknown extension → default to .mini
            base_path = os.path.splitext(file_path)[0]
            file_path = base_path + ".mini"
            content = export_with_colors()
            file_format = "np100"

        # Write file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        # Update state
        original_content = content
        current_file_path = file_path

        return True

    except Exception as e:
        messagebox.showerror("Error", f"Could not save file: {e}")
        return False

def save_file():
    """Save file directly if file path exists, otherwise show Save As dialog."""
    if current_file_path and os.path.exists(current_file_path):
        result = _perform_save(current_file_path)
        text.edit_modified(False)
        return result
    else:
        result = save_file_as()
        text.edit_modified(False)
        return result

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

def change_text_to_white():
    change_text_color("#CCCCCC")
    
def change_text_to_blue():
    change_text_color("#8AB5FF")#7EAAF7

def change_text_to_red():
    change_text_color("#DE3B28") #DE3F1F

def change_text_to_green():
    change_text_color("#4CB562")

def change_text_to_yellow():
    change_text_color("#F0E197")

def increase_font_size():
    """Increase the font size by 1."""
    global FONT_SIZE
    FONT_SIZE += 1
    text.config(font=(FONT_FAMILY, FONT_SIZE))

def decrease_font_size():
    """Decrease the font size by 1 (minimum 8)."""
    global FONT_SIZE
    if FONT_SIZE > 8:  # Set minimum font size to 8
        FONT_SIZE -= 1
        text.config(font=(FONT_FAMILY, FONT_SIZE))

def on_closing():
    if has_unsaved_changes():
        response = messagebox.askyesnocancel(
            "Confirm Exit",
            "Do you want to save changes before closing?"
        )
        if response is None:
            return  # Cancel
        if response:  # Yes, save
            if not save_file():
                return  # If saving fails, do not close
            root.destroy()  # Saved OK → close immediately
            return
        else:
            # Do not save → close directly
            root.destroy()
            return

    # No changes → close
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

def zoom_with_wheel(event):
    if event.delta > 0:
        increase_font_size()
    else:
        decrease_font_size()

def show_search_bar(event=None):
    search_frame.pack(fill="x")
    search_entry.focus()

def hide_search_bar():
    search_frame.pack_forget()
    clear_search_highlight()
    
def search_text(event=None):
    query = search_entry.get()
    clear_search_highlight()

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

def clear_search_highlight():
    text.tag_remove("search_highlight", "1.0", "end")

def apply_color(tag):
    try:
        start = text.index("sel.first")
        end = text.index("sel.last")
    except tk.TclError:
        return  

    # Remove previous colors
    for t in ["color_red", "color_blue", "color_green", "color_yellow", "color_white"]:
        text.tag_remove(t, start, end)

    # Apply the new color
    text.tag_add(tag, start, end)
    
def remove_color():
    try:
        start = text.index("sel.first")
        end = text.index("sel.last")
    except tk.TclError:
        return

    for t in ["color_red", "color_blue", "color_green", "color_yellow", "color_white"]:
        text.tag_remove(t, start, end)


root = tk.Tk()
root.title("mini_notes")
root.configure(bg=POWERSHELL_BG)

icon_image = tk.PhotoImage(file=resource_path("assets", "mini_notes.png"))
root.iconphoto(True, icon_image)

root.update_idletasks()
enable_dark_title_bar(root)

# Menu styling
root.option_add("*Menu.background", POWERSHELL_BG)
root.option_add("*Menu.foreground", POWERSHELL_FG)
root.option_add("*Menu.activeBackground", POWERSHELL_ACCENT)
root.option_add("*Menu.activeForeground", POWERSHELL_FG)
root.option_add("*Menu.relief", "flat")

# Top menu bar frame
menubar_frame = tk.Frame(root, bg="#4A4A4A")
menubar_frame.pack(fill="x")

# Toolbar debajo del menú
toolbar = tk.Frame(root, bd=1, relief=tk.RAISED, background="#1C1C1B")
toolbar.pack(side=tk.TOP, fill=tk.X)
toolbar.pack_propagate(False)
toolbar.config(height=20)
btn_white= tk.Button(toolbar, text="00", fg="#CCCCCC", bg= "#CCCCCC", command=change_text_to_white)
btn_white.pack(side=tk.LEFT, padx=(10,5), pady=(3, 2))

btn_blue= tk.Button(toolbar, text="00", fg="#8AB5FF", bg= "#8AB5FF", command=change_text_to_blue)
btn_blue.pack(side=tk.LEFT, padx=(0), pady=(3, 2))

btn_yellow = tk.Button(toolbar, text="00", fg="#F0E197", bg= "#F0E197", command=change_text_to_yellow)
btn_yellow.pack(side=tk.LEFT, padx=(280,0), pady=(3, 2))

btn_green = tk.Button(toolbar, text="00", fg="#4CB562", bg= "#4CB562", command=change_text_to_green)
btn_green.pack(side=tk.LEFT, padx=5, pady=(3, 2))

btn_red = tk.Button(toolbar, text="00", fg="#DE3B28", bg="#DE3B28",  command=change_text_to_red)
btn_red.pack(side=tk.LEFT, pady=(3, 2))

toolbar.pack(side=tk.TOP, fill=tk.X)

# MAIN EDITOR AREA (prevents double spacing)
editor_frame = tk.Frame(root, bg=POWERSHELL_BG)
editor_frame.pack(expand=True, fill="both")

# Custom scrollbar using Canvas
scroll_canvas = tk.Canvas(
    editor_frame,
    width=12,
    bg=POWERSHELL_BG,
    highlightthickness=0,
    bd=0
)
scroll_canvas.pack(side="right", fill="y")

# Scrollbar thumb (the draggable part)
thumb = scroll_canvas.create_rectangle(
    0, 0, 12, 40,
    fill=POWERSHELL_ACCENT,
    outline=POWERSHELL_ACCENT
)

# Text widget
text = tk.Text(
    editor_frame,
    wrap="word",
    bg=POWERSHELL_BG,
    fg=POWERSHELL_FG,
    insertbackground=POWERSHELL_FG,
    selectbackground=POWERSHELL_ACCENT,
    selectforeground=POWERSHELL_BG,
    highlightthickness=0,
    undo=True,
    autoseparators=True,
    maxundo=-1,
    font=(FONT_FAMILY, FONT_SIZE)
)
text.pack(side="left", expand=True, fill="both")

text.tag_config("search_highlight", background="yellow")
text.insert("1.0", "\n\n")
text.edit_modified(False)


text.tag_config("color_red", foreground="#DE3B28")
text.tag_config("color_blue", foreground="#8AB5FF")
text.tag_config("color_green", foreground="#4CB562")
text.tag_config("color_yellow", foreground="#F0E197")
text.tag_config("color_white", foreground="#CCCCCC")

def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)

text.bind("<Button-3>", show_context_menu)

def update_thumb(*args):
    text.update_idletasks()

    total = float(text.count("1.0", "end", "ypixels")[0])
    visible = float(text.winfo_height())

    first, last = text.yview()

    # If everything fits, hide the thumb
    if total <= visible:
        scroll_canvas.itemconfigure(thumb, state="hidden")
        return
    else:
        scroll_canvas.itemconfigure(thumb, state="normal")

    # Proportional thumb size
    proportional_height = visible * (visible / total)

    # Limits for better precision
    min_thumb = 30
    max_thumb = visible * 0.6  # never bigger than 60% of the bar

    thumb_height = max(min_thumb, min(max_thumb, proportional_height))

    # Position
    thumb_y = first * (visible - thumb_height)

    scroll_canvas.coords(thumb, 0, thumb_y, 12, thumb_y + thumb_height)

def scroll_drag(event):
    canvas_height = scroll_canvas.winfo_height()
    thumb_height = scroll_canvas.coords(thumb)[3] - scroll_canvas.coords(thumb)[1]

    pos = event.y - thumb_height / 2
    pos = max(0, min(pos, canvas_height - thumb_height))

    fraction = pos / (canvas_height - thumb_height)
    text.yview_moveto(fraction)
    update_thumb()

def on_thumb_enter(event):
    scroll_canvas.itemconfig(thumb, fill="#FEF89E")  # hover

def on_thumb_leave(event):
    scroll_canvas.itemconfig(thumb, fill=POWERSHELL_ACCENT)  # normal

scroll_canvas.tag_bind(thumb, "<Enter>", on_thumb_enter)
scroll_canvas.tag_bind(thumb, "<Leave>", on_thumb_leave)

def scroll_wheel(event):
    text.yview_scroll(int(-1 * (event.delta / 120)), "units")
    update_thumb()
    
def save_shortcut(event=None):
    if current_file_path:
        save_file()
    else:
        save_file_as()


scroll_canvas.bind("<Button-1>", scroll_drag)
scroll_canvas.bind("<B1-Motion>", scroll_drag)
scroll_canvas.bind("<MouseWheel>", scroll_wheel)
text.bind("<MouseWheel>", scroll_wheel)
text.bind("<<Modified>>", update_thumb)
text.bind("<Configure>", update_thumb)
text.bind("<KeyRelease>", update_thumb)
root.bind("<Control-MouseWheel>", zoom_with_wheel)
root.bind("<Control-f>", show_search_bar)

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Verde", command=lambda: apply_color("color_green"))
context_menu.add_command(label="Amarillo", command=lambda: apply_color("color_yellow"))
context_menu.add_command(label="Rojo", command=lambda: apply_color("color_red"))
context_menu.add_command(label="Azul", command=lambda: apply_color("color_blue"))
context_menu.add_command(label="Blanco", command=lambda: apply_color("color_white"))
context_menu.add_separator()
context_menu.add_command(label="Quitar color", command=remove_color)



file_btn = tk.Menubutton(menubar_frame, text="File", bg="#4A4A4A", fg=POWERSHELL_FG)
file_dropdown = tk.Menu(file_btn, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
file_dropdown.add_command(label="Open", command=open_file)
file_dropdown.add_command(label="Save", command=save_file)
file_dropdown.add_command(label="Save As", command=save_file_as)
file_btn.config(menu=file_dropdown)
file_btn.pack(side="left", padx=5)

format_btn = tk.Menubutton(menubar_frame, text="Format", bg="#4A4A4A", fg=POWERSHELL_FG)
format_dropdown = tk.Menu(format_btn, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
color_submenu = tk.Menu(format_dropdown, tearoff=0, bg="#4A4A4A", fg=POWERSHELL_FG)
color_submenu.add_command(label="Red", command=change_text_to_red)
color_submenu.add_command(label="Green", command=change_text_to_green)
color_submenu.add_command(label="Yellow", command=change_text_to_yellow)
color_submenu.add_command(label="White", command=change_text_to_white)
color_submenu.add_command(label="Blue", command=change_text_to_blue)
format_dropdown.add_cascade(label="Text Color", menu=color_submenu)
format_dropdown.add_separator()
format_dropdown.add_command(label="Increase Font Size (Ctrl++)", command=increase_font_size)
format_dropdown.add_command(label="Decrease Font Size (Ctrl+-)", command=decrease_font_size)
format_btn.config(menu=format_dropdown)
format_btn.pack(side="left", padx=5)

# Bind keyboard shortcuts for font size
def on_font_increase(event):
    increase_font_size()
    return "break"

def on_font_decrease(event):
    decrease_font_size()
    return "break"

# Bind Ctrl + + for increasing font size
# Handle different key combinations: Ctrl + = (which becomes + with Shift), Ctrl + +, Ctrl + = without Shift
root.bind_all("<Control-equal>", on_font_increase)  # Ctrl + = (often used for zoom)
root.bind_all("<Control-plus>", on_font_increase)   # Ctrl + + (numpad plus)
root.bind_all("<Control-Key-plus>", on_font_increase)  # Alternative binding
text.bind("<Control-equal>", on_font_increase)
text.bind("<Control-plus>", on_font_increase)
text.bind("<Control-Key-plus>", on_font_increase)

# Ctrl + S shortcut
root.bind("<Control-s>", save_shortcut)

# Bind Ctrl + - for decreasing font size
root.bind_all("<Control-minus>", on_font_decrease)  # Ctrl + -
root.bind_all("<Control-KP_Subtract>", on_font_decrease)  # Numpad minus
text.bind("<Control-minus>", on_font_decrease)
text.bind("<Control-KP_Subtract>", on_font_decrease)

if len(sys.argv) > 1:
    load_file(sys.argv[1])
else:
    text.insert("1.0", "")
    original_content = ""
    file_format = "txt"
    current_file_path = None
    
search_frame = tk.Frame(root)
search_entry = tk.Entry(search_frame)
search_entry.pack(side="left", fill="x", expand=True)

close_search_btn = tk.Button(search_frame, text="X", command=lambda: hide_search_bar())
close_search_btn.pack(side="right")

search_entry.bind("<KeyRelease>", search_text)


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()