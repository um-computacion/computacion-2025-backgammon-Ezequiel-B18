"""Board class for backgammon game."""

from core.exceptions import InvalidPointError

# Constants for player IDs
EMPTY = 0
PLAYER_WHITE = 1
PLAYER_BLACK = 2

# Constants for board layout
NUM_POINTS = 24
WHITE_HOME_RANGE = range(0, 6)
BLACK_HOME_RANGE = range(18, 24)


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
        self.__points__ = [(EMPTY, 0) for _ in range(NUM_POINTS)]
        self.__bar__ = {PLAYER_WHITE: 0, PLAYER_BLACK: 0}
        self.__home__ = {PLAYER_WHITE: 0, PLAYER_BLACK: 0}

        if test_bearing_off:
            # Special setup for bearing off tests
            # All white checkers in home board (1-6, which is points 0-5 in 0-based)
            self.__points__[0] = (PLAYER_WHITE, 2)
            self.__points__[1] = (PLAYER_WHITE, 2)
            self.__points__[2] = (PLAYER_WHITE, 3)
            self.__points__[3] = (PLAYER_WHITE, 2)
            self.__points__[4] = (PLAYER_WHITE, 3)
            self.__points__[5] = (PLAYER_WHITE, 3)

            # All black checkers in their home board (19-24, which is points 18-23 in 0-based)
            self.__points__[18] = (PLAYER_BLACK, 2)
            self.__points__[19] = (PLAYER_BLACK, 2)
            self.__points__[20] = (PLAYER_BLACK, 3)
            self.__points__[21] = (PLAYER_BLACK, 2)
            self.__points__[22] = (PLAYER_BLACK, 3)
            self.__points__[23] = (PLAYER_BLACK, 3)
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
        if not 0 <= point <= NUM_POINTS - 1:
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
        if not 0 <= point <= NUM_POINTS - 1:
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
        if not (0 <= from_point < NUM_POINTS and 0 <= to_point < NUM_POINTS):
            raise InvalidPointError(
                from_point if not 0 <= from_point < NUM_POINTS else to_point
            )

        # Check if there are checkers on the bar that must be entered first
        if self.bar[player] > 0:
            return False

        # Check if the source point has checkers belonging to the player
        if self.points[from_point][0] != player or self.points[from_point][1] == 0:
            return False

        # Check movement direction based on player
        if (
            player == PLAYER_WHITE
        ):  # White moves from high points to low points (23 -> 0)
            if to_point >= from_point:
                return False  # White cannot move backwards (higher numbers)
        else:  # Black moves from low points to high points (0 -> 23)
            if to_point <= from_point:
                return False  # Black cannot move backwards (lower numbers)

        # Check if the target point is blocked by the opponent
        # A point is blocked if it has 2 or more checkers of the opponent
        target_player, target_count = self.points[to_point]
        if target_player != EMPTY and target_player != player and target_count >= 2:
            return False

        return True

    def setup_starting_positions(self):
        """Set up the standard backgammon starting positions."""
        # Clear all points first
        self.__points__ = [(EMPTY, 0) for _ in range(NUM_POINTS)]

        # White checkers (player 1) starting positions - need to bear off to 1-6
        # So they start from the far end (higher numbers)
        self.__points__[23] = (PLAYER_WHITE, 2)  # 2 white checkers on point 23
        self.__points__[12] = (PLAYER_WHITE, 5)  # 5 white checkers on point 12
        self.__points__[7] = (PLAYER_WHITE, 3)  # 3 white checkers on point 7
        self.__points__[5] = (PLAYER_WHITE, 5)  # 5 white checkers on point 5

        # Black checkers (player 2) starting positions - need to bear off to 19-24
        # So they start from the far end (lower numbers)
        self.__points__[0] = (PLAYER_BLACK, 2)  # 2 black checkers on point 0
        self.__points__[11] = (PLAYER_BLACK, 5)  # 5 black checkers on point 11
        self.__points__[16] = (PLAYER_BLACK, 3)  # 3 black checkers on point 16
        self.__points__[18] = (PLAYER_BLACK, 5)  # 5 black checkers on point 18

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
            self.points[from_point] = (EMPTY, 0)
        else:
            self.points[from_point] = (source_player, source_count - 1)

        # Handle normal target point
        target_player, target_count = self.points[to_point]
        if target_player in (EMPTY, player):
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

        # Validate entry points based on tests
        if (
            player == PLAYER_WHITE
        ):  # White enters from points 18-23 (19-24 in user terms)
            if point not in BLACK_HOME_RANGE:
                return False
        else:  # Black enters from points 0-5 (1-6 in user terms)
            if point not in WHITE_HOME_RANGE:
                return False

        # Check if point is blocked by opponent
        current_player, current_count = self.__points__[point]
        if current_player != EMPTY and current_player != player and current_count >= 2:
            return False

        # Handle hitting
        if current_player != EMPTY and current_player != player and current_count == 1:
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
        home_range = WHITE_HOME_RANGE if player == PLAYER_WHITE else BLACK_HOME_RANGE

        # Count checkers on board for this player
        checkers_on_board = 0
        checkers_in_home = 0

        for point_idx in range(NUM_POINTS):
            point_player, count = self.__points__[point_idx]
            if point_player == player:
                checkers_on_board += count
                if point_idx in home_range:
                    checkers_in_home += count

        # All on-board checkers must be in home board
        return checkers_on_board == checkers_in_home

    def bear_off(self, player, point):
        """Bear off a checker from the specified point."""
        home_range = WHITE_HOME_RANGE if player == PLAYER_WHITE else BLACK_HOME_RANGE
        if point not in home_range:
            return False

        # Check if there's a checker at this point
        current_player, current_count = self.__points__[point]
        if current_player != player or current_count == 0:
            return False

        # Remove checker from point
        new_count = current_count - 1
        if new_count == 0:
            self.__points__[point] = (EMPTY, 0)
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
        if self.home[PLAYER_WHITE] == 15:
            return PLAYER_WHITE
        if self.home[PLAYER_BLACK] == 15:
            return PLAYER_BLACK
        return EMPTY

    def to_dict(self):
        """Converts the Board object to a dictionary."""
        return {
            "points": self.points,
            "bar": self.bar,
            "home": self.home,
        }

    @staticmethod
    def from_dict(data):
        """Creates a Board object from a dictionary."""
        board = Board()
        board.points[:] = data["points"]
        # JSON keys are strings, so convert them back to integers
        board.bar.clear()
        board.bar.update({int(k): v for k, v in data["bar"].items()})
        board.home.clear()
        board.home.update({int(k): v for k, v in data["home"].items()})
        return board
