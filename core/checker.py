"""Checker class for backgammon game."""

from enum import Enum, auto
from core.exceptions import InvalidCheckerPositionError


class CheckerColor(Enum):
    """Enum representing the possible colors of a checker."""

    WHITE = auto()
    BLACK = auto()


class CheckerState(Enum):
    """Enum representing the possible states of a checker."""

    ON_BOARD = auto()  # Checker is on the board
    ON_BAR = auto()  # Checker is on the bar (after being hit)
    BORNE_OFF = auto()  # Checker has been borne off (removed from board)


class Checker:
    """
    Represents a backgammon checker (piece).
    Handles checker state, position, and movement rules.
    """

    def __init__(self, color):
        """
        Initialize a checker with a specific color.

        Args:
            color (CheckerColor): The color of the checker (WHITE or BLACK)
        """
        self.__color__ = color
        self.__state__ = CheckerState.ON_BOARD
        self.__position__ = None

    @property
    def color(self):
        """Get the color of the checker."""
        return self.__color__

    @property
    def state(self):
        """Get the current state of the checker."""
        return self.__state__

    @state.setter
    def state(self, value):
        """Set the state of the checker."""
        self.__state__ = value

    @property
    def position(self):
        """Get the current position of the checker."""
        return self.__position__

    @position.setter
    def position(self, value):
        """Set the position of the checker."""
        self.__position__ = value

    def set_position(self, position):
        """
        Set the initial position of the checker on the board.

        Args:
            position (int): Point index (0-23) where the checker is placed
        """
        if not 0 <= position <= 23:
            raise InvalidCheckerPositionError(position)

        self.__position__ = position
        self.__state__ = CheckerState.ON_BOARD

    def move_to_position(self, new_position):
        """
        Move the checker to a new position on the board.

        Args:
            new_position (int): Target point index (0-23)
        """
        if not 0 <= new_position <= 23:
            raise InvalidCheckerPositionError(new_position)

        self.__position__ = new_position
        self.__state__ = CheckerState.ON_BOARD

    def calculate_new_position(self, dice_value):
        """
        Calculate the new position after moving by dice_value.
        White moves from low to high (0->23), Black moves from high to low (23->0).
        """
        if self.__state__ != CheckerState.ON_BOARD:
            raise ValueError("Checker must be on board to calculate new position")

        if self.position is None:
            raise ValueError("Checker position must be set")

        if self.__color__ == CheckerColor.WHITE:
            new_position = self.position + dice_value
        else:  # BLACK
            new_position = self.position - dice_value

        return new_position

    def send_to_bar(self):
        """Send this checker to the bar (after being hit)"""
        self.__state__ = CheckerState.ON_BAR
        self.__position__ = None

    def enter_from_bar(self, position):
        """Enter a checker from the bar to the specified position."""
        if self.__state__ != CheckerState.ON_BAR:
            return False

        # Validate entry points based on color
        if self.__color__ == CheckerColor.WHITE:
            if not 0 <= position <= 5:
                raise InvalidCheckerPositionError(position, "0-5")
        else:  # BLACK
            if not 18 <= position <= 23:
                raise InvalidCheckerPositionError(position, "18-23")

        self.position = position
        self.__state__ = CheckerState.ON_BOARD
        return True

    def bear_off(self):
        """
        Bear off the checker (remove it from the board).

        Raises:
            ValueError: If the checker is not in its home board
        """
        if self.__state__ != CheckerState.ON_BOARD:
            raise ValueError("Cannot bear off: checker not on board")

        if not self.is_in_home_board():
            raise ValueError("Cannot bear off: checker not in home board")

        self.__state__ = CheckerState.BORNE_OFF
        self.__position__ = None

    def is_in_home_board(self):
        """Check if the checker is in its home board."""
        if self.position is None:
            return False

        if self.__color__ == CheckerColor.WHITE:
            return 18 <= self.position <= 23
        # BLACK
        return 0 <= self.position <= 5

    def can_bear_off_with_value(self, dice_value):
        """Check if this checker can be borne off with the given dice value."""
        if not self.is_in_home_board():
            return False

        if self.__color__ == CheckerColor.WHITE:
            needed_value = 24 - self.position
        else:  # BLACK
            needed_value = self.position + 1

        return dice_value >= needed_value

    def __str__(self):
        """String representation of the checker"""
        color_name = "White" if self.__color__ == CheckerColor.WHITE else "Black"
        state_name = self.__state__.name
        pos_str = f"pos={self.__position__}"
        return f"{color_name}({state_name}, {pos_str})"

    def to_dict(self):
        """Converts the Checker object to a dictionary."""
        return {
            "color": self.color.name,
            "state": self.state.name,
            "position": self.position,
        }

    @staticmethod
    def from_dict(data):
        """Creates a Checker object from a dictionary."""
        color = CheckerColor[data["color"]]
        checker = Checker(color)
        checker.__state__ = CheckerState[data["state"]]
        checker.position = data["position"]
        return checker