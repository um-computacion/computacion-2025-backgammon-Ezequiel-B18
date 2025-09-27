"""Tests for the Dice class."""

import unittest
from unittest.mock import patch
from core.dice import Dice
from core.exceptions import DiceNotRolledError


class TestDice(unittest.TestCase):
    """Test cases for the Dice class."""

    def setUp(self):
        self.dice = Dice()

    def test_dice_initialization(self):
        """Test that a new Dice object is initialized correctly"""
        self.assertIsNotNone(self.dice)

        # Test that accessing values before rolling raises exception
        with self.assertRaises(DiceNotRolledError):
            _ = self.dice.values

        # Test that initial_values are properly initialized
        self.assertEqual(self.dice.initial_values, [0, 0])

    def test_dice_not_rolled_error(self):
        """Test that accessing dice values before rolling raises DiceNotRolledError"""
        dice = Dice()

        with self.assertRaises(DiceNotRolledError) as context:
            _ = dice.values

        self.assertIn("Dice must be rolled before accessing values", str(context.exception))

    def test_roll_values_range(self):
        """Test that dice roll values are between 1 and 6"""
        for _ in range(100):  # Test multiple rolls
            self.dice.roll()
            for value in self.dice.values:
                self.assertTrue(1 <= value <= 6)

    @patch("random.randint")
    def test_roll_uses_random(self, mock_randint):
        """Test that roll method uses random to generate values"""
        mock_randint.side_effect = [3, 5]
        self.dice.roll()
        self.assertEqual(self.dice.values, [3, 5])
        mock_randint.assert_called_with(1, 6)

    def test_is_doubles(self):
        """Test that is_doubles correctly identifies when both dice show the same value"""
        with patch("random.randint", side_effect=[4, 4]):
            self.dice.roll()
            self.assertTrue(self.dice.is_doubles())

        with patch("random.randint", side_effect=[2, 5]):
            self.dice.roll()
            self.assertFalse(self.dice.is_doubles())

    def test_get_moves(self):
        """Test that get_moves returns the correct number of moves"""
        # Normal roll (two different values)
        with patch("random.randint", side_effect=[2, 5]):
            self.dice.roll()
            moves = self.dice.get_moves()
            self.assertEqual(moves, [2, 5])

        # Doubles (should return four moves)
        with patch("random.randint", side_effect=[6, 6]):
            self.dice.roll()
            moves = self.dice.get_moves()
            self.assertEqual(moves, [6, 6, 6, 6])

    def test_initial_roll(self):
        """Test initial roll to determine who goes first"""
        # Different values
        with patch("random.randint", side_effect=[6, 2]):
            result = self.dice.initial_roll()
            self.assertEqual(result, (6, 2))
            self.assertEqual(self.dice.initial_values, [6, 2])
            self.assertFalse(self.dice.is_initial_tie())

    def test_initial_roll_tie(self):
        """Test that initial roll identifies ties correctly"""
        with patch("random.randint", side_effect=[3, 3]):
            result = self.dice.initial_roll()
            self.assertEqual(result, (3, 3))
            self.assertTrue(self.dice.is_initial_tie())

    def test_get_highest_roller(self):
        """Test that get_highest_roller returns the correct player"""
        # Player 1 wins (first value is higher)
        with patch("random.randint", side_effect=[6, 2]):
            self.dice.initial_roll()
            self.assertEqual(self.dice.get_highest_roller(), 1)

        # Player 2 wins (second value is higher)
        with patch("random.randint", side_effect=[3, 5]):
            self.dice.initial_roll()
            self.assertEqual(self.dice.get_highest_roller(), 2)

        # Tie (should return 0)
        with patch("random.randint", side_effect=[4, 4]):
            self.dice.initial_roll()
            self.assertEqual(self.dice.get_highest_roller(), 0)
