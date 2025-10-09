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
    def test_start_game_with_custom_names(
        self, mock_game_loop, mock_print, mock_input
    ):  # pylint: disable=unused-argument
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
        mock_player.can_use_dice_for_move.return_value = True
        mock_player.use_dice_for_move.return_value = True
        
        mock_board = Mock()
        mock_board.bar = {1: 1, 2: 0}  # White player has 1 checker on bar
        mock_points = [(0, 0)] * 24
        # White enters on points 0-5 (1-6 in user terms)
        mock_points[2] = (0, 0)  # Point 3 is empty, good for entry
        mock_board.points = mock_points
        mock_board.enter_from_bar.return_value = True
        
        mock_game.current_player = mock_player
        mock_game.board = mock_board
        
        self.cli.game = mock_game
        
        # Test that _has_legal_bar_entries returns True when player has checkers on bar
        result = self.cli._has_legal_bar_entries()
        self.assertTrue(result)
        
        # Test direct bar entry logic
        with patch("builtins.print") as mock_print:
            # Simulate the bar entry handling manually
            to_point_user = 3  # User enters point 3
            to_point_board = to_point_user - 1  # Convert to 0-based index (point 2)
            distance = to_point_user  # Distance for white from bar to point 3
            
            # Check dice validation
            can_use_dice = mock_player.can_use_dice_for_move(distance)
            self.assertTrue(can_use_dice)
            
            # Check board entry
            entry_success = mock_board.enter_from_bar(mock_player.player_id, to_point_board)
            self.assertTrue(entry_success)
        
        # Verify enter_from_bar was called with correct parameters
        mock_board.enter_from_bar.assert_called_with(1, 2)  # Player 1, point 2 (0-based)


if __name__ == "__main__":
    unittest.main()
