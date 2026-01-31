import sys, ctypes
import tkinter as tk
from tkinter import messagebox

from ui import build_ui
from config import FONT_FAMILY, FONT_SIZE

# Editor logic
from editor_ops import (
    zoom_with_wheel,
    show_search_bar,
    hide_search_bar,
    search_text,
    clear_search_highlight,
    apply_color,
    change_text_to_yellow,
    change_text_to_green,
    change_text_to_red,
    change_text_to_blue,
    change_text_to_white,
    increase_font_size,
    decrease_font_size,
    has_color_tags,
    export_with_colors,
    import_with_colors,
)

# File logic
from file_ops import (
    resource_path,
    get_current_content,
    has_unsaved_changes,
    reset_original_content,
    load_file,
    open_file,
    save_file,
    save_file_as,
    on_closing,
)


def run_app():
    root = tk.Tk()
    root.update_idletasks()
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

    icon_image = tk.PhotoImage(file=resource_path("assets", "mini_notes.png"))
    root.iconphoto(True, icon_image)
    
    enable_dark_title_bar(root)
    
    # -------------------------
    # BUILD UI
    # -------------------------
    ui = build_ui(root)
    text = ui["text"]
    scroll_canvas = ui["scroll_canvas"]
    thumb = ui["thumb"]
    search_frame = ui["search_frame"]
    search_entry = ui["search_entry"]

    # -------------------------
    # STATE (replaces globals)
    # -------------------------
    state = {
        "original_content": "",
        "file_format": "txt",
        "current_file_path": None,
        "font_size_state": {"size": FONT_SIZE},
    }

    # -------------------------
    # CONNECT TOOLBAR BUTTONS
    # -------------------------
    ui["btn_white"].config(command=lambda: change_text_to_white(text))
    ui["btn_blue"].config(command=lambda: change_text_to_blue(text))
    ui["btn_yellow"].config(command=lambda: change_text_to_yellow(text))
    ui["btn_green"].config(command=lambda: change_text_to_green(text))
    ui["btn_red"].config(command=lambda: change_text_to_red(text))
    
    
    # -------------------------
    # CONTEXT MENU (Right-click)
    # -------------------------
    context_menu = tk.Menu(text, tearoff=0, bg="#4A4A4A", fg="white")
    context_menu.add_command(label="Yellow", command=lambda: change_text_to_yellow(text))
    context_menu.add_command(label="Green", command=lambda: change_text_to_green(text))
    context_menu.add_command(label="Red", command=lambda: change_text_to_red(text))
    context_menu.add_command(label="Blue", command=lambda: change_text_to_blue(text))
    context_menu.add_command(label="White", command=lambda: change_text_to_white(text))


    def show_context_menu(event):
        context_menu.tk_popup(event.x_root, event.y_root)

    text.bind("<Button-3>", show_context_menu)


    # -------------------------
    # MENU BAR
    # -------------------------
    menubar = ui["menubar_frame"]

    # FILE MENU
    file_btn = tk.Menubutton(menubar, text="File", bg="#4A4A4A", fg="white")
    file_menu = tk.Menu(file_btn, tearoff=0, bg="#4A4A4A", fg="white")
    file_menu.add_command(label="Open", command=lambda: open_file(
        text, root, state, import_with_colors, export_with_colors
    ))
    file_menu.add_command(label="Save", command=lambda: save_file(
        text, state, export_with_colors, get_current_content
    ))
    file_menu.add_command(label="Save As", command=lambda: save_file_as(
        text, state, export_with_colors, get_current_content
    ))
    file_btn.config(menu=file_menu)
    file_btn.pack(side="left")

    # FORMAT MENU
    
    format_btn = tk.Menubutton(menubar, text="Format", bg="#4A4A4A", fg="white")

    format_menu = tk.Menu(format_btn, tearoff=0, bg="#4A4A4A", fg="white")

    # -------------------------
    # BINDS
    # -------------------------
    root.bind("<Control-MouseWheel>", lambda e: zoom_with_wheel(
        e, text, FONT_FAMILY, state["font_size_state"]
    ))

    # Zoom con Ctrl + +
    root.bind("<Control-plus>", lambda e: increase_font_size(text, FONT_FAMILY, state["font_size_state"]))
    root.bind("<Control-KP_Add>", lambda e: increase_font_size(text, FONT_FAMILY, state["font_size_state"]))  

    # Zoom con Ctrl + -
    root.bind("<Control-minus>", lambda e: decrease_font_size(text, FONT_FAMILY, state["font_size_state"]))
    root.bind("<Control-KP_Subtract>", lambda e: decrease_font_size(text, FONT_FAMILY, state["font_size_state"])) 

    
    root.bind("<Control-f>", lambda e: show_search_bar(search_frame, search_entry))

    root.bind("<Control-s>", lambda e: save_file(text, state, export_with_colors, get_current_content))
    root.bind("<Control-S>", lambda e: save_file(text, state, export_with_colors, get_current_content))  

    search_entry.bind("<KeyRelease>", lambda e: search_text(e, text, search_entry))

    # Submenú de colores
    color_submenu = tk.Menu(format_menu, tearoff=0, bg="#1C1C1B", fg="white")

    color_submenu.add_command(label="White", command=lambda: change_text_to_white(text))
    color_submenu.add_command(label="Blue", command=lambda: change_text_to_blue(text))
    color_submenu.add_command(label="Yellow", command=lambda: change_text_to_yellow(text))
    color_submenu.add_command(label="Green", command=lambda: change_text_to_green(text))
    color_submenu.add_command(label="Red", command=lambda: change_text_to_red(text))
    
    format_menu.add_cascade(label="Text Color", menu=color_submenu)
    format_menu.add_separator()
    
    format_menu.add_command(label="Increase Font Size (Ctrl ++)", command=lambda: increase_font_size(
        text, FONT_FAMILY, state["font_size_state"]
    ))
    format_menu.add_command(label="Decrease Font Size (Ctrl +-)", command=lambda: decrease_font_size(
        text, FONT_FAMILY, state["font_size_state"]
    ))
    format_btn.config(menu=format_menu)
    format_btn.pack(side="left")
    
    # -------------------------
    # SCROLLBAR LOGIC
    # -------------------------
    def update_thumb(*args):
        text.update_idletasks()

        total = float(text.count("1.0", "end", "ypixels")[0])
        visible = float(text.winfo_height())
        first, last = text.yview()

        if total <= visible:
            scroll_canvas.itemconfigure(thumb, state="hidden")
            return

        scroll_canvas.itemconfigure(thumb, state="normal")

        proportional_height = visible * (visible / total)
        min_thumb = 30
        max_thumb = visible * 0.6
        thumb_height = max(min_thumb, min(max_thumb, proportional_height))
        thumb_y = first * (visible - thumb_height)

        scroll_canvas.coords(thumb, 0, thumb_y, 12, thumb_y + thumb_height)

    text.bind("<<Modified>>", update_thumb)
    text.bind("<Configure>", update_thumb)
    text.bind("<KeyRelease>", update_thumb)

    # -------------------------
    # LOAD FILE FROM ARGUMENT
    # -------------------------
    if len(sys.argv) > 1:
        load_file(
            sys.argv[1], text, root, state, import_with_colors, export_with_colors
        )
        


    else:
        text.insert("1.0", "")
        state["original_content"] = ""
        state["file_format"] = "txt"
        state["current_file_path"] = None

    # -------------------------
    # WINDOW CLOSE HANDLER
    # -------------------------
    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: on_closing(
            root,
            text,
            state,
            lambda: save_file(text, state, export_with_colors, get_current_content),
            has_unsaved_changes,
        ),
    )

    root.mainloop()

    
    
    
    
    
    
