import tkinter as tk
from tkinter import colorchooser
import random

# ============================================================
# GAME OF LIFE — RELAXED EDITION
# Parts 1 + 2A + 2B + 3 + 4
# Home screen • themes • colours • rules • speed • touch controls
# ============================================================

ROWS = 20
COLS = 20
CELL_SIZE = 28

BOARD_W = COLS * CELL_SIZE
BOARD_H = ROWS * CELL_SIZE

RULES = {
    "Life": {
        "birth": {3},
        "survival": {2, 3},
        "code": "B3/S23",
        "description": "The classic balanced Game of Life."
    },
    "HighLife": {
        "birth": {3, 6},
        "survival": {2, 3},
        "code": "B36/S23",
        "description": "Like Life, with extra births at 6 neighbours."
    },
    "Seeds": {
        "birth": {2},
        "survival": set(),
        "code": "B2/S",
        "description": "Fast and energetic. Living cells never survive."
    },
    "Day & Night": {
        "birth": {3, 6, 7, 8},
        "survival": {3, 4, 6, 7, 8},
        "code": "B3678/S34678",
        "description": "Dense patterns where life and empty space feel balanced."
    },
}

THEMES = {
    "Dark": {
        "bg": "#0E1116",
        "panel": "#171B22",
        "panel2": "#202630",
        "text": "#F4F7FB",
        "muted": "#98A2B3",
        "grid": "#2C3440",
        "button": "#252C36",
        "button_hover": "#313A47",
        "accent": "#8BA8FF",
        "dead": "#11151B",
        "alive": "#F4F7FB",
    },
    "Light": {
        "bg": "#EEF2F7",
        "panel": "#FFFFFF",
        "panel2": "#E7ECF3",
        "text": "#17202B",
        "muted": "#667085",
        "grid": "#D6DDE7",
        "button": "#E7ECF3",
        "button_hover": "#DCE3EC",
        "accent": "#496FD8",
        "dead": "#F8FAFC",
        "alive": "#27364A",
    },
}

# ============================================================
# STATE
# ============================================================

running = False
generation = 0
after_id = None

selected_rule = "Life"
selected_theme = "Dark"
alive_colour = THEMES[selected_theme]["alive"]
dead_colour = THEMES[selected_theme]["dead"]
speed_ms = 250

board = [[0 for _ in range(COLS)] for _ in range(ROWS)]


# ============================================================
# ROOT
# ============================================================

root = tk.Tk()
root.title("Game of Life — Relaxed Edition")
root.minsize(650, 760)

# Let the app fit smaller laptop displays better.
try:
    root.state("zoomed")
except tk.TclError:
    pass


# ============================================================
# HELPERS
# ============================================================

def theme():
    return THEMES[selected_theme]


def make_empty_board():
    new_board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(0)
        new_board.append(row)
    return new_board


def clear_root():
    for widget in root.winfo_children():
        widget.destroy()


def count_alive():
    return sum(sum(row) for row in board)


def soft_button(parent, text, command, width=12, accent=False):
    t = theme()
    bg = t["accent"] if accent else t["button"]
    fg = "#FFFFFF" if accent else t["text"]

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=bg,
        fg=fg,
        activebackground=t["button_hover"] if not accent else t["accent"],
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=10,
        pady=9,
        font=("Helvetica", 10, "bold"),
        cursor="hand2",
        highlightthickness=0,
    )
    return button


def card(parent):
    return tk.Frame(
        parent,
        bg=theme()["panel"],
        highlightthickness=1,
        highlightbackground=theme()["grid"]
    )


# ============================================================
# PART 2A — NEIGHBOURS
# ============================================================

def count_neighbours(r, c):
    count = 0

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue

            nr = r + dr
            nc = c + dc

            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if board[nr][nc] == 1:
                    count += 1

    return count


# ============================================================
# PART 2B / PART 4 — STEP + RULE ENGINE
# ============================================================

def step():
    global board, generation

    new_board = make_empty_board()
    birth = RULES[selected_rule]["birth"]
    survival = RULES[selected_rule]["survival"]

    for r in range(ROWS):
        for c in range(COLS):
            n = count_neighbours(r, c)

            if board[r][c] == 1:
                if n in survival:
                    new_board[r][c] = 1
                else:
                    new_board[r][c] = 0
            else:
                if n in birth:
                    new_board[r][c] = 1
                else:
                    new_board[r][c] = 0

    board = new_board
    generation += 1

    if current_screen == "game":
        draw_board()


# ============================================================
# PART 3 — RUN / STOP
# ============================================================

def simulation_loop():
    global after_id

    if not running:
        return

    step()
    after_id = root.after(speed_ms, simulation_loop)


def start_game():
    global running

    if running:
        return

    running = True
    update_game_controls()
    simulation_loop()


def stop_game():
    global running, after_id

    running = False

    if after_id is not None:
        try:
            root.after_cancel(after_id)
        except tk.TclError:
            pass
        after_id = None

    update_game_controls()


def toggle_running(event=None):
    if current_screen != "game":
        return

    if running:
        stop_game()
    else:
        start_game()


# ============================================================
# BOARD ACTIONS
# ============================================================

def clear_board():
    global board, generation

    stop_game()
    board = make_empty_board()
    generation = 0

    if current_screen == "game":
        draw_board()


def random_board():
    global generation

    stop_game()

    for r in range(ROWS):
        for c in range(COLS):
            board[r][c] = 1 if random.random() < 0.35 else 0

    generation = 0

    if current_screen == "game":
        draw_board()


# ============================================================
# HOME / SETTINGS SCREEN
# ============================================================

current_screen = "home"

def show_home():
    global current_screen

    stop_game()
    current_screen = "home"
    clear_root()

    t = theme()
    root.configure(bg=t["bg"])

    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True, padx=28, pady=24)

    tk.Label(
        outer,
        text="GAME OF LIFE",
        bg=t["bg"],
        fg=t["text"],
        font=("Helvetica", 26, "bold")
    ).pack(pady=(8, 2))

    tk.Label(
        outer,
        text="A calm cellular automata playground",
        bg=t["bg"],
        fg=t["muted"],
        font=("Helvetica", 11)
    ).pack(pady=(0, 18))

    # RULE CARD
    rule_card = card(outer)
    rule_card.pack(fill="x", pady=7)

    tk.Label(
        rule_card,
        text="WORLD",
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 9, "bold")
    ).pack(anchor="w", padx=18, pady=(15, 8))

    rule_buttons = tk.Frame(rule_card, bg=t["panel"])
    rule_buttons.pack(fill="x", padx=14)

    def choose_rule(name):
        global selected_rule
        selected_rule = name
        show_home()

    for name in RULES:
        chosen = name == selected_rule
        b = tk.Button(
            rule_buttons,
            text=name,
            command=lambda n=name: choose_rule(n),
            bg=t["accent"] if chosen else t["button"],
            fg="#FFFFFF" if chosen else t["text"],
            activebackground=t["button_hover"],
            activeforeground=t["text"],
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            font=("Helvetica", 9, "bold"),
            cursor="hand2"
        )
        b.pack(side="left", expand=True, fill="x", padx=3)

    rule = RULES[selected_rule]

    tk.Label(
        rule_card,
        text=rule["code"],
        bg=t["panel"],
        fg=t["accent"],
        font=("Helvetica", 13, "bold")
    ).pack(pady=(13, 2))

    tk.Label(
        rule_card,
        text=rule["description"],
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 9),
        wraplength=520
    ).pack(padx=18, pady=(0, 15))

    # APPEARANCE CARD
    appearance = card(outer)
    appearance.pack(fill="x", pady=7)

    tk.Label(
        appearance,
        text="APPEARANCE",
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 9, "bold")
    ).pack(anchor="w", padx=18, pady=(15, 9))

    appearance_row = tk.Frame(appearance, bg=t["panel"])
    appearance_row.pack(fill="x", padx=18, pady=(0, 10))

    def set_theme(name):
        global selected_theme, alive_colour, dead_colour
        selected_theme = name
        alive_colour = THEMES[name]["alive"]
        dead_colour = THEMES[name]["dead"]
        show_home()

    soft_button(
        appearance_row,
        "Dark",
        lambda: set_theme("Dark"),
        width=9,
        accent=selected_theme == "Dark"
    ).pack(side="left", padx=(0, 5))

    soft_button(
        appearance_row,
        "Light",
        lambda: set_theme("Light"),
        width=9,
        accent=selected_theme == "Light"
    ).pack(side="left", padx=5)

    def choose_alive():
        global alive_colour
        colour = colorchooser.askcolor(
            color=alive_colour,
            title="Choose living cell colour"
        )[1]
        if colour:
            alive_colour = colour
            show_home()

    def choose_dead():
        global dead_colour
        colour = colorchooser.askcolor(
            color=dead_colour,
            title="Choose background cell colour"
        )[1]
        if colour:
            dead_colour = colour
            show_home()

    soft_button(
        appearance_row,
        "Living Cells",
        choose_alive,
        width=12
    ).pack(side="right", padx=(5, 0))

    soft_button(
        appearance_row,
        "Board",
        choose_dead,
        width=9
    ).pack(side="right", padx=5)

    preview = tk.Frame(appearance, bg=t["panel"])
    preview.pack(pady=(0, 14))

    tk.Label(
        preview,
        text="  ",
        bg=dead_colour,
        width=3,
        height=1,
        relief="flat"
    ).pack(side="left", padx=4)

    tk.Label(
        preview,
        text="  ",
        bg=alive_colour,
        width=3,
        height=1,
        relief="flat"
    ).pack(side="left", padx=4)

    # SPEED CARD
    speed_card = card(outer)
    speed_card.pack(fill="x", pady=7)

    tk.Label(
        speed_card,
        text="SIMULATION SPEED",
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 9, "bold")
    ).pack(anchor="w", padx=18, pady=(15, 4))

    speed_value = tk.IntVar(value=speed_ms)

    def speed_changed(value):
        global speed_ms
        speed_ms = int(float(value))

    slider = tk.Scale(
        speed_card,
        variable=speed_value,
        command=speed_changed,
        from_=1000,
        to=50,
        orient="horizontal",
        showvalue=False,
        bg=t["panel"],
        fg=t["text"],
        troughcolor=t["panel2"],
        activebackground=t["accent"],
        highlightthickness=0,
        bd=0,
        length=430
    )
    slider.pack(padx=18, fill="x")

    speed_words = tk.Frame(speed_card, bg=t["panel"])
    speed_words.pack(fill="x", padx=20, pady=(0, 13))

    tk.Label(
        speed_words, text="Relaxed", bg=t["panel"],
        fg=t["muted"], font=("Helvetica", 8)
    ).pack(side="left")

    tk.Label(
        speed_words, text="Fast", bg=t["panel"],
        fg=t["muted"], font=("Helvetica", 8)
    ).pack(side="right")

    # PLAY
    play = soft_button(
        outer,
        "Enter World",
        show_game,
        width=22,
        accent=True
    )
    play.pack(pady=(16, 7))

    tk.Label(
        outer,
        text="Space = Run / Pause   •   S = Step   •   R = Random   •   Esc = Menu",
        bg=t["bg"],
        fg=t["muted"],
        font=("Helvetica", 8)
    ).pack(pady=(3, 0))


# ============================================================
# GAME SCREEN
# ============================================================

canvas = None
generation_label = None
alive_label = None
status_label = None
run_button = None
stop_button = None
step_button = None


def show_game():
    global current_screen
    global canvas, generation_label, alive_label, status_label
    global run_button, stop_button, step_button

    stop_game()
    current_screen = "game"
    clear_root()

    t = theme()
    root.configure(bg=t["bg"])

    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True, padx=18, pady=14)

    # Header
    header = tk.Frame(outer, bg=t["bg"])
    header.pack(fill="x", pady=(0, 10))

    menu_button = soft_button(
        header,
        "☰  Menu",
        show_home,
        width=9
    )
    menu_button.pack(side="left")

    title_box = tk.Frame(header, bg=t["bg"])
    title_box.pack(side="left", padx=14)

    tk.Label(
        title_box,
        text=selected_rule,
        bg=t["bg"],
        fg=t["text"],
        font=("Helvetica", 18, "bold")
    ).pack(anchor="w")

    tk.Label(
        title_box,
        text=RULES[selected_rule]["code"],
        bg=t["bg"],
        fg=t["accent"],
        font=("Helvetica", 9, "bold")
    ).pack(anchor="w")

    stats = tk.Frame(header, bg=t["bg"])
    stats.pack(side="right")

    generation_label = tk.Label(
        stats,
        text="",
        bg=t["bg"],
        fg=t["text"],
        font=("Helvetica", 10, "bold")
    )
    generation_label.pack(anchor="e")

    alive_label = tk.Label(
        stats,
        text="",
        bg=t["bg"],
        fg=t["muted"],
        font=("Helvetica", 9)
    )
    alive_label.pack(anchor="e")

    # Board
    board_frame = tk.Frame(
        outer,
        bg=t["panel"],
        highlightthickness=1,
        highlightbackground=t["grid"]
    )
    board_frame.pack()

    canvas = tk.Canvas(
        board_frame,
        width=BOARD_W,
        height=BOARD_H,
        bg=dead_colour,
        highlightthickness=0,
        cursor="hand2"
    )
    canvas.pack(padx=1, pady=1)
    canvas.bind("<Button-1>", toggle_cell)

    # Large touch-friendly controls
    controls = card(outer)
    controls.pack(fill="x", pady=(10, 0))

    controls_row = tk.Frame(controls, bg=t["panel"])
    controls_row.pack(fill="x", padx=10, pady=10)

    random_button = soft_button(
        controls_row, "Random", random_board, width=10
    )
    random_button.pack(side="left", expand=True, fill="x", padx=3)

    clear_button = soft_button(
        controls_row, "Clear", clear_board, width=10
    )
    clear_button.pack(side="left", expand=True, fill="x", padx=3)

    step_button = soft_button(
        controls_row, "Step", step, width=10
    )
    step_button.pack(side="left", expand=True, fill="x", padx=3)

    run_button = soft_button(
        controls_row, "▶ Run", start_game, width=10, accent=True
    )
    run_button.pack(side="left", expand=True, fill="x", padx=3)

    stop_button = soft_button(
        controls_row, "❚❚ Pause", stop_game, width=10
    )
    stop_button.pack(side="left", expand=True, fill="x", padx=3)

    bottom = tk.Frame(controls, bg=t["panel"])
    bottom.pack(fill="x", padx=13, pady=(0, 10))

    status_label = tk.Label(
        bottom,
        text="Paused",
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 9, "bold")
    )
    status_label.pack(side="left")

    tk.Label(
        bottom,
        text="Tap cells to draw • Space to run/pause • Esc for menu",
        bg=t["panel"],
        fg=t["muted"],
        font=("Helvetica", 8)
    ).pack(side="right")

    draw_board()
    update_game_controls()


def draw_board():
    if current_screen != "game" or canvas is None:
        return

    t = theme()
    canvas.delete("all")

    for r in range(ROWS):
        for c in range(COLS):
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            fill = alive_colour if board[r][c] else dead_colour

            # Small inset gives the cells a cleaner, softer appearance.
            canvas.create_rectangle(
                x1 + 1,
                y1 + 1,
                x2 - 1,
                y2 - 1,
                fill=fill,
                outline=t["grid"],
                width=1
            )

    if generation_label is not None:
        generation_label.config(text=f"Generation {generation}")

    if alive_label is not None:
        alive_label.config(text=f"{count_alive()} alive")


def toggle_cell(event):
    if running:
        return

    c = event.x // CELL_SIZE
    r = event.y // CELL_SIZE

    if 0 <= r < ROWS and 0 <= c < COLS:
        board[r][c] = 0 if board[r][c] else 1
        draw_board()


def update_game_controls():
    if current_screen != "game":
        return

    t = theme()

    if status_label is not None:
        if running:
            status_label.config(text="● Running", fg="#66D69A")
        else:
            status_label.config(text="● Paused", fg=t["muted"])

    if run_button is not None:
        run_button.config(state="disabled" if running else "normal")

    if stop_button is not None:
        stop_button.config(state="normal" if running else "disabled")

    if step_button is not None:
        step_button.config(state="disabled" if running else "normal")


# ============================================================
# KEYBOARD
# ============================================================

def keyboard_step(event=None):
    if current_screen == "game" and not running:
        step()


def keyboard_random(event=None):
    if current_screen == "game":
        random_board()


def keyboard_menu(event=None):
    if current_screen == "game":
        show_home()


root.bind("<space>", toggle_running)
root.bind("s", keyboard_step)
root.bind("S", keyboard_step)
root.bind("r", keyboard_random)
root.bind("R", keyboard_random)
root.bind("<Escape>", keyboard_menu)


# ============================================================
# CLOSE
# ============================================================

def close_app():
    stop_game()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)


# ============================================================
# START
# ============================================================

show_home()
root.mainloop()
