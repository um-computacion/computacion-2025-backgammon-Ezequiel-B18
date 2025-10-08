"""Board class for backgammon game."""

from core.exceptions import InvalidPointError


class Board:
    """
    Represents a backgammon board.
    Handles the state of the board, moving checkers, and checking game conditions.
    """

    def __init__(self, test_bearing_off=False):
        """
        Initialize the backgammon board with the standard starting position.

        Args:
            test_bearing_off (bool): If True, set up a test position with
                                   all white checkers in home board
        """
        # Points are represented as tuples (player, count)
        # player: 0 = empty, 1 = white, 2 = black
        # count: number of checkers at that point
        self.__points__ = [(0, 0) for _ in range(24)]
        self.__bar__ = {1: 0, 2: 0}
        self.__home__ = {1: 0, 2: 0}

        if test_bearing_off:
            # Special setup for bearing off tests
            # All white checkers in home board
            self.__points__[18] = (1, 2)
            self.__points__[19] = (1, 2)
            self.__points__[20] = (1, 3)
            self.__points__[21] = (1, 2)
            self.__points__[22] = (1, 3)
            self.__points__[23] = (1, 3)

            # All black checkers in their home board
            self.__points__[0] = (2, 2)
            self.__points__[1] = (2, 2)
            self.__points__[2] = (2, 3)
            self.__points__[3] = (2, 2)
            self.__points__[4] = (2, 3)
            self.__points__[5] = (2, 3)
        else:
            # Use the new helper to set standard starting positions
            self.setup_starting_positions()

    @property
    def points(self):
        """View (mutable at element level) of board points (internal SSoT: __points__)."""
        return self.__points__

    @property
    def bar(self):  # pylint: disable=disallowed-name
        """Dictionary mapping player -> number of checkers on the bar."""
        return self.__bar__

    @property
    def home(self):
        """Dictionary mapping player -> number of checkers borne off (home)."""
        return self.__home__

    def get_player_at_point(self, point):
        """
        Get the player who has checkers at the given point.

        Args:
            point (int): Point index (0-23)

        Returns:
            int: Player number (0 if empty, 1 for white, 2 for black)
        """
        if not 0 <= point <= 23:
            raise InvalidPointError(point)
        return self.points[point][0]

    def get_checkers_count(self, point):
        """
        Get the number of checkers at the given point.

        Args:
            point (int): Point index (0-23)

        Returns:
            int: Number of checkers at the point
        """
        if not 0 <= point <= 23:
            raise InvalidPointError(point)
        return self.points[point][1]

    def is_valid_move(self, player, from_point, to_point):
        """
        Check if a move is valid.

        Args:
            player (int): Player making the move (1 for white, 2 for black)
            from_point (int): Starting point index (0-23)
            to_point (int): Target point index (0-23)

        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Validate point indices
        if not 0 <= from_point <= 23:
            raise InvalidPointError(from_point)
        if not 0 <= to_point <= 23:
            raise InvalidPointError(to_point)

        # Check if there are checkers on the bar that must be entered first
        if self.bar[player] > 0:
            return False

        # Check if the source point has checkers belonging to the player
        if self.points[from_point][0] != player or self.points[from_point][1] == 0:
            return False

        # Check if the target point is blocked by the opponent
        # A point is blocked if it has 2 or more checkers of the opponent
        target_player, target_count = self.points[to_point]
        if target_player != 0 and target_player != player and target_count >= 2:
            return False

        return True

    def setup_starting_positions(self):
        """Set up the standard backgammon starting positions."""
        # Clear all points first
        self.__points__ = [(0, 0) for _ in range(24)]

        # White checkers (player 1) starting positions
        self.__points__[0] = (1, 2)  # 2 white checkers on point 0
        self.__points__[11] = (1, 5)  # 5 white checkers on point 11
        self.__points__[16] = (1, 3)  # 3 white checkers on point 16
        self.__points__[18] = (1, 5)  # 5 white checkers on point 18

        # Black checkers (player 2) starting positions
        self.__points__[23] = (2, 2)  # 2 black checkers on point 23
        self.__points__[12] = (2, 5)  # 5 black checkers on point 12
        self.__points__[7] = (2, 3)  # 3 black checkers on point 7
        self.__points__[5] = (2, 5)  # 5 black checkers on point 5

    def move_checker(self, player, from_point, to_point):
        """
        Move a checker and return a structured event describing what happened.
        Returns dict: {'moved': bool, 'hit': bool, 'hit_player': int or None,
                      'borne_off': bool}
        """
        event = {"moved": False, "hit": False, "hit_player": None, "borne_off": False}

        try:
            if not self.is_valid_move(player, from_point, to_point):
                return event
        except InvalidPointError:  # pylint: disable=try-except-raise
            # Re-raise point errors to be caught by Game
            raise

        # Remove checker from source point
        source_player, source_count = self.points[from_point]
        if source_count == 1:
            self.points[from_point] = (0, 0)
        else:
            self.points[from_point] = (source_player, source_count - 1)

        # Handle target point
        target_player, target_count = self.points[to_point]
        if target_player in (0, player):
            # Empty point or same player, add checker
            self.points[to_point] = (player, target_count + 1)
        elif target_count == 1:
            # Hit opponent's blot
            self.points[to_point] = (player, 1)
            self.bar[target_player] += 1
            event["hit"] = True
            event["hit_player"] = target_player

        event["moved"] = True
        return event

    def enter_from_bar(self, player, point):
        """Enter a checker from the bar to the specified point."""
        if self.bar[player] == 0:
            return False

        # Validate entry points
        if player == 1:  # White enters from points 0-5
            if not 0 <= point <= 5:
                return False
        else:  # Black enters from points 18-23
            if not 18 <= point <= 23:
                return False

        # Check if point is blocked by opponent
        current_player, current_count = self.__points__[point]
        if current_player != 0 and current_player != player and current_count >= 2:
            return False

        # Handle hitting
        if current_player != 0 and current_player != player and current_count == 1:
            # Hit opponent checker
            self.bar[current_player] += 1
            self.__points__[point] = (player, 1)
        elif current_player == player:
            # Stack on own checker
            self.__points__[point] = (player, current_count + 1)
        else:
            # Empty point
            self.__points__[point] = (player, 1)

        # Remove from bar
        self.bar[player] -= 1
        return True

    def all_checkers_in_home_board(self, player):
        """Check if all of a player's checkers are in their home board."""
        if player == 1:  # White player
            home_range = range(18, 24)
        else:  # Black player
            home_range = range(0, 6)

        # Count checkers on board for this player
        checkers_on_board = 0
        checkers_in_home = 0

        for point_idx in range(24):
            point_player, count = self.__points__[point_idx]
            if point_player == player:
                checkers_on_board += count
                if point_idx in home_range:
                    checkers_in_home += count

        # All on-board checkers must be in home board
        return checkers_on_board == checkers_in_home

    def bear_off(
        self, player, point
    ):  # pylint: disable=too-many-return-statements,too-many-branches
        """Bear off a checker from the specified point."""
        # Validate point is in player's home board
        if player == 1:  # White
            if not 18 <= point <= 23:
                return False
        else:  # Black
            if not 0 <= point <= 5:
                return False

        # Check if all checkers are in home board
        if not self.all_checkers_in_home_board(player):
            return False

        # Check if there's a checker at this point
        current_player, current_count = self.__points__[point]
        if current_player != player or current_count == 0:
            return False

        # Check if there are checkers on higher points (for bearing off validation)
        if player == 1:  # White
            for higher_point in range(point + 1, 24):
                higher_player, higher_count = self.__points__[higher_point]
                if higher_player == player and higher_count > 0:
                    return False
        else:  # Black
            for higher_point in range(0, point):
                higher_player, higher_count = self.__points__[higher_point]
                if higher_player == player and higher_count > 0:
                    return False

        # Remove checker from point
        new_count = current_count - 1
        if new_count == 0:
            self.__points__[point] = (0, 0)
        else:
            self.__points__[point] = (player, new_count)

        # Add to home
        self.home[player] += 1

        return True

    def check_winner(self):
        """
        Check if there is a winner.

        Returns:
            int: 0 if no winner, 1 if white wins, 2 if black wins
        """
        if self.home[1] == 15:
            return 1
        if self.home[2] == 15:
            return 2
        return 0
