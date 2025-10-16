"""Tests for the exceptions module."""

import unittest
from core.exceptions import (
    BackgammonError,
    GameError,
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
    BoardError,
    InvalidPointError,
    PlayerError,
    InvalidPlayerColorError,
    CheckerError,
    InvalidCheckerPositionError,
    DiceError,
    NoMovesRemainingError,
    InvalidCheckerCountError,
    DiceNotRolledError,
    InvalidDiceValueError,
    InvalidCheckerStateError,
    CheckerPositionError,
    GameQuitException,
)


class TestExceptions(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for custom exception classes."""

    def test_backgammon_error_base(self):
        """Test BackgammonError base exception."""
        error = BackgammonError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertIsInstance(error, Exception)

    def test_game_error(self):
        """Test GameError exception."""
        error = GameError("Game error")
        self.assertEqual(str(error), "Game error")
        self.assertIsInstance(error, BackgammonError)

    def test_game_not_initialized_error(self):
        """Test GameNotInitializedError exception."""
        error = GameNotInitializedError("Game not initialized")
        self.assertEqual(str(error), "Game not initialized")
        self.assertIsInstance(error, GameError)

    def test_invalid_player_turn_error(self):
        """Test InvalidPlayerTurnError exception."""
        error = InvalidPlayerTurnError("Invalid turn")
        self.assertEqual(str(error), "Invalid turn")
        self.assertIsInstance(error, GameError)

    def test_game_already_over_error(self):
        """Test GameAlreadyOverError exception."""
        error = GameAlreadyOverError("Game over")
        self.assertEqual(str(error), "Game over")
        self.assertIsInstance(error, GameError)

    def test_invalid_move_error_without_reason(self):
        """Test InvalidMoveError without reason."""
        error = InvalidMoveError(5, 10)
        self.assertEqual(error.from_point, 5)
        self.assertEqual(error.to_point, 10)
        self.assertIsNone(error.reason)
        self.assertEqual(str(error), "Invalid move from 5 to 10")
        self.assertIsInstance(error, GameError)

    def test_invalid_move_error_with_reason(self):
        """Test InvalidMoveError with reason."""
        error = InvalidMoveError(5, 10, "Point blocked")
        self.assertEqual(error.from_point, 5)
        self.assertEqual(error.to_point, 10)
        self.assertEqual(error.reason, "Point blocked")
        self.assertEqual(str(error), "Invalid move from 5 to 10: Point blocked")

    def test_board_error(self):
        """Test BoardError exception."""
        error = BoardError("Board error")
        self.assertEqual(str(error), "Board error")
        self.assertIsInstance(error, BackgammonError)

    def test_invalid_point_error_default_message(self):
        """Test InvalidPointError with default message."""
        error = InvalidPointError(25)
        self.assertEqual(error.point, 25)
        self.assertEqual(str(error), "Invalid point: 25. Points must be between 0-23.")
        self.assertIsInstance(error, BoardError)

    def test_invalid_point_error_custom_message(self):
        """Test InvalidPointError with custom message."""
        error = InvalidPointError(25, "Custom error message")
        self.assertEqual(error.point, 25)
        self.assertEqual(str(error), "Custom error message")

    def test_player_error(self):
        """Test PlayerError exception."""
        error = PlayerError("Player error")
        self.assertEqual(str(error), "Player error")
        self.assertIsInstance(error, BackgammonError)

    def test_invalid_player_color_error(self):
        """Test InvalidPlayerColorError exception."""
        error = InvalidPlayerColorError("Invalid color")
        self.assertEqual(str(error), "Invalid color")
        self.assertIsInstance(error, PlayerError)

    def test_checker_error(self):
        """Test CheckerError exception."""
        error = CheckerError("Checker error")
        self.assertEqual(str(error), "Checker error")
        self.assertIsInstance(error, BackgammonError)

    def test_invalid_checker_position_error(self):
        """Test InvalidCheckerPositionError exception."""
        error = InvalidCheckerPositionError(25)
        self.assertEqual(error.position, 25)
        self.assertEqual(error.valid_range, "0-23")
        self.assertEqual(str(error), "Position must be between 0-23, got 25")
        self.assertIsInstance(error, CheckerError)

    def test_invalid_checker_position_error_custom_range(self):
        """Test InvalidCheckerPositionError with custom range."""
        error = InvalidCheckerPositionError(10, "1-6")
        self.assertEqual(error.position, 10)
        self.assertEqual(error.valid_range, "1-6")
        self.assertEqual(str(error), "Position must be between 1-6, got 10")

    def test_dice_error(self):
        """Test DiceError exception."""
        error = DiceError("Dice error")
        self.assertEqual(str(error), "Dice error")
        self.assertIsInstance(error, BackgammonError)

    def test_no_moves_remaining_error(self):
        """Test NoMovesRemainingError exception."""
        error = NoMovesRemainingError("Alice")
        self.assertEqual(error.player_name, "Alice")
        self.assertEqual(str(error), "Player Alice has no remaining moves")
        self.assertIsInstance(error, PlayerError)

    def test_invalid_checker_count_error(self):
        """Test InvalidCheckerCountError exception."""
        error = InvalidCheckerCountError(15, 12)
        self.assertEqual(error.expected, 15)
        self.assertEqual(error.actual, 12)
        self.assertEqual(str(error), "Expected 15 checkers, but got 12")
        self.assertIsInstance(error, PlayerError)

    def test_dice_not_rolled_error(self):
        """Test DiceNotRolledError exception."""
        error = DiceNotRolledError()
        self.assertIsInstance(error, DiceError)

    def test_invalid_dice_value_error(self):
        """Test InvalidDiceValueError exception."""
        error = InvalidDiceValueError(7)
        self.assertEqual(error.value, 7)
        self.assertEqual(str(error), "Invalid dice value: 7. Must be between 1-6.")
        self.assertIsInstance(error, DiceError)

    def test_invalid_checker_state_error_without_expected(self):
        """Test InvalidCheckerStateError without expected state."""
        error = InvalidCheckerStateError("INVALID")
        self.assertEqual(error.current_state, "INVALID")
        self.assertIsNone(error.expected_state)
        self.assertEqual(str(error), "Invalid checker state: INVALID")
        self.assertIsInstance(error, CheckerError)

    def test_invalid_checker_state_error_with_expected(self):
        """Test InvalidCheckerStateError with expected state."""
        error = InvalidCheckerStateError("INVALID", "ON_BOARD")
        self.assertEqual(error.current_state, "INVALID")
        self.assertEqual(error.expected_state, "ON_BOARD")
        self.assertEqual(
            str(error), "Invalid checker state: INVALID. Expected: ON_BOARD"
        )

    def test_checker_position_error(self):
        """Test CheckerPositionError exception."""
        error = CheckerPositionError(25, "ON_BOARD")
        self.assertEqual(error.position, 25)
        self.assertEqual(error.state, "ON_BOARD")
        self.assertEqual(
            str(error), "Invalid position 25 for checker in state ON_BOARD"
        )
        self.assertIsInstance(error, CheckerError)

    def test_game_quit_exception(self):
        """Test GameQuitException exception."""
        error = GameQuitException("User quit")
        self.assertEqual(str(error), "User quit")
        self.assertIsInstance(error, Exception)


if __name__ == "__main__":
    unittest.main()
