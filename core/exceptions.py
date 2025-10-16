"""Custom exceptions for the backgammon game.

This module defines custom exceptions used throughout the game,
following SOLID principles and TDD methodology.
"""


class GameQuitException(Exception):
    """Exception raised when user wants to quit the game."""


# Base Exception
class BackgammonError(Exception):
    """Base exception for all backgammon game errors."""


# Game-level exceptions (already in use)
class GameError(BackgammonError):
    """Base exception for game-level errors."""


class GameNotInitializedError(GameError):
    """Raised when trying to perform actions on an uninitialized game."""


class InvalidPlayerTurnError(GameError):
    """Raised when a player tries to act when it's not their turn."""


class GameAlreadyOverError(GameError):
    """Raised when trying to perform actions on a finished game."""


class InvalidMoveError(GameError):
    """Raised when attempting an invalid move."""

    def __init__(self, from_point, to_point, reason=None):
        self.from_point = from_point
        self.to_point = to_point
        self.reason = reason
        message = f"Invalid move from {from_point} to {to_point}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


# Board-level exceptions (to be used based on tests)
class BoardError(BackgammonError):
    """Base exception for board-related errors."""


class InvalidPointError(BoardError):
    """Raised when trying to access an invalid board point."""

    def __init__(self, point, message=None):
        self.point = point
        if message is None:
            message = f"Invalid point: {point}. Points must be between 0-23."
        super().__init__(message)


# Player-level exceptions (to be used based on tests)
class PlayerError(BackgammonError):
    """Base exception for player-related errors."""


class InvalidPlayerColorError(PlayerError):
    """Raised when an invalid player color is specified."""


# Checker-level exceptions (to be used based on tests)
class CheckerError(BackgammonError):
    """Base exception for checker-related errors."""


class InvalidCheckerPositionError(CheckerError):
    """Raised when trying to set an invalid checker position."""

    def __init__(self, position, valid_range="0-23"):
        self.position = position
        self.valid_range = valid_range
        super().__init__(f"Position must be between {valid_range}, got {position}")


# Dice-level exceptions (to be used based on tests)
class DiceError(BackgammonError):
    """Base exception for dice-related errors."""


# Specific Player Exceptions
class NoMovesRemainingError(PlayerError):
    """Raised when a player tries to move with no remaining moves."""

    def __init__(self, player_name):
        self.player_name = player_name
        super().__init__(f"Player {player_name} has no remaining moves")


class InvalidCheckerCountError(PlayerError):
    """Raised when a player has an invalid number of checkers."""

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Expected {expected} checkers, but got {actual}")


# Specific Dice Exceptions
class DiceNotRolledError(DiceError):
    """Raised when trying to access dice values before rolling."""


class InvalidDiceValueError(DiceError):
    """Raised when dice show invalid values."""

    def __init__(self, value):
        self.value = value
        super().__init__(f"Invalid dice value: {value}. Must be between 1-6.")


# Specific Checker Exceptions
class InvalidCheckerStateError(CheckerError):
    """Raised when a checker is in an invalid state."""

    def __init__(self, current_state, expected_state=None):
        self.current_state = current_state
        self.expected_state = expected_state
        message = f"Invalid checker state: {current_state}"
        if expected_state:
            message += f". Expected: {expected_state}"
        super().__init__(message)


class CheckerPositionError(CheckerError):
    """Raised when a checker has an invalid position."""

    def __init__(self, position, state):
        self.position = position
        self.state = state
        super().__init__(f"Invalid position {position} for checker in state {state}")
