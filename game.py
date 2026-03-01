# game.py
from engine import ChessGame
from gui import ChessGUI
import importlib
import traceback

def load_bot(path):
    module = importlib.import_module(path)
    return module.ChooseMove

def main():
    game = ChessGame()

    black_bot = load_bot(input("Введите путь(относительный к боту 1: "))
    white_bot = load_bot(input("Введите путь(относительный к боту 2: "))

    # white_bot = load_bot("adaptive")
    # black_bot = load_bot("greedy")
    

    gui = ChessGUI(game)

    def step():
        if game.game_over and not getattr(game, "redo_history", []):
            return

        if getattr(game, "redo_history", []):
            game.redo_move()
            gui.draw()
            return

        bot = white_bot if game.current_player == "white" else black_bot

        try:
            move = bot(game.board, game.current_player)
        except Exception:
            game.game_over = True
            game.winner = "black" if game.current_player == "white" else "white"
            game.game_over_reason = "bot crashed"
            gui.draw()
            return

        if not move or not game.make_move(*move):
            gui.draw()
            return

        gui.draw()


    gui.bind_forward(step)
    gui.run()

if __name__ == "__main__":
    main()