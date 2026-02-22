# gui.py
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os

# === CONFIG ===
SPRITE_SIZE = 64
BOARD_COLOR_LIGHT = "#4f8f5a"
BOARD_COLOR_DARK = "#427842"

SPRITE_PATH = os.path.join(
    "AlgoChess",
    "sprites",
    "PNG",
    "Double (128px)"
)

PIECES = ["pawn", "rook", "knight", "bishop", "queen", "king"]


# =========================
# SPRITE MANAGER
# =========================

class SpriteManager:
    def __init__(self):
        self.cache = {}
        self._load()
        self.empty = ImageTk.PhotoImage(
            Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))
        )
    def _load(self):
        for p in PIECES:
            filename = f"chess_{p}.png"
            path = os.path.join(SPRITE_PATH, filename)

            img = Image.open(path).convert("RGBA")
            img = img.resize((SPRITE_SIZE, SPRITE_SIZE), Image.LANCZOS)

            self.cache[f"white_{p}"] = ImageTk.PhotoImage(img)
            self.cache[f"black_{p}"] = ImageTk.PhotoImage(
                self._to_black(img)
            )

    def _to_black(self, img: Image.Image) -> Image.Image:
        r, g, b, a = img.split()
        gray = ImageOps.grayscale(Image.merge("RGB", (r, g, b)))
        dark = ImageOps.colorize(
            gray,
            black="#111111",
            white="#555555"
        )
        return Image.merge("RGBA", (*dark.split(), a))

    def get(self, name):
        return self.cache.get(name)


# =========================
# GUI
# =========================

class ChessGUI:
    def __init__(self, game):
        self.game = game
        self.forward_callback = None

        self.root = tk.Tk()
        self.root.title("AlgoChess")

        self.sprites = SpriteManager()

        self.turn_label = tk.Label(
            self.root,
            font=("Arial", 14, "bold")
        )
        self.turn_label.pack(pady=4)

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.cells = []
        for r in range(8):
            row = []
            for c in range(8):
                lbl = tk.Label(
                    self.board_frame,
                    image=None,
                    bd=0,
                    highlightthickness=0,
                    bg=(
                        BOARD_COLOR_LIGHT
                        if (r + c) % 2 == 0
                        else BOARD_COLOR_DARK
                    )
                )
                lbl.grid(row=r, column=c)
                row.append(lbl)
            self.cells.append(row)

        ctrl = tk.Frame(self.root)
        ctrl.pack(pady=8)

        tk.Button(ctrl, text="← Back", command=self.back).pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl, text="→ Forward", command=self.forward).pack(side=tk.LEFT, padx=5)

        self.draw()

    def bind_forward(self, cb):
        self.forward_callback = cb

    def draw(self):
        for r in range(8):
            for c in range(8):
                cell = self.cells[r][c]
                cell.config(
                    image=self.sprites.empty,
                    bg=(
                        BOARD_COLOR_LIGHT
                        if (r + c) % 2 == 0
                        else BOARD_COLOR_DARK
                    )
                )
                cell.image = self.sprites.empty

                piece = self.game.board[r][c]
                if piece:
                    img = self.sprites.get(piece)
                    cell.config(image=img)
                    cell.image = img  # IMPORTANT: keep reference

        if self.game.game_over:
            reason = self.game.game_over_reason or "game ended"
            self.turn_label.config(
                text=f"GAME OVER — {self.game.winner.upper()} ({reason})"
            )
        else:
            self.turn_label.config(
                text=f"Turn: {self.game.current_player.upper()}"
            )

    def forward(self):
        if self.forward_callback:
            self.forward_callback()
            self.draw()

    def back(self):
        if self.game.undo_move():
            self.draw()

    def run(self):
        self.root.mainloop()