# api.py
# Public Bot API – safe, read-only helpers

# =========================
# BASIC BOARD OPERATIONS
# =========================

def get_all_valid_moves(board, color):
    from engine import ChessGame
    g = ChessGame()
    g.board = board
    g.current_player = color
    return g.get_all_valid_moves(color)


def clone_board(board):
    return [row[:] for row in board]


def inside_board(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def get_piece(board, row, col):
    if not inside_board(row, col):
        return None
    return board[row][col]


def is_empty(board, row, col):
    return get_piece(board, row, col) == ""


def is_white(piece):
    return piece.startswith("white")


def is_black(piece):
    return piece.startswith("black")


def piece_color(piece):
    if piece.startswith("white"):
        return "white"
    if piece.startswith("black"):
        return "black"
    return None


def piece_type(piece):
    return piece.split("_")[1]


# =========================
# PIECE COLLECTION
# =========================

def get_all_pieces(board, color):
    result = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.startswith(color):
                result.append((r, c, p))
    return result


def get_all_enemy_pieces(board, color):
    enemy = "black" if color == "white" else "white"
    return get_all_pieces(board, enemy)


def count_pieces(board, color):
    return len(get_all_pieces(board, color))


def count_piece_type(board, color, ptype):
    return sum(
        1 for _, _, p in get_all_pieces(board, color)
        if piece_type(p) == ptype
    )


# =========================
# POSITION / COORDS
# =========================

def coords_to_position(row, col):
    return f"{chr(ord('a') + col)}{8 - row}"


def position_to_coords(pos):
    col = ord(pos[0]) - ord("a")
    row = 8 - int(pos[1])
    return row, col


# =========================
# KING / STATUS
# =========================

def find_king(board, color):
    target = f"{color}_king"
    for r in range(8):
        for c in range(8):
            if board[r][c] == target:
                return r, c
    return None


def is_king_alive(board, color):
    return find_king(board, color) is not None


def enemy_color(color):
    return "black" if color == "white" else "white"


# =========================
# MATERIAL EVALUATION
# =========================

PIECE_VALUE = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
    "king": 1000,
}


def material_score(board, color):
    score = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if not p:
                continue
            v = PIECE_VALUE[piece_type(p)]
            score += v if p.startswith(color) else -v
    return score


def material_diff(board):
    return material_score(board, "white") - material_score(board, "black")


# =========================
# MOVE HELPERS (DUMB)
# =========================

def generate_all_targets():
    for r in range(8):
        for c in range(8):
            yield r, c


def random_piece(board, color):
    import random
    pieces = get_all_pieces(board, color)
    return random.choice(pieces) if pieces else None


def random_move(board, color):
    import random
    p = random_piece(board, color)
    if not p:
        return None
    r, c, _ = p
    tr = random.randint(0, 7)
    tc = random.randint(0, 7)
    return (
        coords_to_position(r, c),
        coords_to_position(tr, tc)
    )


# =========================
# BOARD SCANS
# =========================

def is_column_open(board, col):
    return all(board[r][col] == "" for r in range(8))


def is_row_open(board, row):
    return all(board[row][c] == "" for c in range(8))


def pieces_in_column(board, col):
    return [(r, board[r][col]) for r in range(8) if board[r][col]]


def pieces_in_row(board, row):
    return [(c, board[row][c]) for c in range(8) if board[row][c]]


# =========================
# PAWN STRUCTURE (BASIC)
# =========================

def pawns(board, color):
    return [
        (r, c) for r, c, p in get_all_pieces(board, color)
        if piece_type(p) == "pawn"
    ]


def pawn_count(board, color):
    return len(pawns(board, color))


def doubled_pawns(board, color):
    seen = set()
    doubled = 0
    for _, c in pawns(board, color):
        if c in seen:
            doubled += 1
        seen.add(c)
    return doubled


# =========================
# THREATS (VERY ROUGH)
# =========================

def square_has_enemy(board, row, col, color):
    p = get_piece(board, row, col)
    return p and piece_color(p) != color


def adjacent_squares(row, col):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            yield row + dr, col + dc