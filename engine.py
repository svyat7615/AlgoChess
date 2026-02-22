# engine.py

class ChessGame:
    def __init__(self):
        self.meta_history = []
        self.redo_history = []
        self.redo_move_history = []
        self.redo_meta_history = []

        self.board = self._create_initial_board()
        self.current_player = "white"
        self.history = []
        self.move_history = []
        self.game_over = False
        self.winner = None
        self.game_over_reason = None

    def _create_initial_board(self):
        board = [["" for _ in range(8)] for _ in range(8)]

        for c in range(8):
            board[1][c] = "black_pawn"
            board[6][c] = "white_pawn"

        pieces = [
            "rook", "knight", "bishop", "queen",
            "king", "bishop", "knight", "rook"
        ]

        for c, p in enumerate(pieces):
            board[0][c] = f"black_{p}"
            board[7][c] = f"white_{p}"

        return board

    # =========================
    # COORDS
    # =========================

    def position_to_coords(self, pos):
        col = ord(pos[0].lower()) - ord("a")
        row = 8 - int(pos[1])
        return row, col

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    # =========================
    # MOVE VALIDATION
    # =========================

    def is_valid_move(self, start_pos, end_pos):
        try:
            sr, sc = self.position_to_coords(start_pos)
            er, ec = self.position_to_coords(end_pos)
        except Exception:
            return False

        if not self.inside(sr, sc) or not self.inside(er, ec):
            return False

        piece = self.board[sr][sc]
        if not piece or not piece.startswith(self.current_player):
            return False

        target = self.board[er][ec]
        if target and target.startswith(self.current_player):
            return False

        color, ptype = piece.split("_")
        dr = er - sr
        dc = ec - sc

        # ---- PAWN ----
        if ptype == "pawn":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1

            if dc == 0:
                if dr == direction and not target:
                    return True
                if dr == 2 * direction and sr == start_row:
                    mid = sr + direction
                    return not target and not self.board[mid][sc]

            if abs(dc) == 1 and dr == direction:
                return target and not target.startswith(color)

            return False

        # ---- KNIGHT ----
        if ptype == "knight":
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]

        # ---- KING ----
        if ptype == "king":
            return abs(dr) <= 1 and abs(dc) <= 1

        # ---- SLIDING PIECES ----
        if ptype in ("rook", "bishop", "queen"):
            if ptype == "rook" and dr != 0 and dc != 0:
                return False
            if ptype == "bishop" and abs(dr) != abs(dc):
                return False
            if ptype == "queen" and not (
                dr == 0 or dc == 0 or abs(dr) == abs(dc)
            ):
                return False

            step_r = (dr > 0) - (dr < 0)
            step_c = (dc > 0) - (dc < 0)

            r, c = sr + step_r, sc + step_c
            while (r, c) != (er, ec):
                if self.board[r][c]:
                    return False
                r += step_r
                c += step_c

            return True

        return False

    # =========================
    # MAKE MOVE
    # =========================

    def make_move(self, start_pos, end_pos):
        if self.game_over:
            return False

        if not self.is_valid_move(start_pos, end_pos):
            self.game_over = True
            self.winner = (
                "black" if self.current_player == "white" else "white"
            )
            self.game_over_reason = "invalid move"
            return False

        sr, sc = self.position_to_coords(start_pos)
        er, ec = self.position_to_coords(end_pos)

        self.history.append([row[:] for row in self.board])
        self.meta_history.append((
            self.current_player, self.game_over, self.winner, self.game_over_reason
        ))
        self.move_history.append((start_pos, end_pos))

        self.redo_history.clear()
        self.redo_move_history.clear()
        self.redo_meta_history.clear()

        captured = self.board[er][ec]
        self.board[er][ec] = self.board[sr][sc]
        self.board[sr][sc] = ""

        if captured == "white_king":
            self.game_over = True
            self.winner = "black"
            self.game_over_reason = "king captured"
        elif captured == "black_king":
            self.game_over = True
            self.winner = "white"
            self.game_over_reason = "king captured"

        self.current_player = (
            "black" if self.current_player == "white" else "white"
        )
        return True

    def undo_move(self):
        if not self.history:
            return False

        self.redo_history.append([row[:] for row in self.board])
        self.redo_meta_history.append((
            self.current_player, self.game_over, self.winner, self.game_over_reason
        ))
        self.redo_move_history.append(self.move_history.pop())

        self.board = self.history.pop()
        self.current_player, self.game_over, self.winner, self.game_over_reason = self.meta_history.pop()
        return True

    def redo_move(self):
        if not self.redo_history:
            return False

        self.history.append([row[:] for row in self.board])
        self.meta_history.append((
            self.current_player, self.game_over, self.winner, self.game_over_reason
        ))
        self.move_history.append(self.redo_move_history.pop())

        self.board = self.redo_history.pop()
        self.current_player, self.game_over, self.winner, self.game_over_reason = self.redo_meta_history.pop()
        return True


    def get_all_valid_moves(self, color=None):
        color = color or self.current_player
        moves = []
        for sr in range(8):
            for sc in range(8):
                piece = self.board[sr][sc]
                if not piece or not piece.startswith(color):
                    continue
                start = f"{chr(ord('a') + sc)}{8 - sr}"
                for er in range(8):
                    for ec in range(8):
                        end = f"{chr(ord('a') + ec)}{8 - er}"
                        cur = self.current_player
                        self.current_player = color
                        ok = self.is_valid_move(start, end)
                        self.current_player = cur
                        if ok:
                            moves.append((start, end))
        return moves
