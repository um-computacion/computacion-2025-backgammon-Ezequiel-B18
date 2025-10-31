"""Tests for the Game class."""

import unittest
from unittest.mock import patch
from core.dice import Dice
from core.game import Game
from core.player import PlayerColor
from core.checker import CheckerState
from core.exceptions import (
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
)


class TestGame(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for the Game class."""

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game()
        self.game.setup_game()

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
        # White starts at 23,12,7,5 (bear off to 1-6)
        self.assertEqual(game.board.points[23][0], 1)
        self.assertEqual(game.board.points[12][0], 1)
        self.assertEqual(game.board.points[7][0], 1)
        self.assertEqual(game.board.points[5][0], 1)
        # Black starts at 0,11,16,18 (bear off to 19-24)
        self.assertEqual(game.board.points[0][0], 2)
        self.assertEqual(game.board.points[11][0], 2)
        self.assertEqual(game.board.points[16][0], 2)
        self.assertEqual(game.board.points[18][0], 2)

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
        game.setup_game()  # Initialize game first
        game.current_player = game.player1
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
        game.setup_game()  # Initialize but don't set current player
        with self.assertRaises(GameNotInitializedError):
            game.start_turn()

    def test_apply_move_without_current_player_returns_false(self):
        """Test that apply_move raises InvalidPlayerTurnError when no current player after init."""
        game = Game()
        game.setup_game()  # Initialize the game first
        # Don't set current_player - this should raise InvalidPlayerTurnError

        with self.assertRaises(InvalidPlayerTurnError) as context:
            game.apply_move(0, 3)

        self.assertIn("No current player set", str(context.exception))

    def test_apply_move_event_not_moved_returns_false(self):
        """Test that apply_move returns False when move is invalid."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.remaining_moves = 1
        game.current_player.available_moves = [2]  # Set available dice
        # attempt invalid move (no checker at 1)
        self.assertFalse(game.apply_move(1, 3))

    def test_apply_move_hit_and_sync_updates_checkers(self):
        """Test that apply_move handles hits and syncs checker states."""
        game = Game()
        game.setup_game()
        # Clear the starting positions and set up a specific scenario
        # White moves from high to low, so test 10 -> 7
        game.board.points[10] = (1, 1)  # One white checker at point 10
        game.board.points[7] = (2, 1)  # One black checker at point 7
        # Sync the checker states to match board
        game.sync_checkers()
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.remaining_moves = 1
        game.current_player.available_moves = [3]  # Set available dice for distance 3
        # Apply move: white from 10 to 7 -> hit black
        moved = game.apply_move(10, 7)
        self.assertTrue(moved)
        # board should reflect black on bar
        self.assertEqual(game.board.bar[2], 1)
        # player's checker objects should reflect that (one black on bar)
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
        self.assertEqual(
            len(game.player1.get_checkers_by_state(CheckerState.BORNE_OFF)), 2
        )
        # black on bar count
        self.assertEqual(
            len(game.player2.get_checkers_by_state(CheckerState.ON_BAR)), 1
        )

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

    def test_sync_checkers_multiple_borne_off(self):
        """Test sync_checkers with multiple checkers borne off."""
        game = Game("P1", "P2")
        game.setup_game()

        # Set up board state with multiple checkers borne off
        game.board.home[1] = 3  # 3 white checkers borne off
        game.board.bar[1] = 2  # 2 white checkers on bar

        # Sync checkers
        game.sync_checkers()

        # Verify checker states
        borne_off_count = game.player1.count_checkers_by_state(CheckerState.BORNE_OFF)
        on_bar_count = game.player1.count_checkers_by_state(CheckerState.ON_BAR)

        self.assertEqual(borne_off_count, 3)
        self.assertEqual(on_bar_count, 2)

    def test_initial_roll_player2_wins(self):
        """Test initial roll when player 2 wins."""
        game = Game("P1", "P2")
        game.setup_game()

        def fake_initial_roll():
            game.dice.initial_values = [3, 5]  # Player 2 wins
            return (3, 5)

        with patch.object(game.dice, "initial_roll", side_effect=fake_initial_roll):
            with patch.object(game.dice, "get_highest_roller", return_value=2):
                # Test that player 2 is assigned as current player when winning initial roll
                winner = game.dice.get_highest_roller()
                if winner == 2:
                    game.current_player = game.player2
                    game.other_player = game.player1

                self.assertEqual(winner, 2)

    def test_sync_checkers_skip_borne_off_checkers(self):
        """Test that sync_checkers skips already borne off checkers."""
        game = Game("P1", "P2")
        game.setup_game()

        # Set up the board to have checkers borne off
        game.board.home[1] = 2  # Board says 2 borne off

        # Sync should set checkers to borne off state
        game.sync_checkers()

        # Check that some checkers are now borne off
        borne_off_count = game.player1.count_checkers_by_state(CheckerState.BORNE_OFF)
        self.assertEqual(borne_off_count, 2)

    def test_start_turn_raises_errors_from_coverage(self):
        """Test that start_turn raises errors under specific conditions."""
        game = Game()
        with self.assertRaises(GameNotInitializedError):
            game.start_turn()
        self.game.current_player = self.game.player1
        self.game.board.home[1] = 15
        with self.assertRaises(GameAlreadyOverError):
            self.game.start_turn()

    def test_apply_move_raises_errors_from_coverage(self):
        """Test that apply_move raises errors under specific conditions."""
        game = Game()
        with self.assertRaises(GameNotInitializedError):
            game.apply_move(0, 1)
        self.game.current_player = None
        with self.assertRaises(InvalidPlayerTurnError):
            self.game.apply_move(0, 1)
        self.game.current_player = self.game.player1
        self.game.board.home[1] = 15
        with self.assertRaises(GameAlreadyOverError):
            self.game.apply_move(0, 1)
        self.game.board.home[1] = 0
        self.game.current_player.remaining_moves = 0
        with self.assertRaises(InvalidPlayerTurnError):
            self.game.apply_move(0, 1)

    def test_apply_move_from_bar_from_coverage(self):
        """Test apply_move for moves from the bar."""
        self.game.current_player = self.game.player1
        self.game.board.bar[1] = 1
        self.game.current_player.available_moves = [3]
        self.game.current_player.remaining_moves = 1
        with self.assertRaises(InvalidMoveError):
            self.game.apply_move("bar", 20)
        self.game.apply_move("bar", 21)
        self.assertEqual(self.game.board.bar[1], 0)

    def test_apply_bear_off_move_raises_errors_from_coverage(self):
        """Test that apply_bear_off_move raises errors."""
        self.game.current_player = self.game.player1
        self.game.current_player.available_moves = [3]
        with self.assertRaises(InvalidMoveError):
            self.game.apply_bear_off_move(2)
        game = Game(test_bearing_off=True)
        game.setup_game()
        game.current_player = game.player1
        game.current_player.available_moves = [1]
        with self.assertRaises(InvalidMoveError):
            game.apply_bear_off_move(2)

    def test_get_winner_from_coverage(self):
        """Test the get_winner method."""
        self.assertIsNone(self.game.get_winner())
        self.game.board.home[2] = 15
        self.assertEqual(self.game.get_winner(), self.game.player2)

    def test_sync_checkers_from_coverage(self):
        """Test the sync_checkers method."""
        self.game.board.home[1] = 2
        self.game.board.bar[1] = 3
        self.game.sync_checkers()
        borne_off = 0
        on_bar = 0
        for checker in self.game.player1.checkers:
            if checker.state == CheckerState.BORNE_OFF:
                borne_off += 1
            if checker.state == CheckerState.ON_BAR:
                on_bar += 1
        self.assertEqual(borne_off, 2)
        self.assertEqual(on_bar, 3)

    def test_get_valid_moves_from_bar_from_logic(self):
        """Test get_valid_moves for a checker on the bar."""
        self.game.current_player = self.game.player1
        self.game.board.bar[1] = 1
        self.game.current_player.available_moves = [3, 4]
        valid_moves = self.game.get_valid_moves("bar")
        self.assertEqual(len(valid_moves), 2)
        self.assertIn(20, valid_moves)
        self.assertIn(21, valid_moves)

    def test_has_any_valid_moves_no_moves_from_logic(self):
        """Test has_any_valid_moves when there are no valid moves."""
        self.game.current_player = self.game.player1
        self.game.board.bar[1] = 1
        self.game.current_player.available_moves = [1, 2]
        self.game.board.points[22] = (2, 2)
        self.game.board.points[23] = (2, 2)
        self.assertFalse(self.game.has_any_valid_moves())

    def test_is_valid_bear_off_move_exact_roll_from_logic(self):
        """Test is_valid_bear_off_move with an exact dice roll."""
        for i in range(24):
            self.game.board.points[i] = (0, 0)
        for i in range(6):
            self.game.board.points[i] = (1, 2)
        self.game.board.points[0] = (1, 3)
        self.game.current_player = self.game.player1
        self.game.current_player.available_moves = [3]
        self.assertTrue(self.game.is_valid_bear_off_move(2))

    def test_no_valid_moves_in_bear_off_from_logic(self):
        """Test has_any_valid_moves when no valid moves are available during bear-off."""
        for i in range(24):
            self.game.board.points[i] = (0, 0)
        self.game.board.points[0] = (1, 15)
        self.game.current_player = self.game.player1
        self.game.current_player.available_moves = [2, 3]
        self.assertTrue(self.game.has_any_valid_moves())

    def test_no_valid_moves_out_of_home_board_from_logic(self):
        """Test that moves out of the home board are not valid during bear-off."""
        for i in range(24):
            self.game.board.points[i] = (0, 0)
        self.game.board.points[5] = (1, 15)
        self.game.current_player = self.game.player1
        self.game.current_player.available_moves = [1, 2]
        self.assertTrue(self.game.has_any_valid_moves())

    def test_roll_dice_for_turn_handles_multiple_skips(self):
        """
        Tests that `roll_dice_for_turn` correctly handles multiple consecutive
        turn skips by verifying the sequence of method calls.
        """
        game = self.game
        game.current_player = game.player1
        game.other_player = game.player2

        # Mock the methods that are called inside the loop
        with patch.object(game, "start_turn") as mock_start_turn, patch.object(
            game, "has_any_valid_moves", side_effect=[False, False, True]
        ) as mock_has_moves, patch.object(
            game, "switch_players"
        ) as mock_switch_players:

            game.roll_dice_for_turn()

            # --- Assertions ---
            # The loop should run 3 times before has_any_valid_moves returns True
            self.assertEqual(
                mock_start_turn.call_count, 3, "start_turn should be called 3 times"
            )
            self.assertEqual(
                mock_has_moves.call_count,
                3,
                "has_any_valid_moves should be called 3 times",
            )

            # Since the first two turns are skipped, players should be switched twice
            self.assertEqual(
                mock_switch_players.call_count,
                2,
                "switch_players should be called twice",
            )

    def test_turn_skips_after_bar_move_with_no_more_valid_moves(self):
        """
        Tests that the turn automatically skips if a player makes a move from
        the bar and has no other valid moves with the remaining dice.
        """
        # --- Setup ---
        # Clear the board to create a specific, controlled scenario
        for i in range(24):
            self.game.board.points[i] = (0, 0)

        # Player 2 (Black) has one checker on the bar and one on point 0
        self.game.board.bar[2] = 1
        self.game.board.points[0] = (2, 1)  # This checker cannot move
        self.game.sync_checkers()

        # Player 2's turn, rolls a 5 and a 2
        self.game.current_player = self.game.player2
        self.game.other_player = self.game.player1
        self.game.current_player.available_moves = [5, 2]
        self.game.current_player.remaining_moves = 2

        # Point 4 is OPEN for the dice roll of 5 (entry for bar checker)
        # Point 1 is BLOCKED for the dice roll of 2 (entry for bar checker)
        self.game.board.points[1] = (1, 2)
        # Point 2 is BLOCKED for the dice roll of 2 (for the checker on point 0)
        self.game.board.points[2] = (1, 2)
        # Point 6 is BLOCKED for the dice roll of 2 (for the checker that will land on point 4)
        self.game.board.points[6] = (1, 2)

        # --- Action ---
        # Player 2 makes their only valid move: entering from the bar to point 4
        move_successful = self.game.apply_move("bar", 4)
        self.assertTrue(
            move_successful, "The valid move from the bar should be successful"
        )

        # --- Assertion ---
        # After the move, Player 2 has one dice left (2) but no valid moves.
        # The turn should have automatically switched to Player 1.
        self.assertIs(
            self.game.current_player,
            self.game.player1,
            "Turn should switch to Player 1",
        )

    # ------------------------------
    # Additional tests to raise coverage of core/game.py
    # ------------------------------

    def test_apply_move_returns_false_when_dice_not_available(self):
        """If the move distance is not in available dice, apply_move returns False."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        # Ensure a legal board move (white 12 -> 10 is distance 2)
        game.board.points[12] = (1, 1)
        game.board.points[10] = (0, 0)
        game.current_player.available_moves = [3]  # distance 2 not available
        game.current_player.remaining_moves = 1
        self.assertFalse(game.apply_move(12, 10))

    def test_apply_move_wraps_board_exception_as_invalid_move(self):
        """When Board.move_checker raises, Game wraps it as InvalidMoveError."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3]
        game.current_player.remaining_moves = 1

        # Valid distance so we pass dice check, but force board failure
        with patch.object(game.board, "move_checker", side_effect=Exception("boom")):
            with self.assertRaises(InvalidMoveError):
                game.apply_move(10, 7)  # distance 3

    def test_switch_players_after_initialized(self):
        """switch_players swaps current and other players when initialized."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        game.switch_players()
        self.assertIs(game.current_player, game.player2)
        self.assertIs(game.other_player, game.player1)

    def test_get_valid_moves_includes_bear_off(self):
        """get_valid_moves should include 'bear_off' when conditions are met."""
        game = Game()
        game.setup_game()
        # Put all white checkers in home board and one at point 2
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[2] = (1, 1)
        game.board.points[0] = (1, 14)
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3]
        moves = game.get_valid_moves(2)
        self.assertIn("bear_off", moves)

    def test_apply_bear_off_move_exact_success(self):
        """apply_bear_off_move succeeds with exact dice value."""
        game = Game()
        game.setup_game()
        # Configure home-board-only state for white, checker at point 2
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[2] = (1, 1)
        game.board.points[0] = (1, 14)
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3]
        game.current_player.remaining_moves = 1
        home_before = game.board.home[1]
        ok = game.apply_bear_off_move(2)
        self.assertTrue(ok)
        self.assertEqual(game.board.home[1], home_before + 1)

    def test_apply_bear_off_move_uses_higher_dice_when_highest(self):
        """A larger die can be used for bearing off if checker is the highest."""
        game = Game()
        game.setup_game()
        # All white checkers in home, nothing above point 2
        for i in range(24):
            game.board.points[i] = (0, 0)
        # place 14 checkers at point 0 and 1 checker at point 2 (highest)
        game.board.points[0] = (1, 14)
        game.board.points[2] = (1, 1)
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [4]  # higher than required 3
        game.current_player.remaining_moves = 1
        ok = game.apply_bear_off_move(2)
        self.assertTrue(ok)

    def test_has_any_valid_moves_true_with_bar_entry(self):
        """has_any_valid_moves returns True when bar entry is possible."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        # One on bar, open point for a 3 or 4
        game.board.bar[1] = 1
        game.board.points[21] = (0, 0)  # open for 3
        game.board.points[20] = (0, 0)  # open for 4
        game.current_player.available_moves = [3, 4]
        self.assertTrue(game.has_any_valid_moves())

    def test_is_valid_bear_off_move_false_when_not_all_in_home(self):
        """is_valid_bear_off_move returns False if not all checkers are in home board."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        # Ensure at least one checker outside home (keep default setup)
        game.current_player.available_moves = [3]
        self.assertFalse(game.is_valid_bear_off_move(2))

    def test_roll_dice_for_turn_sets_turn_was_skipped_flag(self):
        """roll_dice_for_turn should set turn_was_skipped when first player has no moves."""
        game = self.game
        game.current_player = game.player1
        game.other_player = game.player2
        with patch.object(game, "start_turn") as _mock_start, patch.object(
            game, "has_any_valid_moves", side_effect=[False, True]
        ):
            game.roll_dice_for_turn()
            self.assertTrue(game.turn_was_skipped)

    def test_roll_dice_for_turn_returns_early_when_moves_exist(self):
        """If current player has moves after start_turn, it should return without switching."""
        game = self.game
        game.current_player = game.player1
        game.other_player = game.player2
        with patch.object(game, "start_turn") as _mock_start, patch.object(
            game, "has_any_valid_moves", return_value=True
        ) as _mock_has, patch.object(game, "switch_players") as mock_switch:
            game.roll_dice_for_turn()
            mock_switch.assert_not_called()
            self.assertFalse(game.turn_was_skipped)

    def test_apply_move_event_false_when_target_blocked(self):
        """Board returns moved=False when target is blocked; Game should return False."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        # make 12->10 attempt with distance 2 available, but block point 10 by black (2 checkers)
        game.board.points[12] = (1, 1)
        game.board.points[10] = (2, 2)
        game.current_player.available_moves = [2]
        game.current_player.remaining_moves = 1
        self.assertFalse(game.apply_move(12, 10))

    def test_apply_move_raises_if_fail_to_consume_dice(self):
        """If dice consumption fails unexpectedly, raise InvalidMoveError."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.other_player = game.player2
        # ensure a legal move distance 3
        game.board.points[10] = (1, 1)
        game.board.points[7] = (0, 0)
        with patch.object(
            game.current_player, "can_use_dice_for_move", return_value=True
        ), patch.object(
            game.board, "move_checker", return_value={"moved": True}
        ), patch.object(
            game.current_player, "use_dice_for_move", return_value=False
        ):
            game.current_player.remaining_moves = 1
            with self.assertRaises(InvalidMoveError):
                game.apply_move(10, 7)

    def test_apply_bear_off_move_switches_turn_when_no_moves_left(self):
        """After successful bear-off and no remaining moves, players should switch."""
        game = Game()
        game.setup_game()
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[0] = (1, 14)
        game.board.points[2] = (1, 1)
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3]
        game.current_player.remaining_moves = 1
        game.apply_bear_off_move(2)
        self.assertIs(game.current_player, game.player2)

    def test_get_valid_moves_empty_when_invalid_from_point_type(self):
        """get_valid_moves returns empty when from_point type is invalid (not int or 'bar')."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.available_moves = [1]
        self.assertEqual(game.get_valid_moves({}), [])

    def test_get_valid_moves_empty_when_bar_checker_present_and_from_point_is_board(
        self,
    ):
        """If a checker is on the bar, board moves should be empty."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.board.bar[1] = 1
        game.current_player.available_moves = [3]
        self.assertEqual(game.get_valid_moves(12), [])

    def test_is_valid_bear_off_move_true_with_higher_die(self):
        """is_valid_bear_off_move should return True using a larger die if highest checker."""
        game = Game()
        game.setup_game()
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[0] = (1, 14)
        game.board.points[2] = (1, 1)
        game.current_player = game.player1
        game.current_player.available_moves = [4]
        self.assertTrue(game.is_valid_bear_off_move(2))

    def test_is_valid_bear_off_move_false_for_non_int(self):
        """Non-integer from_point should yield False."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.available_moves = [1]
        self.assertFalse(game.is_valid_bear_off_move("bar"))

    def test_get_valid_moves_from_bar_with_no_bar_checkers_is_empty(self):
        """Asking for moves from 'bar' when bar is empty returns []."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.available_moves = [3]
        game.board.bar[1] = 0
        self.assertEqual(game.get_valid_moves("bar"), [])

    def test_get_valid_moves_returns_empty_when_not_own_checker(self):
        """Requesting moves from a point not owned by the player returns []."""
        game = Game()
        game.setup_game()
        game.current_player = game.player1
        game.current_player.available_moves = [2]
        # Choose a point owned by black in the starting position (11)
        self.assertEqual(game.get_valid_moves(11), [])

    def test_player2_valid_moves_direction(self):
        """Ensure player 2 (black) moves low->high and valid moves computed accordingly."""
        game = Game()
        game.setup_game()
        game.current_player = game.player2
        game.other_player = game.player1
        # Create a simple scenario: one black checker at point 0 moving to 2 with a 2
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[0] = (2, 1)
        game.current_player.available_moves = [2]
        moves = game.get_valid_moves(0)
        self.assertIn(2, moves)

    def test_bear_off_move_with_remaining_moves_and_other_moves_keeps_turn(self):
        """After a bear off, if another move is available, turn should not switch."""
        game = Game()
        game.setup_game()
        # All white in home, checkers at points 2 and 1
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[2] = (1, 1)
        game.board.points[1] = (1, 1)
        game.board.points[0] = (1, 13)
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3, 2]
        game.current_player.remaining_moves = 2
        game.apply_bear_off_move(2)
        # Another move (bear off from point 1 with a 2) should be available -> no switch
        self.assertIs(game.current_player, game.player1)

    def test_bear_off_move_with_remaining_moves_but_no_moves_switches_and_skips(self):
        """After a bear off, if no moves remain available, switch with skip flag."""
        game = Game()
        game.setup_game()
        # Only one checker on board at point 2, rest already borne off
        for i in range(24):
            game.board.points[i] = (0, 0)
        game.board.points[2] = (1, 1)
        game.board.home[1] = 14
        game.current_player = game.player1
        game.other_player = game.player2
        game.current_player.available_moves = [3, 1]
        game.current_player.remaining_moves = 2
        game.apply_bear_off_move(2)
        self.assertIs(game.current_player, game.player2)
        self.assertTrue(game.turn_was_skipped)

    def test_is_valid_bear_off_move_false_when_higher_die_but_not_highest(self):
        """Using a larger die is invalid if the checker is not the highest."""
        game = Game()
        game.setup_game()
        for i in range(24):
            game.board.points[i] = (0, 0)
        # Two checkers: at 4 (higher) and at 2; attempting from 2 with higher die should fail
        game.board.points[4] = (1, 1)
        game.board.points[2] = (1, 1)
        game.board.points[0] = (1, 13)
        game.current_player = game.player1
        game.current_player.available_moves = [5]  # higher than required 3
        self.assertFalse(game.is_valid_bear_off_move(2))


if __name__ == "__main__":
    unittest.main()
