# Copyright (C) 2015  aws

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import random
import sys
from enum import Enum

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSound
from PyQt5 import QtWidgets

from Dialog import *
from tictactoe_ui import Ui_tictactoe

class PlayerType(Enum):
    PLAYER_X = 0
    PLAYER_O = 1

class GameState(Enum):
    PLAYING = 0
    ENDED = 1

class QLearningPlayer:
    def __init__(self, player_type, epsilon=0.2, alpha=0.3, gamma=0.9):
        self.q = {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.type = player_type
        self.human = False

    def reset(self):
        self.last_board = [0] * 9
        self.last_move = None

    def getQ(self, state, action):
        if self.q.get((state, action)) is None:
            self.q[(state, action)] = 1.0

        return self.q.get((state, action))

    def reward(self, value, board):
        if self.last_move:
            self.learn(self.last_board, self.last_move, value, tuple(board))

    def learn(self, state, action, reward, result_state):
        prev = self.getQ(state, action)
        maxqnew = max([self.getQ(result_state, a) for a in self.available_moves(state)])
        self.q[(state, action)] = prev + self.alpha * ((reward + self.gamma * maxqnew) - prev)

    def available_moves(self, board):
        return [i for i in range(0, 9) if board[i] == 0]

    def get_player_identifier(self):
        if self.type == PlayerType.PLAYER_X:
            return 1
        else:
            return 2

    def move(self, board):
        self.last_board = tuple(board)
        actions = self.available_moves(board)

        if random.random() < self.epsilon:
            self.last_move = random.choice(actions)
            return self.last_move

        qs = [self.getQ(self.last_board, a) for a in actions]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            # More than 1 best option; choose among them wisely
            best_options = [i for i in range(len(actions)) if qs[i] == maxQ]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ)

        self.last_move = actions[i]
        return actions[i]

    def __str__(self):
        if self.type == PlayerType.PLAYER_X:
            return "Player X"
        else:
            return "Player O"

    __repr__ = __str__


class Game(QMainWindow, Ui_tictactoe):
    def __init__(self, playerX, playerO, interactive=True, parent=None):
        self.interactive = interactive
        super().__init__(parent)
        self.board = [0] * 9
        self.playerX, self.playerO = playerX, playerO
        self.current_player = random.choice([self.playerX, self.playerO])
        self.game_state = GameState.PLAYING
        self.winner = None

        self.setupUi(self)

        self.timer = QTimer()

        # Shows only the close button
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.sounds = dict(circle=QSound("circle.wav"),
                           cross=QSound("cross.wav"),
                           win=QSound("win.wav"),
                           lose=QSound("lose.wav"))

        xIconPath = os.path.join("Icons", "x.png")
        oIconPath = os.path.join("Icons", "o.png")

        self.xIcon = QIcon(xIconPath)
        self.oIcon = QIcon(oIconPath)

        # To make the icons appear in full color while disabled
        self.xIcon.addPixmap(QPixmap(xIconPath), QIcon.Disabled)
        self.oIcon.addPixmap(QPixmap(oIconPath), QIcon.Disabled)

        self.allButtons = self.frame.findChildren(QToolButton)
        self.defaultPalette = QApplication.palette()

        self.board_to_button_mapping = [self.button1, self.button2, self.button3, self.button4, self.button5,
                                        self.button6, self.button7, self.button8, self.button9]

        # across the top
        self.winCombo1 = [0, 1, 2]

        # across the middle
        self.winCombo2 = [3, 4, 5]

        # across the bottom
        self.winCombo3 = [6, 7, 8]

        # down the left side
        self.winCombo4 = [0, 3, 6]

        # down the middle
        self.winCombo5 = [1, 4, 7]

        # down the right side
        self.winCombo6 = [2, 5, 8]

        # diagonal
        self.winCombo7 = [0, 4, 8]

        # diagonal
        self.winCombo8 = [2, 4, 6]

        # connections
        for button in self.allButtons:
            button.clicked.connect(self.button_clicked)

        self.actionNew_Game.triggered.connect(self.new_game)
        self.actionDark_Theme.toggled.connect(self.dark_theme)
        self.action_Exit.triggered.connect(self.close)

        self.setFocus()  # sets the focus to the main window
        self.new_game()  # starts a new game

    def is_board_full(self):
        return 0 not in self.board

    def switch_player(self):
        if self.current_player.type == PlayerType.PLAYER_X:
            self.current_player = self.playerO
        else:
            self.current_player = self.playerX

    def play(self):
        while not self.is_board_full():
            if self.current_player.human is False:
                move = self.current_player.move(self.board)
                self.execute_move(move, self.current_player.get_player_identifier())

                if self.game_state == GameState.ENDED:
                    # Check who won the game
                    if self.winner == self.playerX:
                        self.playerX.reward(10, self.board)
                        self.playerO.reward(-10, self.board)
                    elif self.winner == self.playerO:
                        self.playerO.reward(10, self.board)
                        self.playerX.reward(-10, self.board)
                    else:
                        self.playerX.reward(5, self.board)
                        self.playerO.reward(5, self.board)
                    return
                else:
                    self.switch_player()
            else:
                return

    def autoplay(self, num_games=10):
        assert self.playerX is not None
        assert self.playerO is not None

        games_played = 0
        while games_played < num_games:
            print("Autoplaying: %s" % games_played)
            self.play()
            self.new_game()
            games_played += 1

    def execute_move(self, pos, value):
        self.board[pos] = value
        button = self.board_to_button_mapping[pos]
        self.button_clicked(button)

    def new_game(self):
        self.reset()

    def reset(self):
        self.playerX.reset()
        self.playerO.reset()
        self.current_player = random.choice([self.playerX, self.playerO])
        self.frame.setEnabled(True)
        self.board = [0] * 9
        self.game_state = GameState.PLAYING
        self.winner = None

        for button in self.allButtons[:]:
            button.setText("")
            button.setIcon(QIcon())
            button.setEnabled(True)

    def check(self):
        if self.check_list(self.winCombo1):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo2):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo3):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo4):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo5):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo6):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo7):
            return self.end_game(self.current_player)

        elif self.check_list(self.winCombo8):
            return self.end_game(self.current_player)
        elif self.is_board_full():
            return self.end_game(None)

    def check_list(self, lst):
        for member in lst:
            if self.board[member] != self.current_player.get_player_identifier():
                return False
        return True

    def end_game(self, player):
        """Ends the game"""

        self.winner = player
        if player is None:
            if self.interactive:
                Dialog(self, 3).show()

            for button in self.allButtons:
                button.setEnabled(False)
            self.game_state = GameState.ENDED
            return True

        elif player.type == PlayerType.PLAYER_X:
            if self.interactive:
                self.sounds["win"].play()
                Dialog(self, 1).show()

            for button in self.allButtons:
                button.setEnabled(False)
            self.game_state = GameState.ENDED
            return True

        elif player.type == PlayerType.PLAYER_O:
            if self.interactive:
                self.sounds["lose"].play()
                Dialog(self, 2).show()

            for button in self.allButtons:
                button.setEnabled(False)
            self.game_state = GameState.ENDED
            return True

        return False

    def update_button(self, button, player_type):
        if player_type == PlayerType.PLAYER_X:
            if self.interactive:
                self.sounds["cross"].play()
            button.setText("1")
            button.setIcon(self.xIcon)
        else:
            if self.interactive:
                self.sounds["circle"].play()
            button.setText("2")
            button.setIcon(self.oIcon)

        button.setEnabled(False)

    def button_clicked(self, button=None):
        if button is None or type(button) != QtWidgets.QToolButton:
            button = self.sender()

            # In this case manually figure out which button this maps to
            for move, b in enumerate(self.board_to_button_mapping):
                if b == button:
                    self.execute_move(move, self.current_player.get_player_identifier())
                    if self.game_state == GameState.PLAYING:
                        self.switch_player()
                        self.play()
                    return

        self.update_button(button, self.current_player.type)

        if self.check():
            return

    def dark_theme(self):
        """Changes the theme between dark and normal"""
        if self.actionDark_Theme.isChecked():
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15, 15, 15))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(0, 24, 193).lighter())
            palette.setColor(QPalette.HighlightedText, Qt.black)
            palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            palette.setColor(
                QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
            app.setPalette(palette)
            return

        app.setPalette(self.defaultPalette)


app = QApplication(sys.argv)

def main():
    playerX = QLearningPlayer(PlayerType.PLAYER_X)
    playerO = QLearningPlayer(PlayerType.PLAYER_O)
    game = Game(playerX, playerO)
    game.show()
    game.interactive = False
    game.autoplay(1000000)
    game.interactive = True
    playerX.human = True
    game.play()
    app.exec_()

if __name__ == "__main__":
    main()