"""Dice class for backgammon game."""

import random
from core.exceptions import DiceNotRolledError, InvalidDiceValueError


class Dice:
    """
    Represents a pair of dice used in a backgammon game.
    Handles regular rolls, doubles detection, and initial roll to determine the first player.
    """

    def __init__(self):
        """Initialize two dice with default values of [0, 0]"""
        self.__values__ = [0, 0]
        self.initial_values = [0, 0]

    @property
    def values(self):
        """Get the current dice values."""
        if self.__values__ == [0, 0]:
            raise DiceNotRolledError("Dice must be rolled before accessing values")
        return self.__values__

    @property
    def rolled(self):
        """Check if the dice have been rolled."""
        return self.__values__ != [0, 0]

    def roll(self):
        """Roll both dice and store their values"""
        self.__values__ = [random.randint(1, 6), random.randint(1, 6)]
        # Validate the rolled values
        for value in self.__values__:
            if not 1 <= value <= 6:
                raise InvalidDiceValueError(value)
        return self.__values__

    def is_doubles(self):
        """Check if both dice show the same value"""
        return self.values[0] == self.values[1]

    def get_moves(self):
        """
        Get the available moves based on dice values.
        If doubles were rolled, each die value can be used four times.
        """
        if self.is_doubles():
            # For doubles, return the value four times
            return [self.values[0]] * 4
        return self.values.copy()

    def initial_roll(self):
        """
        Roll dice to determine who goes first.
        Each player rolls one die separately.
        Returns the values as [player1_roll, player2_roll].
        """
        player1_roll = random.randint(1, 6)
        player2_roll = random.randint(1, 6)
        self.initial_values = [player1_roll, player2_roll]
        return tuple(self.initial_values)

    def is_initial_tie(self):
        """Check if the initial roll resulted in a tie"""
        return self.initial_values[0] == self.initial_values[1]

    def get_highest_roller(self):
        """
        Get the player who rolled the highest value in the initial roll.
        Returns 1 if player 1 rolled higher, 2 if player 2 rolled higher, 0 if tie.
        """
        if self.initial_values[0] > self.initial_values[1]:
            return 1
        if self.initial_values[1] > self.initial_values[0]:
            return 2
        return 0
