"""Tests for the Player class."""

import unittest
from unittest.mock import Mock
from core.player import Player, PlayerColor
from core.checker import CheckerColor, CheckerState
from core.exceptions import NoMovesRemainingError


class TestPlayer(unittest.TestCase):
    """Test cases for the Player class."""

    def setUp(self):
        self.white_player = Player("Player 1", PlayerColor.WHITE)
        self.black_player = Player("Player 2", PlayerColor.BLACK)

    def test_player_initialization(self):
        """Test that a new Player object is initialized correctly"""
        self.assertEqual(self.white_player.name, "Player 1")
        self.assertEqual(self.white_player.color, PlayerColor.WHITE)
        self.assertEqual(self.white_player.player_id, 1)
        self.assertEqual(self.black_player.name, "Player 2")
        self.assertEqual(self.black_player.color, PlayerColor.BLACK)
        self.assertEqual(self.black_player.player_id, 2)

        # Check turn and remaining moves
        self.assertFalse(self.white_player.is_turn)
        self.assertFalse(self.black_player.is_turn)
        self.assertEqual(self.white_player.remaining_moves, 0)
        self.assertEqual(self.black_player.remaining_moves, 0)

        # Check checker collections
        self.assertEqual(len(self.white_player.checkers), 15)
        for checker in self.white_player.checkers:
            self.assertEqual(checker.color, CheckerColor.WHITE)

        self.assertEqual(len(self.black_player.checkers), 15)
        for checker in self.black_player.checkers:
            self.assertEqual(checker.color, CheckerColor.BLACK)

    def test_get_starting_positions(self):
        """Test getting the standard starting positions for checkers"""
        # White player's starting positions
        white_positions = self.white_player.get_starting_positions()
        self.assertEqual(white_positions, [(0, 2), (11, 5), (16, 3), (18, 5)])

        # Black player's starting positions
        black_positions = self.black_player.get_starting_positions()
        self.assertEqual(black_positions, [(23, 2), (12, 5), (7, 3), (5, 5)])

    def test_start_turn(self):
        """Test starting a player's turn"""
        # Mock dice values [3, 5]
        mock_dice = Mock()
        mock_dice.get_moves.return_value = [3, 5]

        # Start turn
        self.white_player.start_turn(mock_dice)

        self.assertTrue(self.white_player.is_turn)
        self.assertEqual(self.white_player.remaining_moves, 2)  # Two dice values

    def test_start_turn_with_doubles(self):
        """Test starting a turn with doubles"""
        # Mock dice with doubles [4, 4] -> [4, 4, 4, 4]
        mock_dice = Mock()
        mock_dice.get_moves.return_value = [4, 4, 4, 4]
        mock_dice.is_doubles.return_value = True

        # Start turn
        self.white_player.start_turn(mock_dice)

        self.assertTrue(self.white_player.is_turn)
        self.assertEqual(self.white_player.remaining_moves, 4)  # Four moves for doubles

    def test_end_turn(self):
        """Test ending a player's turn"""
        # Setup: player is in turn with remaining moves
        self.white_player.is_turn = True
        self.white_player.remaining_moves = 2

        # End turn
        self.white_player.end_turn()

        self.assertFalse(self.white_player.is_turn)
        self.assertEqual(self.white_player.remaining_moves, 0)

    def test_use_move(self):
        """Test using a move during a turn"""
        # Setup: player is in turn with 2 remaining moves
        self.white_player.is_turn = True
        self.white_player.remaining_moves = 2

        # Use one move
        self.white_player.use_move()

        self.assertEqual(self.white_player.remaining_moves, 1)
        self.assertTrue(self.white_player.is_turn)  # Still in turn

        # Use second move
        self.white_player.use_move()

        self.assertEqual(self.white_player.remaining_moves, 0)
        self.assertTrue(
            self.white_player.is_turn
        )  # Still in turn until explicitly ended

    def test_use_move_with_no_remaining_raises_error(self):
        """Test that use_move raises NoMovesRemainingError when no moves remaining"""
        # Setup: player with no remaining moves
        self.white_player.remaining_moves = 0

        with self.assertRaises(NoMovesRemainingError) as context:
            self.white_player.use_move()

        self.assertEqual(context.exception.player_name, "Player 1")
        self.assertIn("Player Player 1 has no remaining moves", str(context.exception))

    def test_get_checkers_by_state(self):
        """Test getting checkers by their state"""
        # Initially all checkers are on board (but with no position)
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.ON_BOARD)), 15
        )
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.ON_BAR)), 0
        )
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.BORNE_OFF)), 0
        )

        # Change state of some checkers
        self.white_player.checkers[0].send_to_bar()
        self.white_player.checkers[1].send_to_bar()
        self.white_player.checkers[2].set_position(20)  # In white home board
        self.white_player.checkers[2].bear_off()

        # Check counts again
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.ON_BOARD)), 12
        )
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.ON_BAR)), 2
        )
        self.assertEqual(
            len(self.white_player.get_checkers_by_state(CheckerState.BORNE_OFF)), 1
        )

    def test_count_checkers_by_state(self):
        """Test counting checkers by their state"""
        # Initially all checkers are on board
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.ON_BOARD), 15
        )
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.ON_BAR), 0
        )
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.BORNE_OFF), 0
        )

        # Change state of some checkers
        self.white_player.checkers[0].send_to_bar()
        self.white_player.checkers[1].set_position(20)  # In white home board
        self.white_player.checkers[1].bear_off()

        # Check counts again
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.ON_BOARD), 13
        )
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.ON_BAR), 1
        )
        self.assertEqual(
            self.white_player.count_checkers_by_state(CheckerState.BORNE_OFF), 1
        )

    def test_has_checkers_on_bar(self):
        """Test checking if a player has checkers on the bar"""
        # Initially no checkers on bar
        self.assertFalse(self.white_player.has_checkers_on_bar())

        # Send a checker to bar
        self.white_player.checkers[0].send_to_bar()

        # Now should have checkers on bar
        self.assertTrue(self.white_player.has_checkers_on_bar())

    def test_has_won(self):
        """Test checking if a player has won (all checkers borne off)"""
        # Initially has not won
        self.assertFalse(self.white_player.has_won())

        # Bear off all checkers
        for checker in self.white_player.checkers:
            checker.set_position(20)  # Position in home board
            checker.bear_off()

        # Now should have won
        self.assertTrue(self.white_player.has_won())

    def test_distribute_checkers(self):
        """Test distributing checkers to their starting positions"""
        # Create a mock board
        mock_board = Mock()
        mock_board.points = [(0, 0) for _ in range(24)]

        # Distribute checkers
        self.white_player.distribute_checkers(mock_board)

        # Check checkers were positioned
        positions_count = {}
        for checker in self.white_player.checkers:
            if checker.position is not None:
                pos = checker.position
                positions_count[pos] = positions_count.get(pos, 0) + 1

        # Check counts match starting positions
        self.assertEqual(positions_count.get(0, 0), 2)
        self.assertEqual(positions_count.get(11, 0), 5)
        self.assertEqual(positions_count.get(16, 0), 3)
        self.assertEqual(positions_count.get(18, 0), 5)

    def test_player_str_representation(self):
        """Test the string representation of a player"""
        self.assertEqual(
            str(self.white_player),
            "Player 1 (WHITE): 15 on board, 0 on bar, 0 borne off, not in turn",
        )

        # Change some checker states
        self.white_player.checkers[0].send_to_bar()
        self.white_player.checkers[1].set_position(20)  # In white home board
        self.white_player.checkers[1].bear_off()
        self.white_player.is_turn = True
        self.white_player.remaining_moves = 3

        self.assertEqual(
            str(self.white_player),
            "Player 1 (WHITE): 13 on board, 1 on bar, 1 borne off, in turn (3 moves)",
        )
