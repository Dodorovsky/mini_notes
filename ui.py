import tkinter as tk
from file_ops import open_file
from config import (
    WINDOW_TITLE, FONT_FAMILY, FONT_SIZE,
    POWERSHELL_ACCENT, POWERSHELL_BG, POWERSHELL_FG, POWERSHELL_ACCENT_HOVER
)

def build_ui(root):

    # --- WINDOW CONFIG ---
    root.title(WINDOW_TITLE)
    root.configure(bg=POWERSHELL_BG)

    # --- MENU BAR FRAME ---
    menubar_frame = tk.Frame(root, bg="#4A4A4A")
    menubar_frame.pack(fill="x")

    # --- TOOLBAR ---
    toolbar = tk.Frame(root, bd=1, relief=tk.RAISED, background="#1C1C1B")
    toolbar.pack(side=tk.TOP, fill=tk.X)
    toolbar.pack_propagate(False)
    toolbar.config(height=20)

    # Buttons (solo UI)
    btn_white = tk.Button(toolbar, text="000", fg="#CCCCCC", bg="#CCCCCC")
    btn_white.pack(side=tk.LEFT, padx=(10, 5), pady=(3, 2))

    btn_blue = tk.Button(toolbar, text="000", fg="#8AB5FF", bg="#8AB5FF")
    btn_blue.pack(side=tk.LEFT, padx=0, pady=(3, 2))

    btn_yellow = tk.Button(toolbar, text="000", fg="#F0E197", bg="#F0E197")
    btn_yellow.pack(side=tk.LEFT, padx=(280, 0), pady=(3, 2))

    btn_green = tk.Button(toolbar, text="000", fg="#4CB562", bg="#4CB562")
    btn_green.pack(side=tk.LEFT, padx=5, pady=(3, 2))

    btn_red = tk.Button(toolbar, text="000", fg="#DE3B28", bg="#DE3B28")
    btn_red.pack(side=tk.LEFT, pady=(3, 2))

    # --- MAIN EDITOR FRAME ---
    editor_frame = tk.Frame(root, bg=POWERSHELL_BG)
    editor_frame.pack(expand=True, fill="both")

    # --- CUSTOM SCROLLBAR ---
    scroll_canvas = tk.Canvas(
        editor_frame,
        width=12,
        bg=POWERSHELL_BG,
        highlightthickness=0,
        bd=0
    )
    scroll_canvas.pack(side="right", fill="y")

    # Thumb inicial
    thumb = scroll_canvas.create_rectangle(
        0, 0, 12, 40,
        fill=POWERSHELL_ACCENT,
        outline=POWERSHELL_ACCENT
    )

    # --- TEXT WIDGET ---
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

    # --- SEARCH BAR ---
    search_frame = tk.Frame(root)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True)

    close_search_btn = tk.Button(search_frame, text="X")
    close_search_btn.pack(side="right")
    
    # --- FUNCIONES DE SINCRONIZACIÓN ---

    def update_scrollbar(first, last):
        """
        Actualiza la posición y tamaño del thumb cuando el Text hace scroll.
        """
        first = float(first)
        last = float(last)

        canvas_height = scroll_canvas.winfo_height()

        # Tamaño mínimo del thumb
        thumb_height = max(40, (last - first) * canvas_height)

        y1 = first * canvas_height
        y2 = y1 + thumb_height

        scroll_canvas.coords(thumb, 0, y1, 12, y2)


    def on_drag(event):
        """
        Permite arrastrar el thumb para mover el texto.
        """
        canvas_height = scroll_canvas.winfo_height()
        y = event.y

        # Limitar dentro del canvas
        y = max(0, min(canvas_height, y))

        # Convertir posición del canvas → fracción de scroll
        fraction = y / canvas_height
        text.yview_moveto(fraction)


    # --- EVENTOS DEL THUMB ---

    def on_enter(event):
        scroll_canvas.itemconfig(thumb, fill=POWERSHELL_ACCENT_HOVER)

    def on_leave(event):
        scroll_canvas.itemconfig(thumb, fill=POWERSHELL_ACCENT)


    # --- ENLACES ---

    # El Text avisa al Canvas cuando se mueve
    text.config(yscrollcommand=update_scrollbar)

    # El Canvas controla al Text cuando arrastras el thumb
    scroll_canvas.bind("<B1-Motion>", on_drag)
    scroll_canvas.bind("<Button-1>", on_drag)

    # Hover del thumb
    scroll_canvas.tag_bind(thumb, "<Enter>", on_enter)
    scroll_canvas.tag_bind(thumb, "<Leave>", on_leave)

    # --- RETURN ALL IMPORTANT WIDGETS ---
    return {
        "menubar_frame": menubar_frame,
        "toolbar": toolbar,
        "text": text,
        "scroll_canvas": scroll_canvas,
        "thumb": thumb,
        "search_frame": search_frame,
        "search_entry": search_entry,
        "btn_yellow": btn_yellow,
        "btn_green": btn_green,
        "btn_red": btn_red,
        "btn_blue": btn_blue,
        "btn_white": btn_white,  
    }
    




    
