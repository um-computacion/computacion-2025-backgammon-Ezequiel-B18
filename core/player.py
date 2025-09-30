"""Player class for backgammon game."""

from enum import Enum, auto
from core.checker import Checker, CheckerColor, CheckerState
from core.exceptions import NoMovesRemainingError


class PlayerColor(Enum):
    """Enum representing the possible colors (sides) of a player."""

    WHITE = auto()
    BLACK = auto()


class Player:
    """
    Represents a backgammon player.
    Focuses solely on player-specific concerns: identity, turn management, and checker collection.
    """

    def __init__(self, name, color):
        """
        Initialize a player with a name and color.

        Args:
            name (str): The player's name
            color (PlayerColor): The player's color (WHITE or BLACK)
        """
        self.name = name
        self.color = color

        # Player ID (1 for white, 2 for black) for board interactions
        self.player_id = 1 if color == PlayerColor.WHITE else 2

        # Initialize 15 checkers with corresponding color
        checker_color = (
            CheckerColor.WHITE if color == PlayerColor.WHITE else CheckerColor.BLACK
        )
        self.__checkers__ = [Checker(checker_color) for _ in range(15)]

        # Turn and move tracking
        self.is_turn = False
        self.remaining_moves = 0

    @property
    def checkers(self):
        """Access to the player's list of checkers (element mutation allowed)."""
        return self.__checkers__

    def get_starting_positions(self):
        """
        Get the standard starting positions for this player's checkers.

        Returns:
            list: List of tuples (point_index, checker_count)
        """
        if self.color == PlayerColor.WHITE:
            return [(0, 2), (11, 5), (16, 3), (18, 5)]
        return [(23, 2), (12, 5), (7, 3), (5, 5)]

    def distribute_checkers(self, _board):
        """
        Assign initial positions to this player's Checker objects based on the
        standard starting layout.
        Important: this method no longer mutates board.points.
        Board.setup_starting_positions() should be called by the orchestrator
        (Game) to initialize the board. This keeps Board as the single source
        of truth.
        """
        starting_positions = self.get_starting_positions()
        checker_index = 0

        for point, count in starting_positions:
            for _ in range(count):
                if checker_index < len(self.checkers):
                    self.checkers[checker_index].set_position(point)
                    checker_index += 1

    def start_turn(self, dice):
        """
        Start the player's turn with a dice roll.

        Args:
            dice: The dice roll
        """
        self.is_turn = True
        moves = dice.get_moves()
        self.remaining_moves = len(moves)

    def end_turn(self):
        """End the player's turn."""
        self.is_turn = False
        self.remaining_moves = 0

    def use_move(self):
        """
        Use a move during the player's turn.

        Returns:
            bool: True if successful, False if no moves remaining
        """
        if self.remaining_moves <= 0:
            raise NoMovesRemainingError(self.name)

        self.remaining_moves -= 1
        return True

    def get_checkers_by_state(self, state):
        """
        Get all checkers in a specific state.

        Args:
            state (CheckerState): The state to filter by (ON_BOARD, ON_BAR, BORNE_OFF)

        Returns:
            list: List of checkers in the specified state
        """
        return [checker for checker in self.checkers if checker.state == state]

    def count_checkers_by_state(self, state):
        """
        Count how many checkers are in a specific state.

        Args:
            state (CheckerState): The state to count

        Returns:
            int: Number of checkers in the specified state
        """
        return len(self.get_checkers_by_state(state))

    def has_checkers_on_bar(self):
        """
        Check if the player has any checkers on the bar.

        Returns:
            bool: True if there are checkers on the bar, False otherwise
        """
        return any(checker.state == CheckerState.ON_BAR for checker in self.checkers)

    def has_won(self):
        """
        Check if the player has won (all checkers borne off).

        Returns:
            bool: True if all checkers are borne off, False otherwise
        """
        return all(checker.state == CheckerState.BORNE_OFF for checker in self.checkers)

    def __str__(self):
        """String representation of the player"""
        on_board = self.count_checkers_by_state(CheckerState.ON_BOARD)
        on_bar = self.count_checkers_by_state(CheckerState.ON_BAR)
        borne_off = self.count_checkers_by_state(CheckerState.BORNE_OFF)

        turn_status = (
            f"in turn ({self.remaining_moves} moves)" if self.is_turn else "not in turn"
        )

        return (
            f"{self.name} ({self.color.name}): {on_board} on board, "
            f"{on_bar} on bar, {borne_off} borne off, {turn_status}"
        )
