"""Tests for the Checker class."""

import unittest
from core.checker import Checker, CheckerColor, CheckerState
from core.exceptions import InvalidCheckerPositionError


class TestChecker(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for the Checker class."""

    def setUp(self):
        self.white_checker = Checker(CheckerColor.WHITE)
        self.black_checker = Checker(CheckerColor.BLACK)

    def test_checker_initialization(self):
        """Test that checker initializes with correct values"""
        self.assertEqual(self.white_checker.color, CheckerColor.WHITE)
        self.assertEqual(self.black_checker.color, CheckerColor.BLACK)

        # Initial state should be on board
        self.assertEqual(self.white_checker.state, CheckerState.ON_BOARD)
        self.assertEqual(self.black_checker.state, CheckerState.ON_BOARD)

        # Initial position should be None until placed on the board
        self.assertIsNone(self.white_checker.position)
        self.assertIsNone(self.black_checker.position)

    def test_set_position(self):
        """Test setting a checker's position on the board"""
        self.white_checker.set_position(0)  # Set to point 0
        self.assertEqual(self.white_checker.position, 0)

        self.black_checker.set_position(23)  # Set to point 23
        self.assertEqual(self.black_checker.position, 23)

    def test_move_to_position(self):
        """Test moving a checker to a new position"""
        # Initial position
        self.white_checker.set_position(0)

        # Move to new position
        self.white_checker.move_to_position(5)
        self.assertEqual(self.white_checker.position, 5)
        self.assertEqual(self.white_checker.state, CheckerState.ON_BOARD)

        # Move again
        self.white_checker.move_to_position(7)
        self.assertEqual(self.white_checker.position, 7)

    def test_move_by_value(self):
        """Test moving a checker by a dice value"""
        # Setup: white checker at position 5
        self.white_checker.set_position(5)

        # Move by dice value 6
        new_position = self.white_checker.calculate_new_position(6)
        self.assertEqual(new_position, 11)  # 5 + 6 = 11

        # Actually move
        self.white_checker.move_to_position(new_position)
        self.assertEqual(self.white_checker.position, 11)

        # Test with black (moves in opposite direction)
        self.black_checker.set_position(18)

        # Move by dice value 4
        new_position = self.black_checker.calculate_new_position(4)
        self.assertEqual(new_position, 14)  # 18 - 4 = 14

        # Actually move
        self.black_checker.move_to_position(new_position)
        self.assertEqual(self.black_checker.position, 14)

    def test_send_to_bar(self):
        """Test sending a checker to the bar"""
        # Setup checker on board
        self.white_checker.set_position(10)

        # Send to bar
        self.white_checker.send_to_bar()
        self.assertEqual(self.white_checker.state, CheckerState.ON_BAR)
        self.assertIsNone(self.white_checker.position)

    def test_enter_from_bar(self):
        """Test entering a checker from the bar"""
        # Setup checker on bar
        self.white_checker.send_to_bar()

        # Enter from bar to position 3 (valid for white)
        self.white_checker.enter_from_bar(3)
        self.assertEqual(self.white_checker.state, CheckerState.ON_BOARD)
        self.assertEqual(self.white_checker.position, 3)

        # Same for black
        self.black_checker.send_to_bar()

        # Enter from bar to position 20 (valid for black)
        self.black_checker.enter_from_bar(20)
        self.assertEqual(self.black_checker.state, CheckerState.ON_BOARD)
        self.assertEqual(self.black_checker.position, 20)

    def test_invalid_enter_from_bar(self):
        """Test that entering from bar follows correct rules"""
        # Setup checker on bar
        self.white_checker.send_to_bar()

        # Try to enter at invalid position (valid white entry points are 0-5)
        with self.assertRaises(InvalidCheckerPositionError):
            self.white_checker.enter_from_bar(6)

        # Ensure state hasn't changed
        self.assertEqual(self.white_checker.state, CheckerState.ON_BAR)
        self.assertIsNone(self.white_checker.position)

        # Same for black (valid black entry points are 18-23)
        self.black_checker.send_to_bar()

        with self.assertRaises(InvalidCheckerPositionError):
            self.black_checker.enter_from_bar(17)

        self.assertEqual(self.black_checker.state, CheckerState.ON_BAR)
        self.assertIsNone(self.black_checker.position)

    def test_bear_off(self):
        """Test bearing off a checker"""
        # Setup white checker in home board
        self.white_checker.set_position(20)  # Point in white home board

        # Bear off
        self.white_checker.bear_off()
        self.assertEqual(self.white_checker.state, CheckerState.BORNE_OFF)
        self.assertIsNone(self.white_checker.position)

        # Same for black
        self.black_checker.set_position(4)  # Point in black home board

        # Bear off
        self.black_checker.bear_off()
        self.assertEqual(self.black_checker.state, CheckerState.BORNE_OFF)
        self.assertIsNone(self.black_checker.position)

    def test_invalid_bear_off(self):
        """Test that bearing off from outside home board raises error"""
        # Setup white checker outside home board (home board is 18-23)
        self.white_checker.set_position(15)

        # Try to bear off
        with self.assertRaises(ValueError):
            self.white_checker.bear_off()

        # Ensure state hasn't changed
        self.assertEqual(self.white_checker.state, CheckerState.ON_BOARD)
        self.assertEqual(self.white_checker.position, 15)

        # Same for black (home board is 0-5)
        self.black_checker.set_position(10)

        with self.assertRaises(ValueError):
            self.black_checker.bear_off()

        self.assertEqual(self.black_checker.state, CheckerState.ON_BOARD)
        self.assertEqual(self.black_checker.position, 10)

    def test_is_in_home_board(self):
        """Test checking if a checker is in its home board"""
        # White home board is 18-23
        self.white_checker.set_position(20)
        self.assertTrue(self.white_checker.is_in_home_board())

        self.white_checker.set_position(10)
        self.assertFalse(self.white_checker.is_in_home_board())

        # Black home board is 0-5
        self.black_checker.set_position(3)
        self.assertTrue(self.black_checker.is_in_home_board())

        self.black_checker.set_position(15)
        self.assertFalse(self.black_checker.is_in_home_board())

    def test_can_bear_off_with_value(self):
        """Test if a checker can be borne off with a specific dice value"""
        # White checker on point 20, needs a 5 to bear off (or higher)
        self.white_checker.set_position(20)
        self.assertTrue(self.white_checker.can_bear_off_with_value(5))
        self.assertTrue(
            self.white_checker.can_bear_off_with_value(6)
        )  # Higher value is also valid
        self.assertFalse(self.white_checker.can_bear_off_with_value(3))  # Too small

        # Black checker on point 3, needs a 4 to bear off (or higher)
        self.black_checker.set_position(3)
        self.assertTrue(self.black_checker.can_bear_off_with_value(4))
        self.assertTrue(
            self.black_checker.can_bear_off_with_value(6)
        )  # Higher value is also valid
        self.assertFalse(self.black_checker.can_bear_off_with_value(2))  # Too small

        # Exact value needed when on the furthest point
        self.white_checker.set_position(23)
        self.assertTrue(self.white_checker.can_bear_off_with_value(1))

        self.black_checker.set_position(0)
        self.assertTrue(self.black_checker.can_bear_off_with_value(1))

    def test_checker_str_representation(self):
        """Test string representation of checker"""
        self.assertEqual(str(self.white_checker), "White(ON_BOARD, pos=None)")
        self.assertEqual(str(self.black_checker), "Black(ON_BOARD, pos=None)")

        self.white_checker.set_position(5)
        self.assertEqual(str(self.white_checker), "White(ON_BOARD, pos=5)")

        # Set position in home board before bearing off
        self.white_checker.set_position(20)  # Position in white home board
        self.white_checker.bear_off()
        self.assertEqual(str(self.white_checker), "White(BORNE_OFF, pos=None)")

    def test_set_position_invalid_raises(self):
        """Test that set_position raises InvalidCheckerPositionError for invalid positions."""
        c = Checker(CheckerColor.WHITE)
        with self.assertRaises(InvalidCheckerPositionError):
            c.set_position(-1)
        with self.assertRaises(InvalidCheckerPositionError):
            c.set_position(24)

    def test_move_to_position_invalid_raises(self):
        """Test that move_to_position raises InvalidCheckerPositionError for invalid positions."""
        c = Checker(CheckerColor.BLACK)
        with self.assertRaises(InvalidCheckerPositionError):
            c.move_to_position(-5)
        with self.assertRaises(InvalidCheckerPositionError):
            c.move_to_position(100)

    def test_calculate_new_position_errors_when_not_on_board(self):
        """Test that calculate_new_position raises ValueError when checker not on board."""
        c = Checker(CheckerColor.WHITE)
        c.send_to_bar()
        with self.assertRaises(ValueError):
            c.calculate_new_position(3)

    def test_calculate_new_position_errors_when_no_position(self):
        """Test that calculate_new_position raises ValueError when position is None."""
        c = Checker(CheckerColor.WHITE)
        # state ON_BOARD but no position set - use send_to_bar then force back to ON_BOARD
        c.send_to_bar()
        c.state = (
            CheckerState.ON_BOARD
        )  # Force invalid state: ON_BOARD with None position
        with self.assertRaises(ValueError):
            c.calculate_new_position(2)

    def test_set_position_invalid_raises_custom_error(self):
        """Test that set_position raises InvalidCheckerPositionError for invalid positions."""
        c = Checker(CheckerColor.WHITE)

        with self.assertRaises(InvalidCheckerPositionError) as context:
            c.set_position(-1)

        self.assertEqual(context.exception.position, -1)
        self.assertIn("Position must be between 0-23", str(context.exception))

        with self.assertRaises(InvalidCheckerPositionError):
            c.set_position(24)

    def test_move_to_position_invalid_raises_custom_error(self):
        """Test that move_to_position raises InvalidCheckerPositionError for invalid positions."""
        c = Checker(CheckerColor.BLACK)

        with self.assertRaises(InvalidCheckerPositionError) as context:
            c.move_to_position(-5)

        self.assertEqual(context.exception.position, -5)

        with self.assertRaises(InvalidCheckerPositionError):
            c.move_to_position(100)

    def test_enter_from_bar_invalid_position_raises_custom_error(self):
        """Test that entering from bar with invalid position raises InvalidCheckerPositionError."""
        # Setup checker on bar
        self.white_checker.send_to_bar()

        # Try to enter at invalid position for white (valid range is 0-5)
        with self.assertRaises(InvalidCheckerPositionError) as context:
            self.white_checker.enter_from_bar(6)

        self.assertEqual(context.exception.position, 6)
        self.assertEqual(context.exception.valid_range, "0-5")
        self.assertIn("Position must be between 0-5", str(context.exception))

        # Same for black (valid range is 18-23)
        self.black_checker.send_to_bar()

        with self.assertRaises(InvalidCheckerPositionError) as context:
            self.black_checker.enter_from_bar(17)

        self.assertEqual(context.exception.position, 17)
        self.assertEqual(context.exception.valid_range, "18-23")

    def test_enter_from_bar_invalid_state(self):
        """Test that entering from bar when not on bar fails."""
        # Checker is on board, not on bar
        self.white_checker.set_position(10)

        # Should return False when not on bar
        self.assertFalse(self.white_checker.enter_from_bar(3))

    def test_enter_from_bar_wrong_entry_points(self):
        """Test that entering from bar to wrong entry points fails."""
        # Put white checker on bar
        self.white_checker.send_to_bar()

        # White can only enter on points 0-5, should raise exception for point 10
        with self.assertRaises(InvalidCheckerPositionError):
            self.white_checker.enter_from_bar(10)

        # Put black checker on bar
        self.black_checker.send_to_bar()

        # Black can only enter on points 18-23, should raise exception for point 10
        with self.assertRaises(InvalidCheckerPositionError):
            self.black_checker.enter_from_bar(10)


if __name__ == "__main__":
    unittest.main()
