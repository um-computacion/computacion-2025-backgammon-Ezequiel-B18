import unittest
from unittest.mock import patch
from core.game import Game
from core.player import PlayerColor

class TestGame(unittest.TestCase):
    def test_game_initialization(self):
        game = Game("Alice", "Bob")
        self.assertEqual(game.player1.name, "Alice")
        self.assertEqual(game.player2.name, "Bob")
        self.assertEqual(game.player1.color, PlayerColor.WHITE)
        self.assertEqual(game.player2.color, PlayerColor.BLACK)
        self.assertIsNotNone(game.board)
        self.assertIsNotNone(game.dice)

    def test_setup_distribute_checkers(self):
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
        game = Game()
        game.current_player = game.player1
        # Mock dice.roll and get_moves
        with patch.object(game.dice, "roll", return_value=(3, 4)):
            with patch.object(game.dice, "get_moves", return_value=[3, 4]):
                game.start_turn()
                self.assertTrue(game.player1.is_turn)
                self.assertEqual(game.player1.remaining_moves, 2)

if __name__ == "__main__":
    unittest.main()
