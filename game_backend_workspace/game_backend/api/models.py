from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# PUBLIC_INTERFACE
class User(AbstractUser):
    """
    PUBLIC_INTERFACE
    Custom user model for Tic Tac Toe users. Inherits from Django's AbstractUser.
    """
    # You can add extra fields here if needed
    pass


# PUBLIC_INTERFACE
class Game(models.Model):
    """
    PUBLIC_INTERFACE
    Represents a Tic Tac Toe game session.
    """
    PLAYER_X = 'X'
    PLAYER_O = 'O'
    EMPTY = ''

    PLAYER_CHOICES = [
        (PLAYER_X, 'Player X'),
        (PLAYER_O, 'Player O'),
    ]

    board = models.JSONField(
        default=list,
        help_text='A list of 9 strings representing the board (row major, 0-based flat index).'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    player_x = models.ForeignKey(
        User, related_name='games_as_x', on_delete=models.CASCADE
    )
    player_o = models.ForeignKey(
        User, related_name='games_as_o', on_delete=models.CASCADE, null=True, blank=True
    )
    current_turn = models.CharField(
        max_length=1, choices=PLAYER_CHOICES, default=PLAYER_X
    )
    winner = models.CharField(
        max_length=1, choices=PLAYER_CHOICES, null=True, blank=True
    )
    is_draw = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)

    def reset_board(self):
        """Reset the game board and state."""
        self.board = [self.EMPTY for _ in range(9)]
        self.current_turn = self.PLAYER_X
        self.winner = None
        self.is_draw = False
        self.is_finished = False
        self.save()

    # PUBLIC_INTERFACE
    def make_move(self, user, position):
        """
        Attempt to make a move as the given user at the provided position.
        Returns a tuple: (success: bool, message: str, updated: bool)
        """
        if self.is_finished:
            return False, "Game already finished.", False

        if user != self.player_x and user != self.player_o:
            return False, "Not a player in this game.", False

        symbol = self.PLAYER_X if user == self.player_x else self.PLAYER_O
        if self.current_turn != symbol:
            return False, "It's not your turn.", False

        try:
            position = int(position)
        except ValueError:
            return False, "Invalid position.", False

        if (
            position < 0 or position >= 9 or
            self.board[position] != self.EMPTY
        ):
            return False, "Invalid or already occupied cell.", False

        self.board[position] = symbol
        self.updated = timezone.now()

        # Check for win
        if self.check_win(symbol):
            self.winner = symbol
            self.is_finished = True
            self.save()
            return True, f'Player {symbol} wins!', True

        # Check for draw
        if self.EMPTY not in self.board:
            self.is_draw = True
            self.is_finished = True
            self.save()
            return True, 'Game is a draw.', True

        # Continue game
        self.current_turn = self.PLAYER_O if symbol == self.PLAYER_X else self.PLAYER_X
        self.save()
        return True, "Move accepted.", True

    # PUBLIC_INTERFACE
    def check_win(self, symbol):
        """Check if the given symbol has won on the current board."""
        b = self.board
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6],             # Diagonals
        ]
        for pattern in win_patterns:
            if all(b[i] == symbol for i in pattern):
                return True
        return False
