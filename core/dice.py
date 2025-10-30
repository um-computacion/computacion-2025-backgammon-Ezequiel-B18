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
        self.__initial_values__ = [0, 0]

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

    @property
    def initial_values(self):
        """Get the initial roll values."""
        return self.__initial_values__

    @initial_values.setter
    def initial_values(self, value):
        """Set the initial roll values."""
        self.__initial_values__ = value

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
        self.__initial_values__ = [player1_roll, player2_roll]
        return tuple(self.__initial_values__)

    def is_initial_tie(self):
        """Check if the initial roll resulted in a tie"""
        return self.__initial_values__[0] == self.__initial_values__[1]

    def get_highest_roller(self):
        """
        Get the player who rolled the highest value in the initial roll.
        Returns 1 if player 1 rolled higher, 2 if player 2 rolled higher, 0 if tie.
        """
        if self.__initial_values__[0] > self.__initial_values__[1]:
            return 1
        if self.__initial_values__[1] > self.__initial_values__[0]:
            return 2
        return 0
    
    def to_dict(self):
        """Converts the Dice object to a dictionary."""
        return {
            "values": self.__values__,
            "initial_values": self.__initial_values__,
        }

    @staticmethod
    def from_dict(data):
        """Creates a Dice object from a dictionary."""
        dice = Dice()
        dice.__values__ = data["values"]
        dice.__initial_values__ = data["initial_values"]
        return dice
