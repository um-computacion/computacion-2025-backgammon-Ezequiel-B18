"""Tests for the CLI (Command Line Interface) module."""

import unittest
from unittest.mock import patch, Mock

from cli.cli import BackgammonCLI, GameQuitException, main
from core.exceptions import NoMovesRemainingError


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
    def test_start_game_with_custom_names(self, mock_game_loop, mock_print, mock_input):  # pylint: disable=unused-argument
        """Test starting a game with custom player names."""
        mock_input.side_effect = ["Alice", "Bob", ""]

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
        mock_input.side_effect = ["", "", ""]

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
        mock_input.side_effect = ["h", "1 5"]

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
        mock_input.side_effect = ["invalid", "1 5"]

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_range(self, mock_print, mock_input):
        """Test handling moves with invalid point ranges."""
        mock_input.side_effect = ["0 5", "1 5"]

        mock_game = Mock()
        mock_game.apply_move.return_value = True
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_invalid_move(self, mock_print, mock_input):
        """Test handling invalid moves rejected by game logic."""
        mock_input.side_effect = ["1 5", "2 6"]

        mock_game = Mock()
        mock_game.apply_move.side_effect = [False, True]
        self.cli.game = mock_game

        self.cli.handle_player_move()

        self.assertTrue(mock_print.called)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_handle_player_move_exception(self, mock_print, mock_input):
        """Test handling move that raises exception."""
        mock_input.side_effect = ["1 5", "2 6"]

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
        mock_game.current_player = mock_player
        mock_game.is_game_over.side_effect = [False, True]

        # Fix: Make board.bar subscriptable
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}
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
        self, mock_handle_move, mock_display_info, mock_display_board, mock_input  # pylint: disable=unused-argument
    ):
        """Test game loop handling quit exception."""
        mock_input.return_value = ""

        mock_game = Mock()
        mock_player = Mock()
        mock_player.remaining_moves = 1
        mock_player.player_id = 1
        mock_game.current_player = mock_player
        mock_game.is_game_over.return_value = False

        # Fix: Make board.bar subscriptable
        mock_board = Mock()
        mock_board.bar = {1: 0, 2: 0}
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


if __name__ == "__main__":
    unittest.main()
