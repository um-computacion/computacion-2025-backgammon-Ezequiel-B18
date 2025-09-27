"""Tests for the Game class."""
import unittest
from unittest.mock import patch
from core.game import Game
from core.player import PlayerColor
from core.checker import CheckerState
from core.exceptions import (
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
)


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""

    def test_game_initialization(self):
        """Test that a new Game object is initialized correctly."""
        game = Game("Alice", "Bob")
        self.assertEqual(game.player1.name, "Alice")
        self.assertEqual(game.player2.name, "Bob")
        self.assertEqual(game.player1.color, PlayerColor.WHITE)
        self.assertEqual(game.player2.color, PlayerColor.BLACK)
        self.assertIsNotNone(game.board)
        self.assertIsNotNone(game.dice)

    def test_setup_distribute_checkers(self):
        """Test that setup_game properly distributes checkers."""
        game = Game("P1", "P2")
        game.setup_game()
        # Check that board has expected starting occupancy for some known points
        # White starts at 0,11,16,18
        self.assertEqual(game.board.points[0][0], 1)
        self.assertEqual(game.board.points[11][0], 1)
        self.assertEqual(game.board.points[16][0], 1)
        self.assertEqual(game.board.points[18][0], 1)
        # Black starts at 23,12,7,5
        self.assertEqual(game.board.points[23][0], 2)
        self.assertEqual(game.board.points[12][0], 2)
        self.assertEqual(game.board.points[7][0], 2)
        self.assertEqual(game.board.points[5][0], 2)

    def test_initial_roll_chooses_player(self):
        """Test that initial roll correctly chooses the starting player."""
        game = Game()

        # Patch dice.initial_roll to set initial_values and return non-tie
        def fake_initial_roll():
            game.dice.initial_values = [5, 2]
            return (5, 2)

        with patch.object(game.dice, "initial_roll", side_effect=fake_initial_roll):
            winner = game.initial_roll_until_decided()
            self.assertIn(winner, (1, 2))
            # Because fake_initial_roll sets 5>2, winner should be 1
            self.assertEqual(winner, 1)
            self.assertIs(game.current_player, game.player1)

    def test_start_turn_sets_moves(self):
        """Test that start_turn properly sets remaining moves."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        # Mock dice.roll and get_moves
        with patch.object(game.dice, "roll", return_value=(3, 4)):
            with patch.object(game.dice, "get_moves", return_value=[3, 4]):
                game.start_turn()
                self.assertTrue(game.player1.is_turn)
                self.assertEqual(game.player1.remaining_moves, 2)

    def test_initial_roll_repeats_on_tie_then_decides(self):
        """Test that initial roll repeats on tie then decides winner."""
        game = Game()

        calls = [[3, 3], [4, 2]]  # first tie, then player1 wins

        def fake_initial_roll():
            vals = calls.pop(0)
            game.dice.initial_values = vals
            return tuple(vals)

        with patch.object(game.dice, "initial_roll", side_effect=fake_initial_roll):
            winner = game.initial_roll_until_decided()
            self.assertEqual(winner, 1)
            self.assertIs(game.current_player, game.player1)

    def test_start_turn_without_current_player_raises(self):
        """Test that start_turn raises GameNotInitializedError when no current player."""
        game = Game()
        game.setup_game()
        with self.assertRaises(GameNotInitializedError):
            game.start_turn()

    def test_apply_move_without_current_player_returns_false(self):
        """Test that apply_move raises InvalidPlayerTurnError when no current player."""
        game = Game()
        game.setup_game()
        with self.assertRaises(InvalidPlayerTurnError):
            game.apply_move(0, 3)

    def test_apply_move_event_not_moved_returns_false(self):
        """Test that apply_move returns False when move is invalid."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.remaining_moves = 1
        self.assertFalse(game.apply_move(1, 3))

    def test_apply_move_hit_and_sync_updates_checkers(self):
        """Test that apply_move handles hits and syncs checker states."""
        game = Game()
        game.setup_game()
        game.board.points[0] = (1, 1)
        game.board.points[3] = (2, 1)
        game.sync_checkers()
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.remaining_moves = 1
        moved = game.apply_move(0, 3)
        self.assertTrue(moved)
        self.assertEqual(game.board.bar[2], 1)
        black_on_bar = len(game.player2.get_checkers_by_state(CheckerState.ON_BAR))
        self.assertEqual(black_on_bar, 1)

    def test_sync_checkers_reflects_bar_and_home(self):
        """sync_checkers should map board.bar and board.home to Player.checkers states"""
        game = Game()
        # manipulate board: give white 2 borne off and put 1 black on bar
        game.board.setup_starting_positions()
        game.board.home[1] = 2
        game.board.bar[2] = 1
        # ensure some on-board distribution exists for both players
        game.player1.distribute_checkers(game.board)
        game.player2.distribute_checkers(game.board)
        # reconcile
        game.sync_checkers()
        # white borne off count
        self.assertEqual(len(game.player1.get_checkers_by_state(CheckerState.BORNE_OFF)), 2)
        # black on bar count
        self.assertEqual(len(game.player2.get_checkers_by_state(CheckerState.ON_BAR)), 1)

    def test_get_winner_and_is_game_over(self):
        """is_game_over and get_winner should reflect board.check_winner result"""
        game = Game()
        # no winner
        self.assertFalse(game.is_game_over())
        self.assertIsNone(game.get_winner())
        # set a winner on board
        game.board.home[1] = 15
        self.assertTrue(game.is_game_over())
        self.assertIs(game.get_winner(), game.player1)

    def test_start_turn_without_initialization_raises_error(self):
        """Test that start_turn raises GameNotInitializedError when game not initialized."""
        game = Game()
        game.current_player = game.player1  # Set player but don't initialize game
        
        with self.assertRaises(GameNotInitializedError) as context:
            game.start_turn()
        
        self.assertIn("initialized before starting turns", str(context.exception))

    def test_start_turn_when_game_over_raises_error(self):
        """Test that start_turn raises GameAlreadyOverError when game is over."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        
        # Force game over condition
        game.board.home[1] = 15
        
        with self.assertRaises(GameAlreadyOverError) as context:
            game.start_turn()
        
        self.assertIn("game is over", str(context.exception))

    def test_apply_move_without_initialization_raises_error(self):
        """Test that apply_move raises GameNotInitializedError when game not initialized."""
        game = Game()
        game.current_player = game.player1
        
        with self.assertRaises(GameNotInitializedError) as context:
            game.apply_move(0, 3)
        
        self.assertIn("initialized before making moves", str(context.exception))

    def test_apply_move_without_current_player_raises_error(self):
        """Test that apply_move raises InvalidPlayerTurnError when no current player."""
        game = Game()
        game.setup_game()
        # Don't set current_player
        
        with self.assertRaises(InvalidPlayerTurnError) as context:
            game.apply_move(0, 3)
        
        self.assertIn("No current player set", str(context.exception))

    def test_apply_move_when_game_over_raises_error(self):
        """Test that apply_move raises GameAlreadyOverError when game is over."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        
        # Force game over condition
        game.board.home[1] = 15
        
        with self.assertRaises(GameAlreadyOverError) as context:
            game.apply_move(0, 3)
        
        self.assertIn("game is over", str(context.exception))

    def test_apply_move_without_remaining_moves_raises_error(self):
        """Test that apply_move raises InvalidPlayerTurnError when no moves remaining."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.remaining_moves = 0
        
        with self.assertRaises(InvalidPlayerTurnError) as context:
            game.apply_move(0, 3)
        
        self.assertIn("has no remaining moves", str(context.exception))

    def test_switch_players_without_initialization_raises_error(self):
        """Test that switch_players raises GameNotInitializedError when game not initialized."""
        game = Game()
        game.current_player = game.player1
        game.other_player = game.player2
        
        with self.assertRaises(GameNotInitializedError) as context:
            game.switch_players()
        
        self.assertIn("initialized before switching players", str(context.exception))


if __name__ == "__main__":
    unittest.main()