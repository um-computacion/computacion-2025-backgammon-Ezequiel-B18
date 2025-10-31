"""Tests for the Board class."""

import unittest
from core.board import Board
from core.exceptions import InvalidPointError


class TestBoard(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for the Board class."""

    def setUp(self):
        self.board = Board()

    def test_board_initialization(self):
        """Test that a new Board object is initialized with correct starting positions"""
        self.assertIsNotNone(self.board)

        # Check that the board has 24 points numbered from 0 to 23
        self.assertEqual(len(self.board.points), 24)

        # Check the starting position for white checkers (player 1)
        # White bears off to 1-6, so starts from far end
        self.assertEqual(self.board.points[23], (1, 2))  # 2 white checkers on point 23
        self.assertEqual(self.board.points[12], (1, 5))  # 5 white checkers on point 12
        self.assertEqual(self.board.points[7], (1, 3))  # 3 white checkers on point 7
        self.assertEqual(self.board.points[5], (1, 5))  # 5 white checkers on point 5

        # Check the starting position for black checkers (player 2)
        # Black bears off to 19-24, so starts from far end
        self.assertEqual(self.board.points[0], (2, 2))  # 2 black checkers on point 0
        self.assertEqual(self.board.points[11], (2, 5))  # 5 black checkers on point 11
        self.assertEqual(self.board.points[16], (2, 3))  # 3 black checkers on point 16
        self.assertEqual(self.board.points[18], (2, 5))  # 5 black checkers on point 18

        # Check that both bars start empty
        self.assertEqual(self.board.bar[1], 0)  # No white checkers on the bar
        self.assertEqual(self.board.bar[2], 0)  # No black checkers on the bar

        # Check that both homes start empty
        self.assertEqual(self.board.home[1], 0)  # No white checkers in home
        self.assertEqual(self.board.home[2], 0)  # No black checkers in home

    def test_move_checker(self):
        """Test moving a checker from one point to another"""
        # Move a white checker from point 23 to point 20 (white starts at 23 with 2 checkers)
        self.assertTrue(self.board.move_checker(1, 23, 20))
        self.assertEqual(
            self.board.points[23], (1, 1)
        )  # One white checker left on point 23
        self.assertEqual(
            self.board.points[20], (1, 1)
        )  # One white checker now on point 20

        # Move a black checker from point 0 to point 3 (black starts at 0 with 2 checkers)
        self.assertTrue(self.board.move_checker(2, 0, 3))
        self.assertEqual(
            self.board.points[0], (2, 1)
        )  # One black checker left on point 0
        self.assertEqual(
            self.board.points[3], (2, 1)
        )  # One black checker now on point 3

    def test_checkers_on_bar(self):
        """Test that checkers on the bar must be moved first"""
        # Put a white checker on the bar
        self.board.bar[1] = 1

        # Try to move a regular checker (should fail because bar must be emptied first)
        self.assertFalse(self.board.is_valid_move(1, 20, 18))

        # Move the checker from the bar (for white, entering from point 18-23)
        self.assertTrue(self.board.enter_from_bar(1, 20))
        self.assertEqual(self.board.bar[1], 0)  # Bar now empty
        self.assertEqual(self.board.points[20], (1, 1))  # Checker entered at point 20

    def test_bearing_off(self):
        """Test bearing off checkers (moving them to home)"""
        # Setup: Move all white checkers to the home board
        self.board = Board(
            test_bearing_off=True
        )  # Special test setup with all checkers in home board

        # Count white checkers in the home board (0-5 for white)
        white_checkers_in_home_board = sum(
            count
            for player, count in [self.board.points[i] for i in range(0, 6)]
            if player == 1
        )
        self.assertEqual(
            white_checkers_in_home_board, 15
        )  # All 15 white checkers in home board

        # Bear off a checker from point 5 (highest in white's home board)
        self.assertTrue(self.board.bear_off(1, 5))
        self.assertEqual(
            self.board.points[5], (1, 2)
        )  # One checker removed (was 3, now 2)
        self.assertEqual(self.board.home[1], 1)  # One checker in home

        # Bear off remaining checkers from point 5
        self.assertTrue(self.board.bear_off(1, 5))
        self.assertTrue(self.board.bear_off(1, 5))
        self.assertEqual(self.board.points[5], (0, 0))  # No more checkers
        self.assertEqual(self.board.home[1], 3)  # Three checkers in home

    def test_check_winner(self):
        """Test checking for a winner"""
        # No winner at the start
        self.assertEqual(self.board.check_winner(), 0)

        # Create a fresh board for this test
        test_board = Board()

        # Put all white checkers in home
        test_board.home[1] = 15
        self.assertEqual(test_board.check_winner(), 1)

        # Reset and put all black checkers in home
        test_board.home[1] = 0
        test_board.home[2] = 15
        self.assertEqual(test_board.check_winner(), 2)

        # Both players with all checkers borne off (impossible scenario)
        test_board.home[1] = 15
        test_board.home[2] = 15
        # In this case, we still return the first winner found (white)
        self.assertEqual(test_board.check_winner(), 1)

    def test_get_player_at_point(self):
        """Test getting the player owning checkers at a point"""
        self.assertEqual(self.board.get_player_at_point(0), 2)  # Black at point 0
        self.assertEqual(self.board.get_player_at_point(5), 1)  # White at point 5
        self.assertEqual(self.board.get_player_at_point(1), 0)  # No checkers at point 1

    def test_get_player_at_point_invalid_point_raises_error(self):
        """Test that get_player_at_point raises InvalidPointError for invalid points."""
        board = Board()

        with self.assertRaises(InvalidPointError) as context:
            board.get_player_at_point(-1)

        self.assertEqual(context.exception.point, -1)
        self.assertIn("Invalid point: -1", str(context.exception))

        with self.assertRaises(InvalidPointError):
            board.get_player_at_point(24)

    def test_get_checkers_count(self):
        """Test getting the number of checkers at a point"""
        self.assertEqual(self.board.get_checkers_count(0), 2)  # 2 checkers at point 0
        self.assertEqual(self.board.get_checkers_count(11), 5)  # 5 checkers at point 11
        self.assertEqual(self.board.get_checkers_count(1), 0)  # No checkers at point 1

    def test_get_checkers_count_invalid_point_raises_error(self):
        """Test that get_checkers_count raises InvalidPointError for invalid points."""
        board = Board()

        with self.assertRaises(InvalidPointError) as context:
            board.get_checkers_count(25)

        self.assertEqual(context.exception.point, 25)

        with self.assertRaises(InvalidPointError):
            board.get_checkers_count(-5)

    def test_all_checkers_in_home_board(self):
        """Test checking if all player's checkers are in their home board"""
        # At the start, not all checkers are in home board
        self.assertFalse(self.board.all_checkers_in_home_board(1))
        self.assertFalse(self.board.all_checkers_in_home_board(2))

        # Setup a test case with all white checkers in home board
        test_board = Board(test_bearing_off=True)
        self.assertTrue(test_board.all_checkers_in_home_board(1))
        # Black checkers are also in their home board in this test setup
        self.assertTrue(test_board.all_checkers_in_home_board(2))

    def test_is_valid_move_blocked_by_bar(self):
        """Test that moves are blocked when player has checkers on bar."""
        b = Board()
        b.bar[1] = 1
        # Even if source has checkers, bar presence blocks normal moves
        self.assertFalse(b.is_valid_move(1, 0, 3))

    def test_is_valid_move_source_missing_or_target_blocked(self):
        """Test validation for missing source or blocked target."""
        b = Board()
        # source empty (point 1 is empty at start)
        self.assertFalse(b.is_valid_move(1, 1, 3))
        # target blocked by opponent (make point 3 occupied by 2 black checkers)
        b.points[3] = (2, 2)
        # ensure source has a white checker to attempt move
        b.points[0] = (1, 2)
        self.assertFalse(b.is_valid_move(1, 0, 3))

    def test_move_checker_hits_opponent(self):
        """Test that move_checker properly handles hitting opponent."""
        b = Board()
        # prepare: white at 10 (1 checker), black single at 7
        # white moves from high to low, so 10 -> 7 is valid
        b.points[10] = (1, 1)
        b.points[7] = (2, 1)  # black single checker
        prev_bar_black = b.bar[2]
        event = b.move_checker(1, 10, 7)
        self.assertTrue(event.get("moved", False))
        self.assertTrue(event.get("hit", False))
        self.assertEqual(b.bar[2], prev_bar_black + 1)
        self.assertEqual(b.points[7][0], 1)

    def test_enter_from_bar_invalid_and_hit(self):
        """Test enter_from_bar validation and hitting behavior."""
        b = Board()
        # no checker on bar -> can't enter
        self.assertFalse(b.enter_from_bar(1, 20))
        # simulate a white checker on the bar and a single black on point 20
        b.bar[1] = 1
        b.points[20] = (2, 1)
        result = b.enter_from_bar(1, 20)
        self.assertTrue(result)
        # black should have been hit and moved to bar
        self.assertEqual(b.bar[2], 1)

    def test_enter_from_bar_invalid_entry_point(self):
        """Test that enter_from_bar validates entry points."""
        b = Board()
        b.bar[1] = 1
        # white cannot enter at point 10
        self.assertFalse(b.enter_from_bar(1, 10))

    def test_bear_off_requires_all_in_home_and_correct_point(self):
        """Test bear_off preconditions and validation."""
        b = Board()
        # not all in home -> cannot bear off
        self.assertFalse(
            b.bear_off(1, 0)
        )  # white home board point, but not all checkers in home
        # use test_bearing_off setup to populate home board
        b = Board(test_bearing_off=True)
        # attempt to bear off from an out-of-range point for white
        # (e.g., 18 which is in black's home)
        self.assertFalse(b.bear_off(1, 18))

    def test_is_valid_move_true(self):
        """Valid move should return True when no bar and target not blocked"""
        b = Board()
        # ensure source has white checkers and target is empty
        # white moves from high to low, so test 5 -> 2
        b.points[5] = (1, 2)  # white at point 5
        b.points[2] = (0, 0)  # empty target
        self.assertTrue(b.is_valid_move(1, 5, 2))

    def test_move_checker_stacks_on_same_player_point(self):
        """Moving to a point already occupied by same player should increase count"""
        b = Board()
        # white has 2 at point 23 and 5 at point 12 initially
        # move a white checker from 23 to 12 -> point 12 should increase
        prev_count = b.points[12][1]
        event = b.move_checker(1, 23, 12)
        self.assertTrue(event.get("moved", False))
        self.assertEqual(b.points[12][1], prev_count + 1)

    def test_enter_from_bar_blocked_by_opponent_stack(self):
        """Entering from bar should fail when opponent has 2+ checkers at entry point"""
        b = Board()
        # place two black checkers at white's entry point 3 and put a white on bar
        b.points[3] = (2, 2)
        b.bar[1] = 1
        self.assertFalse(b.enter_from_bar(1, 3))

    def test_bear_off_for_black_counts_and_home_increment(self):
        """Test black bearing off from its home board updates points and home correctly"""
        b = Board(test_bearing_off=True)
        # black home is points 18-23 in corrected setup; pick point 18 which has 2 black there
        prev_home_black = b.home[2]
        prev_count = b.points[18][1]
        # bear off one black from point 18
        result = b.bear_off(2, 18)
        self.assertTrue(result)
        # count on point reduced
        expected_count = prev_count - 1
        # If prev_count was 1 then point becomes empty (0,0), else player remains
        if expected_count == 0:
            self.assertEqual(b.points[18], (0, 0))
        else:
            self.assertEqual(b.points[18], (2, expected_count))
        self.assertEqual(b.home[2], prev_home_black + 1)

    def test_is_valid_move_invalid_points_raise_error(self):
        """Test that is_valid_move raises InvalidPointError for invalid point indices."""
        board = Board()

        with self.assertRaises(InvalidPointError):
            board.is_valid_move(1, -1, 5)

        with self.assertRaises(InvalidPointError):
            board.is_valid_move(1, 0, 24)

    def test_move_checker_invalid_points_raise_error(self):
        """Test that move_checker handles invalid points properly."""
        # This should raise InvalidPointError which gets re-raised
        with self.assertRaises(InvalidPointError):
            self.board.move_checker(1, 25, 20)

    def test_backwards_move_validation(self):
        """Test that backwards moves are properly rejected."""
        # White moves from higher numbers to lower numbers
        self.assertFalse(self.board.is_valid_move(1, 10, 15))  # White moving backwards

        # Black moves from lower numbers to higher numbers
        self.assertFalse(self.board.is_valid_move(2, 15, 10))  # Black moving backwards

    def test_blocked_point_validation(self):
        """Test that moves to blocked points are rejected."""
        # Set up a point blocked by opponent (2+ checkers)
        self.board.points[10] = (2, 3)  # Black has 3 checkers on point 10

        # White player (1) should not be able to move to blocked point
        # But we need a source point with white checkers first
        self.board.points[15] = (1, 1)  # White has 1 checker on point 15

        self.assertFalse(self.board.is_valid_move(1, 15, 10))

        # Should be able to move to point with only 1 opponent checker
        self.board.points[11] = (2, 1)  # Black has 1 checker on point 11
        self.assertTrue(self.board.is_valid_move(1, 15, 11))

    def test_setup_starting_positions_clears_board(self):
        """Test that setup_starting_positions clears the board first."""
        # Modify a point first
        self.board.points[10] = (1, 5)

        # Setup starting positions
        self.board.setup_starting_positions()

        # Verify standard positions are set and random point is cleared
        self.assertEqual(self.board.points[10], (0, 0))
        self.assertEqual(self.board.points[5], (1, 5))  # White starting position


if __name__ == "__main__":
    unittest.main()
