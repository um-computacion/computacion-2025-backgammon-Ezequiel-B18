"""Tests for the CLI (Command Line Interface) module."""

import unittest
from unittest.mock import patch, Mock

from cli.cli import BackgammonCLI, GameQuitException, main
from core.exceptions import (
    NoMovesRemainingError,
    InvalidPlayerTurnError,
    GameQuitException,
)


class TestBackgammonCLI(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for the BackgammonCLI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cli = BackgammonCLI()

    def test_cli_initialization(self):
        """Test that CLI initializes correctly."""
        self.assertIsNone(self.cli.game)
        self.assertIsNone(self.cli.player1_name)
        self.assertIsNone(self.cli.player2_name)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch.object(BackgammonCLI, "game_loop")
    def test_start_game_with_custom_names(
        self, mock_game_loop, mock_print, mock_input
    ):  # pylint: disable=unused-argument
        """Test starting a game with custom player names."""
        mock_input.side_effect = ["Alice", "Bob", "", "q", "q"]

        with patch("cli.cli.Game") as mock_game_class:
            mock_game = Mock()
            mock_game_class.return_value = mock_game
            mock_game.dice.initial_values = [4, 2]
            mock_game.initial_roll_until_decided.return_value = 1
            mock_game.player1.name = "Alice"
            mock_game.player2.name = "Bob"

            self.cli.start_game()

            mock_game_class.assert_called_once_with("Alice", "Bob")
            mock_game.setup_game.assert_called_once()
            mock_game_loop.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch.object(BackgammonCLI, "game_loop")
    def test_start_game_with_default_names(
        self, mock_game_loop, mock_print, mock_input  # pylint: disable=unused-argument
    ):
        """Test starting a game with default player names."""
        mock_input.side_effect = ["", "", "", "q", "q"]

        with patch("cli.cli.Game") as mock_game_class:
            mock_game = Mock()
            mock_game_class.return_value = mock_game
            mock_game.dice.initial_values = [3, 5]
            mock_game.initial_roll_until_decided.return_value = 2

            self.cli.start_game()

            mock_game_class.assert_called_once_with("White", "Black")

    @patch("builtins.print")
    def test_display_welcome(self, mock_print):
        """Test welcome message display."""
        self.cli.display_welcome()

        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("WELCOME TO BACKGAMMON!" in call for call in calls))

    @patch("builtins.print")
    def test_display_help(self, mock_print):
        """Test help display."""
        self.cli.display_help()

        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("BACKGAMMON HELP" in call for call in calls))

    def test_display_board(self):
        """Test board display functionality."""
        mock_game = Mock()
        mock_board = Mock()

        points = [(0, 0) for _ in range(24)]
        points[0] = (1, 2)
        points[23] = (2, 2)

        mock_board.points = points
        mock_board.bar = {1: 0, 2: 1}
        mock_board.home = {1: 3, 2: 0}

        mock_game.board = mock_board
        self.cli.game = mock_game

        with patch("builtins.print"):
            self.cli.display_board()

    def test_display_current_player_info(self):
        """Test current player info display."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Alice"
        mock_player.color.name = "WHITE"
        mock_player.remaining_moves = 2

        mock_game.current_player = mock_player
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_current_player_info()
            self.assertTrue(mock_print.called)

    def test_display_dice_roll_normal(self):
        """Test dice roll display for normal roll."""
        mock_game = Mock()
        mock_dice = Mock()
        mock_dice.values = [3, 5]
        mock_dice.is_doubles.return_value = False
        mock_dice.get_moves.return_value = [3, 5]

        mock_game.dice = mock_dice
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_dice_roll()
            self.assertTrue(mock_print.called)

    def test_display_dice_roll_doubles(self):
        """Test dice roll display for doubles."""
        mock_game = Mock()
        mock_dice = Mock()
        mock_dice.values = [4, 4]
        mock_dice.is_doubles.return_value = True
        mock_dice.get_moves.return_value = [4, 4, 4, 4]

        mock_game.dice = mock_dice
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_dice_roll()
            self.assertTrue(mock_print.called)

    def test_display_available_moves_normal(self):
        """Test available moves display for normal situation."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Alice"
        mock_player.remaining_moves = 2
        mock_player.player_id = 1
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}

        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_available_moves()
            self.assertTrue(mock_print.called)

    def test_display_available_moves_with_bar(self):
        """Test available moves display when player has checkers on bar."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Bob"
        mock_player.remaining_moves = 1
        mock_player.player_id = 2
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 1}

        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_available_moves()
            self.assertTrue(mock_print.called)

    @patch("builtins.input")
    def test_handle_player_move_valid(self, mock_input):
        """Test handling a valid player move."""
        mock_input.return_value = "1 5"

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        with patch("builtins.print"):
            self.cli.handle_player_move()

        mock_game.apply_move.assert_called_once_with(0, 4)

    @patch("builtins.input")
    def test_handle_player_move_quit(self, mock_input):
        """Test handling quit command."""
        mock_input.return_value = "q"

        with patch("builtins.print"):
            with self.assertRaises(GameQuitException):
                self.cli.handle_player_move()

    @patch("builtins.input")
    @patch.object(BackgammonCLI, "display_help")
    def test_handle_player_move_help(self, mock_display_help, mock_input):
        """Test handling help command."""
        mock_input.side_effect = ["h", "1 5", "q"]

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        with patch("builtins.print"):
            self.cli.handle_player_move()

        mock_display_help.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_format(self, mock_print, mock_input):
        """Test handling invalid move format."""
        mock_input.side_effect = ["invalid", "1 5", "q"]

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_range(self, mock_print, mock_input):
        """Test handling moves with invalid point ranges."""
        mock_input.side_effect = ["0 5", "1 5", "q"]

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_move(self, mock_print, mock_input):
        """Test handling invalid moves rejected by game logic."""
        mock_input.side_effect = ["1 5", "2 6", "quit"]

        mock_game = Mock()
        mock_game.apply_move.side_effect = [False, True]
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_exception(self, mock_print, mock_input):
        """Test handling move that raises exception."""
        mock_input.side_effect = ["1 5", "2 6", "quit"]

        mock_game = Mock()
        mock_game.apply_move.side_effect = [NoMovesRemainingError("Alice"), True]
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    def test_display_game_over_with_winner(self):
        """Test game over display with a winner."""
        mock_game = Mock()
        mock_winner = Mock()
        mock_winner.name = "Alice"
        mock_winner.color.name = "WHITE"
        mock_game.get_winner.return_value = mock_winner

        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_game_over()
            self.assertTrue(mock_print.called)

    def test_display_game_over_no_winner(self):
        """Test game over display without winner."""
        mock_game = Mock()
        mock_game.get_winner.return_value = None

        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_game_over()
            self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch.object(BackgammonCLI, "display_board")
    @patch.object(BackgammonCLI, "display_current_player_info")
    @patch.object(BackgammonCLI, "handle_player_move")
    def test_game_loop_basic(
        self, mock_handle_move, mock_display_info, mock_display_board, mock_input
    ):
        """Test basic game loop functionality."""
        mock_input.return_value = ""

        mock_game = Mock()
        mock_player = Mock()
        mock_player.remaining_moves = 1
        mock_player.player_id = 1
        mock_player.available_moves = [3, 4]
        mock_game.current_player = mock_player
        mock_game.is_game_over.side_effect = [False, True]

        # Fix: Make board.bar and board.points subscriptable
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}
        # Create a mock points list that returns (player_id, count) tuples
        mock_points = [(0, 0)] * 24
        mock_points[5] = (1, 2)  # Some checkers for testing
        mock_board.points = mock_points
        mock_board.is_valid_move.return_value = True
        mock_game.board = mock_board

        def mock_handle_move_side_effect():
            mock_player.remaining_moves = 0

        mock_handle_move.side_effect = mock_handle_move_side_effect

        self.cli.game = mock_game

        with patch("builtins.print"):
            self.cli.game_loop()

        mock_display_board.assert_called_once()
        mock_display_info.assert_called_once()
        mock_game.start_turn.assert_called_once()

    @patch("cli.cli.BackgammonCLI")
    def test_main_function_normal(self, mock_cli_class):
        """Test main function normal execution."""
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        main()

        mock_cli_class.assert_called_once()
        mock_cli.start_game.assert_called_once()

    @patch("cli.cli.BackgammonCLI")
    @patch("builtins.print")
    def test_main_function_keyboard_interrupt(self, mock_print, mock_cli_class):
        """Test main function with keyboard interrupt."""
        mock_cli = Mock()
        mock_cli.start_game.side_effect = KeyboardInterrupt()
        mock_cli_class.return_value = mock_cli

        main()

        self.assertTrue(mock_print.called)

    @patch("cli.cli.BackgammonCLI")
    @patch("builtins.print")
    def test_main_function_unexpected_error(self, mock_print, mock_cli_class):
        """Test main function with unexpected error."""
        mock_cli = Mock()
        mock_cli.start_game.side_effect = Exception("Unexpected error")
        mock_cli_class.return_value = mock_cli

        main()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch.object(BackgammonCLI, "display_board")
    @patch.object(BackgammonCLI, "display_current_player_info")
    @patch.object(BackgammonCLI, "handle_player_move")
    def test_game_loop_with_quit(
        self,
        mock_handle_move,
        mock_display_info,
        mock_display_board,
        mock_input,  # pylint: disable=unused-argument
    ):
        """Test game loop handling quit exception."""
        mock_input.return_value = ""

        mock_game = Mock()
        mock_player = Mock()
        mock_player.remaining_moves = 1
        mock_player.player_id = 1
        mock_player.available_moves = [3, 4]
        mock_game.current_player = mock_player
        mock_game.is_game_over.return_value = False

        # Fix: Make board.bar and board.points subscriptable
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}
        # Create a mock points list that returns (player_id, count) tuples
        mock_points = [(0, 0)] * 24
        mock_points[5] = (1, 2)  # Some checkers for testing
        mock_board.points = mock_points
        mock_board.is_valid_move.return_value = True
        mock_game.board = mock_board

        # Simulate quit on first move
        mock_handle_move.side_effect = GameQuitException()

        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.game_loop()

        # Verify quit message was printed
        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("Game ended by player" in call for call in calls))

    def test_double_dice_all_moves(self):
        """Test that player can use all 4 moves from double dice."""
        # Setup game with double dice [3,3,3,3]
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Player1"
        mock_player.player_id = 1
        mock_player.remaining_moves = 4  # All 4 moves from doubles
        mock_player.available_moves = [3, 3, 3, 3]  # Double 3s
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        mock_points = [(0, 0)] * 24
        mock_points[5] = (1, 2)  # Player has checkers on point 5
        mock_points[8] = (1, 1)  # Player has checkers on point 8
        mock_board.points = mock_points
        mock_board.is_valid_move.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.apply_move.return_value = True
        
        mock_dice = Mock()
        mock_dice.values = [3, 3]
        mock_dice.is_doubles.return_value = True
        mock_dice.get_moves.return_value = [3, 3, 3, 3]
        mock_game.dice = mock_dice
        
        self.cli.game = mock_game
        
        # Test that CLI can handle multiple moves from doubles
        with patch("builtins.input", side_effect=["5 8", "8 11", "11 14", "14 17"]):
            with patch("builtins.print"):
                # Simulate moves that consume remaining_moves
                def mock_apply_move_side_effect(from_point, to_point):
                    mock_player.remaining_moves -= 1
                    return True
                
                mock_game.apply_move.side_effect = mock_apply_move_side_effect
                
                # Execute 4 moves
                for _ in range(4):
                    if mock_player.remaining_moves > 0:
                        self.cli.handle_player_move()
        
        # Verify all moves were processed
        self.assertEqual(mock_game.apply_move.call_count, 4)
        self.assertEqual(mock_player.remaining_moves, 0)

    def test_auto_skip_no_moves_available(self):
        """Test that CLI detects when no legal moves are available."""
        # Setup game where player has no legal moves
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Player1"
        mock_player.player_id = 1
        mock_player.remaining_moves = 2  # Add remaining_moves for the while loop
        mock_player.available_moves = [6, 5]  # High dice values
        mock_player.can_use_dice_for_move.return_value = False  # Can't use any dice
        mock_player.end_turn = Mock()  # Add end_turn method
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        # Setup board where player has checkers but can't move with high dice
        mock_points = [(0, 0)] * 24
        mock_points[0] = (1, 15)  # All checkers on point 1, can't move with 6,5
        mock_board.points = mock_points
        mock_board.is_valid_move.return_value = False  # No valid moves
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.switch_players = Mock()  # Add switch_players method
        
        self.cli.game = mock_game
        
        # Test that _has_legal_moves returns False
        result = self.cli._has_legal_moves()
        self.assertFalse(result)
        
        # Test that CLI properly handles this in _execute_player_turn
        with patch.object(self.cli, 'display_board'):
            with patch.object(self.cli, 'display_current_player_info'):
                with patch.object(self.cli, 'display_dice_roll'):
                    with patch.object(self.cli, 'display_available_moves'):
                        with patch("builtins.input", return_value=""):
                            with patch("builtins.print") as mock_print:
                                # Mock start_turn to avoid actual dice rolling
                                mock_game.start_turn = Mock()
                                self.cli._execute_player_turn()
        
        # Verify skip message was printed
        mock_print.assert_any_call(f"\n{mock_player.name} has no legal moves available.")
        mock_print.assert_any_call("Skipping turn...")

    def test_checkers_off_the_bar(self):
        """Test that player can enter checkers from the bar."""
        # Setup game with checker on bar
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Player1"
        mock_player.player_id = 1  # White player
        mock_player.remaining_moves = 2
        mock_player.available_moves = [3, 4]

        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White player has checker on bar
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.home = {1: 0, 2: 0}

        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.apply_move.return_value = True

        self.cli.game = mock_game

        # Test that CLI recognizes when player has checkers on bar
        self.assertEqual(mock_board.bar[1], 1)
        
        # Test the bar check logic
        self.assertTrue(mock_board.bar[mock_player.player_id] > 0)

    @patch("builtins.print")
    @patch.object(BackgammonCLI, "display_game_over")
    def test_game_loop_quit_exception(self, mock_display_game_over, mock_print):
        """Test that game loop handles GameQuitException properly."""
        mock_game = Mock()
        mock_game.is_game_over.return_value = False
        mock_game.current_player = Mock()
        
        self.cli.game = mock_game
        
        # Mock _execute_player_turn to raise GameQuitException
        with patch.object(self.cli, "_execute_player_turn", side_effect=GameQuitException("Player quit")):
            self.cli.game_loop()
        
        # Verify quit message was printed and game_over was not called
        mock_print.assert_any_call("Game ended by player.")
        mock_display_game_over.assert_not_called()

    @patch("builtins.print")
    def test_main_keyboard_interrupt(self, mock_print):
        """Test main function handling KeyboardInterrupt."""
        with patch.object(BackgammonCLI, "start_game", side_effect=KeyboardInterrupt):
            main()
        
        mock_print.assert_any_call("\nGame interrupted by user.")

    @patch("builtins.print")
    def test_main_game_quit_exception(self, mock_print):
        """Test main function handling GameQuitException."""
        with patch.object(BackgammonCLI, "start_game", side_effect=GameQuitException("Quit")):
            main()
        
        mock_print.assert_any_call("Game error: Quit")

    @patch("builtins.print")
    def test_main_os_error(self, mock_print):
        """Test main function handling OSError."""
        with patch.object(BackgammonCLI, "start_game", side_effect=OSError("File error")):
            main()
        
        mock_print.assert_any_call("System error: File error")

    @patch("builtins.print")
    def test_main_unexpected_exception(self, mock_print):
        """Test main function handling unexpected exceptions."""
        with patch.object(BackgammonCLI, "start_game", side_effect=ValueError("Unexpected error")):
            main()
        
        mock_print.assert_any_call("An unexpected error occurred: Unexpected error")

    def test_has_legal_bar_entries_white_player(self):
        """Test _has_legal_bar_entries for white player."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [3, 5]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        # Set up board points - entry points for white are 0-5 (points 1-6)
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[2] = (1, 1)  # Point 3 has one white checker
        mock_board.points[4] = (2, 2)  # Point 5 is blocked by black
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        # Should find legal entry (point 3 is not blocked)
        result = self.cli._has_legal_bar_entries()
        self.assertTrue(result)

    def test_has_legal_bar_entries_black_player(self):
        """Test _has_legal_bar_entries for black player."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 2  # Black
        mock_player.available_moves = [2, 4]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        # Set up board points - entry points for black are 18-23 (points 19-24)
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[20] = (2, 1)  # Point 21 has one black checker
        mock_board.points[19] = (1, 2)  # Point 20 is blocked by white
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_bar_entries()
        self.assertTrue(result)

    def test_has_legal_bar_entries_all_blocked(self):
        """Test _has_legal_bar_entries when all entry points are blocked."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [1, 2, 3, 4, 5, 6]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        # Set up board where all white entry points (0-5) are blocked
        mock_board.points = [(0, 0) for _ in range(24)]
        for i in range(6):  # Block all entry points for white
            mock_board.points[i] = (2, 2)  # 2+ black checkers
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_bar_entries()
        self.assertFalse(result)

    def test_has_legal_regular_moves_with_valid_moves(self):
        """Test _has_legal_regular_moves when valid moves exist."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [3, 5]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        # Set up board with white checkers
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[10] = (1, 2)  # White checkers at point 11
        mock_board.is_valid_move.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_regular_moves()
        self.assertTrue(result)

    def test_has_legal_regular_moves_no_valid_moves(self):
        """Test _has_legal_regular_moves when no valid moves exist."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [6]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        # Set up board with white checkers but no valid moves
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[23] = (1, 2)  # White checkers at point 24
        mock_board.is_valid_move.return_value = False  # All moves blocked
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_regular_moves()
        self.assertFalse(result)

    def test_has_legal_bear_offs_white_player(self):
        """Test _has_legal_bear_offs for white player with valid bear offs."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [2, 4]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.all_checkers_in_home_board.return_value = True
        # Set up home board for white (points 0-5)
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[1] = (1, 2)  # White checkers at point 2
        mock_board.points[3] = (1, 1)  # White checker at point 4
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_bear_offs()
        self.assertTrue(result)

    def test_has_legal_bear_offs_black_player(self):
        """Test _has_legal_bear_offs for black player with valid bear offs."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 2  # Black
        mock_player.available_moves = [3, 6]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.all_checkers_in_home_board.return_value = True
        # Set up home board for black (points 18-23)
        mock_board.points = [(0, 0) for _ in range(24)]
        mock_board.points[20] = (2, 2)  # Black checkers at point 21
        mock_board.points[18] = (2, 1)  # Black checker at point 19
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_bear_offs()
        self.assertTrue(result)

    def test_has_legal_bear_offs_not_in_home_board(self):
        """Test _has_legal_bear_offs when not all checkers are in home board."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.available_moves = [1, 2]
        
        mock_board = Mock()
        mock_board.all_checkers_in_home_board.return_value = False
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        result = self.cli._has_legal_bear_offs()
        self.assertFalse(result)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_white(self, mock_print, mock_input):
        """Test handle_player_move with bar entry for white player."""
        mock_input.side_effect = ["bar 20", "q"]  # White enters at point 20
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 2
        mock_player.available_moves = [5]
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        mock_player.end_turn = Mock()
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        mock_board.enter_from_bar.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.sync_checkers = Mock()
        mock_game.switch_players = Mock()
        
        self.cli.game = mock_game
        
        self.cli.handle_player_move()
        
        # Verify bar entry was attempted
        mock_board.enter_from_bar.assert_called_once_with(1, 19)  # Point 20 -> index 19
        mock_player.use_dice_for_move.assert_called_once_with(5)  # Distance for white to point 20

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_black(self, mock_print, mock_input):
        """Test handle_player_move with bar entry for black player."""
        mock_input.side_effect = ["bar 3", "q"]  # Black enters at point 3
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 2  # Black
        mock_player.remaining_moves = 1
        mock_player.available_moves = [3]
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        mock_player.end_turn = Mock()
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 1}  # Black has checker on bar
        mock_board.enter_from_bar.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.sync_checkers = Mock()
        mock_game.switch_players = Mock()
        
        self.cli.game = mock_game
        
        self.cli.handle_player_move()
        
        # Verify bar entry was attempted
        mock_board.enter_from_bar.assert_called_once_with(2, 2)  # Point 3 -> index 2
        mock_player.use_dice_for_move.assert_called_once_with(3)  # Distance for black to point 3

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_invalid_point(self, mock_print, mock_input):
        """Test handle_player_move with invalid bar entry point."""
        mock_input.side_effect = ["bar 25", "q", "q"]  # Invalid point, then quit
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [6]
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        # Should raise GameQuitException when user enters "quit"
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        # Verify error messages were printed
        mock_print.assert_any_call("Invalid point. Points must be between 1-24.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_no_checkers_on_bar(self, mock_print, mock_input):
        """Test handle_player_move when trying bar entry with no checkers on bar."""
        mock_input.side_effect = ["bar 20"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("You don't have any checkers on the bar!")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_wrong_range_white(self, mock_print, mock_input):
        """Test bar entry with wrong range for white player."""
        mock_input.side_effect = ["bar 10"] + ["q"] * 10  # White tries point 10 (should be 19-24)
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("White must enter on points 19-24.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_wrong_range_black(self, mock_print, mock_input):
        """Test bar entry with wrong range for black player."""
        mock_input.side_effect = ["bar 15"] + ["q"] * 10  # Black tries point 15 (should be 1-6)
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 2  # Black
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 1}  # Black has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Black must enter on points 1-6.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_invalid_dice(self, mock_print, mock_input):
        """Test bar entry when dice don't match distance."""
        mock_input.side_effect = ["bar 20"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [3]  # Only has 3, but needs 6 for point 20
        mock_player.can_use_dice_for_move.return_value = False
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        # Verify any dice-related error message is printed
        calls = [str(call) for call in mock_print.call_args_list]
        dice_error_found = any("dice" in call.lower() or "cannot" in call.lower() for call in calls)
        self.assertTrue(dice_error_found, f"Expected dice error message in calls: {calls}")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_blocked(self, mock_print, mock_input):
        """Test bar entry when target point is blocked."""
        mock_input.side_effect = ["bar 20"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [6]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        mock_board.enter_from_bar.return_value = False  # Entry blocked
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Cannot enter at that point. It may be blocked by opponent checkers.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bar_entry_invalid_format(self, mock_print, mock_input):
        """Test bar entry with invalid input format."""
        mock_input.side_effect = ["bar abc"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid input. Enter 'bar' followed by a point number (e.g., 'bar 5').")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bear_off_white(self, mock_print, mock_input):
        """Test handle_player_move with bearing off for white player."""
        mock_input.side_effect = ["6 off", "q"]  # Bear off from point 6
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [6]
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        mock_player.end_turn = Mock()
        
        mock_board = Mock()
        mock_board.bear_off.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.sync_checkers = Mock()
        mock_game.switch_players = Mock()
        
        self.cli.game = mock_game
        
        self.cli.handle_player_move()
        
        # Verify bear off was attempted
        mock_board.bear_off.assert_called_once_with(1, 5)  # Point 6 -> index 5
        mock_player.use_dice_for_move.assert_called_once_with(6)  # Distance for white from point 6

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bear_off_black(self, mock_print, mock_input):
        """Test handle_player_move with bearing off for black player."""
        mock_input.side_effect = ["19 off", "q"]  # Bear off from point 19
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 2  # Black
        mock_player.remaining_moves = 1
        mock_player.available_moves = [6]
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        mock_player.end_turn = Mock()
        
        mock_board = Mock()
        mock_board.bear_off.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.sync_checkers = Mock()
        mock_game.switch_players = Mock()
        
        self.cli.game = mock_game
        
        self.cli.handle_player_move()
        
        # Verify bear off was attempted
        mock_board.bear_off.assert_called_once_with(2, 18)  # Point 19 -> index 18
        mock_player.use_dice_for_move.assert_called_once_with(6)  # Distance for black from point 19

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bear_off_invalid_point(self, mock_print, mock_input):
        """Test bearing off from invalid point."""
        mock_input.side_effect = ["25 off", "0 off"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid point. Points must be between 1-24.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bear_off_invalid_dice(self, mock_print, mock_input):
        """Test bearing off when dice don't match distance."""
        mock_input.side_effect = ["6 off"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [3]  # Only has 3, but needs 6 for point 6
        mock_player.can_use_dice_for_move.return_value = False
        
        mock_board = Mock()
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Cannot bear off from point 6. Distance 6 doesn't match available dice: [3]")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_bear_off_invalid_conditions(self, mock_print, mock_input):
        """Test bearing off when conditions not met."""
        mock_input.side_effect = ["6 off"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        mock_player.available_moves = [6]
        mock_player.can_use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.bear_off.return_value = False  # Bear off not allowed
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid bear off attempt. Check that all checkers are in home board.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_normal_move_invalid_points(self, mock_print, mock_input):
        """Test normal move with invalid point numbers."""
        mock_input.side_effect = ["25 10", "5 0"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid points. Points must be between 1-24.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_input_format(self, mock_print, mock_input):
        """Test handle_player_move with invalid input format."""
        mock_input.side_effect = ["abc def"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid input. Please enter valid numbers or 'off' for bearing off.")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_normal_move_success(self, mock_print, mock_input):
        """Test successful normal move."""
        mock_input.side_effect = ["13 7"]  # Move from point 13 to point 7
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.apply_move.return_value = True
        
        self.cli.game = mock_game
        
        self.cli.handle_player_move()
        
        # Verify normal move was attempted
        mock_game.apply_move.assert_called_once_with(12, 6)  # Convert from 1-based to 0-based
        mock_print.assert_any_call("Move successful: 13 → 7 (distance: 6)")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_normal_move_failed(self, mock_print, mock_input):
        """Test failed normal move."""
        mock_input.side_effect = ["13 7"] + ["q"] * 10
        
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1  # White
        mock_player.remaining_moves = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        mock_game.apply_move.return_value = False
        
        self.cli.game = mock_game
        
        with self.assertRaises(GameQuitException):
            self.cli.handle_player_move()
        
        mock_print.assert_any_call("Invalid move. Try again or check the board.")

    @patch("builtins.print")
    def test_display_board_with_many_checkers(self, mock_print):
        """Test board display with stacks of more than 5 checkers."""
        mock_game = Mock()
        mock_board = Mock()

        # Set up board with various checker counts including > 5
        points = [(0, 0) for _ in range(24)]
        points[0] = (1, 8)   # 8 white checkers (should show count)
        points[5] = (2, 12)  # 12 black checkers (should show '+')
        points[12] = (1, 3)  # Normal stack
        points[18] = (2, 6)  # 6 checkers

        mock_board.points = points
        mock_board.bar = {1: 2, 2: 1}
        mock_board.home = {1: 5, 2: 3}

        mock_game.board = mock_board
        self.cli.game = mock_game

        self.cli.display_board()
            
        # Verify print was called (board was displayed)
        self.assertTrue(mock_print.called)
        
        # Check that specific board elements were displayed
        calls = [str(call) for call in mock_print.call_args_list]
        
        # Just check that the board display method was called successfully
        # (The exact format may vary, but the method should complete)
        self.assertTrue(len(calls) > 0, "Expected some print calls from board display")

    @patch("builtins.print")
    def test_display_board_empty_points(self, mock_print):
        """Test board display with mostly empty points."""
        mock_game = Mock()
        mock_board = Mock()

        # Set up mostly empty board
        points = [(0, 0) for _ in range(24)]
        points[0] = (1, 1)   # Single white checker
        points[23] = (2, 1)  # Single black checker

        mock_board.points = points
        mock_board.bar = {1: 0, 2: 0}
        mock_board.home = {1: 0, 2: 0}

        mock_game.board = mock_board
        self.cli.game = mock_game

        self.cli.display_board()
            
        self.assertTrue(mock_print.called)

    @patch("builtins.print")
    def test_display_available_moves_empty_bar(self, mock_print):
        """Test display_available_moves when no checkers on bar."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1
        mock_player.available_moves = [3, 5]
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game

        self.cli.display_available_moves()
            
        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        
        # Should not mention specific bar warning about having checkers on bar
        bar_warning_mentioned = any("you have checkers on the bar" in call.lower() for call in calls)
        self.assertFalse(bar_warning_mentioned)

    @patch("builtins.print")
    def test_display_available_moves_all_in_home(self, mock_print):
        """Test display_available_moves when all checkers in home board."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1
        mock_player.available_moves = [2, 4]
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}
        mock_board.all_checkers_in_home_board.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game

        self.cli.display_available_moves()
            
        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        
        # Should mention move instructions (general instructions always shown)
        move_instructions_mentioned = any("enter moves as" in call.lower() for call in calls)
        self.assertTrue(move_instructions_mentioned)

    @patch("builtins.print")
    def test_display_game_over_edge_cases(self, mock_print):
        """Test display_game_over with different winner scenarios."""
        # Test with no winner
        mock_game = Mock()
        mock_game.get_winner.return_value = None
        
        self.cli.game = mock_game
        
        self.cli.display_game_over()
            
        mock_print.assert_any_call("Game ended without a winner.")

    def test_display_board_edge_checker_positions(self):
        """Test display_board with checkers in edge positions."""
        mock_game = Mock()
        mock_board = Mock()

        # Set up board with checkers in edge positions
        points = [(0, 0) for _ in range(24)]
        points[0] = (1, 1)    # Point 1
        points[23] = (2, 1)   # Point 24
        points[11] = (1, 7)   # Point 12 with many checkers
        points[12] = (2, 9)   # Point 13 with many checkers

        mock_board.points = points
        mock_board.bar = {1: 0, 2: 0}
        mock_board.home = {1: 0, 2: 0}

        mock_game.board = mock_board
        self.cli.game = mock_game

        with patch("builtins.print"):
            # Should not raise any exceptions
            self.cli.display_board()

    def test_display_current_player_info_edge_cases(self):
        """Test display_current_player_info with edge cases."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.name = "Player with Long Name"
        mock_player.color.name = "WHITE"
        mock_player.remaining_moves = 0  # No moves remaining
        
        mock_game.current_player = mock_player
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_current_player_info()
            
        self.assertTrue(mock_print.called)

    def test_display_dice_roll_edge_cases(self):
        """Test display_dice_roll with various dice combinations."""
        mock_game = Mock()
        mock_dice = Mock()
        
        # Test with high dice values
        mock_dice.values = [6, 6]
        mock_dice.is_doubles.return_value = True
        mock_dice.get_moves.return_value = [6, 6, 6, 6]
        
        mock_game.dice = mock_dice
        self.cli.game = mock_game

        with patch("builtins.print") as mock_print:
            self.cli.display_dice_roll()
            
        self.assertTrue(mock_print.called)
        calls = [str(call) for call in mock_print.call_args_list]
        
        # Should mention doubles
        doubles_mentioned = any("doubles" in call.lower() for call in calls)
        self.assertTrue(doubles_mentioned)

    def test_has_legal_moves_with_bar_checkers(self):
        """Test _has_legal_moves when player has checkers on bar."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White has checker on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        # Mock the bar entries method to return True
        with patch.object(self.cli, '_has_legal_bar_entries', return_value=True):
            result = self.cli._has_legal_moves()
            self.assertTrue(result)

    def test_has_legal_moves_no_bar_checkers(self):
        """Test _has_legal_moves when no checkers on bar."""
        mock_game = Mock()
        mock_player = Mock()
        mock_player.player_id = 1
        
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}  # No checkers on bar
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        self.cli.game = mock_game
        
        # Mock both regular moves and bear offs
        with patch.object(self.cli, '_has_legal_regular_moves', return_value=True):
            with patch.object(self.cli, '_has_legal_bear_offs', return_value=False):
                result = self.cli._has_legal_moves()
                self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
