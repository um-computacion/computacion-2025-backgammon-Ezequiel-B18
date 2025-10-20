"""Game orchestrator class for backgammon."""

from core.board import Board
from core.dice import Dice
from core.player import Player, PlayerColor
from core.checker import CheckerState
from core.exceptions import (
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
)


class Game:
    """
    Orchestrator for a backgammon game.
    - Follows SOLID: Game orchestrates, Board/Dice/Player handle their own responsibilities.
    - Provides testable, small methods for TDD.
    """

    def __init__(
        self,
        player1_name="White",
        player2_name="Black",
        test_bearing_off=False,
        *,  # Force keyword-only arguments for dependency injection
        board=None,
        dice=None,
        player1=None,
        player2=None,
    ):
        """
        Initialize the game with dependency injection support.

        Args:
            player1_name: Name for player 1 (backward compatibility)
            player2_name: Name for player 2 (backward compatibility)
            test_bearing_off: For backwards compatibility, creates test board
            board: Board instance (if None, creates new Board)
            dice: Dice instance (if None, creates new Dice)
            player1: Player 1 instance (if None, creates new Player with player1_name)
            player2: Player 2 instance (if None, creates new Player with player2_name)
        """
        # Use dependency injection or create defaults
        self.__board__ = (
            board if board is not None else Board(test_bearing_off=test_bearing_off)
        )
        self.__dice__ = dice if dice is not None else Dice()
        self.__player1__ = (
            player1 if player1 is not None else Player(player1_name, PlayerColor.WHITE)
        )
        self.__player2__ = (
            player2 if player2 is not None else Player(player2_name, PlayerColor.BLACK)
        )

        self.current_player = None  # Will be set after initial roll
        self.other_player = None
        self.__game_initialized__ = False

    @property
    def board(self):
        """Get the game board."""
        return self.__board__

    @property
    def dice(self):
        """Get the game dice."""
        return self.__dice__

    @property
    def player1(self):
        """Get player 1."""
        return self.__player1__

    @property
    def player2(self):
        """Get player 2."""
        return self.__player2__

    def setup_game(self):
        """Use Board as source of truth for starting positions and sync player checkers."""
        # Board sets up points
        self.board.setup_starting_positions()
        # Players get checker.position set (for convenience / tests)
        self.player1.distribute_checkers(self.board)
        self.player2.distribute_checkers(self.board)
        # Game reconciles Checker objects to match Board
        self.sync_checkers()
        self.__game_initialized__ = True

    def sync_checkers(self):
        """
        Make Board the source of truth and update Player.checkers states
        accordingly. Deterministic process:
        1) Mark appropriate number of checkers as BORNE_OFF from the end
        2) Mark checkers on the BAR
        3) Assign ON_BOARD positions from board.points in increasing order
        """
        for player_obj, player_id in ((self.player1, 1), (self.player2, 2)):
            self._reset_checker_states(player_obj)
            self._assign_borne_off_checkers(player_obj, player_id)
            self._assign_bar_checkers(player_obj, player_id)
            self._assign_board_positions(player_obj, player_id)

    def _reset_checker_states(self, player_obj):
        """Reset all checker positions and set default state to ON_BOARD."""
        for checker in player_obj.checkers:
            checker.position = None
            checker.state = CheckerState.ON_BOARD

    def _assign_borne_off_checkers(self, player_obj, player_id):
        """Set last N checkers as borne off."""
        borne_off_count = self.board.home.get(player_id, 0)
        if borne_off_count > 0:
            counter = borne_off_count
            for checker in reversed(player_obj.checkers):
                if counter == 0:
                    break
                checker.state = CheckerState.BORNE_OFF
                checker.position = None
                counter -= 1

    def _assign_bar_checkers(self, player_obj, player_id):
        """Set first available (non-borne-off) checkers to ON_BAR."""
        bar_count = self.board.bar.get(player_id, 0)
        if bar_count > 0:
            counter = bar_count
            for checker in player_obj.checkers:
                if counter == 0:
                    break
                if checker.state == CheckerState.BORNE_OFF:
                    continue
                checker.state = CheckerState.ON_BAR
                checker.position = None
                counter -= 1

    def _assign_board_positions(self, player_obj, player_id):
        """Assign ON_BOARD positions according to board.points counts."""
        for point_idx in range(24):
            pt_player, pt_count = self.board.points[point_idx]
            if pt_player != player_id or pt_count == 0:
                continue
            need = pt_count
            for checker in player_obj.checkers:
                if need == 0:
                    break
                if checker.state == CheckerState.ON_BOARD and checker.position is None:
                    checker.position = point_idx
                    need -= 1

    def initial_roll_until_decided(self):
        """
        Perform initial rolls until a non-tie decides who starts.
        Sets current_player and other_player.
        """
        while True:
            self.dice.initial_roll()
            winner = self.dice.get_highest_roller()
            if winner == 1:
                self.current_player = self.player1
                self.other_player = self.player2
                return 1
            if winner == 2:
                self.current_player = self.player2
                self.other_player = self.player1
                return 2
            # else tie -> repeat

    def start_turn(self):
        """
        Roll dice for the current player and start their turn
        (sets remaining moves).
        """
        if not self.__game_initialized__:
            raise GameNotInitializedError(
                "Game must be initialized before starting turns"
            )

        if self.current_player is None:
            raise GameNotInitializedError(
                "Current player not set. Call initial_roll_until_decided() first."
            )

        if self.is_game_over():
            raise GameAlreadyOverError("Cannot start turn when game is over")

        self.dice.roll()
        self.current_player.start_turn(self.dice)

    def apply_move(self, from_point, to_point):
        """
        Apply a move for the current player using the board.
        Validates that the move uses available dice values correctly.
        Returns True if move succeeded, False otherwise.
        """
        if not self.__game_initialized__:
            raise GameNotInitializedError(
                "Game must be initialized before making moves"
            )

        if self.current_player is None:
            raise InvalidPlayerTurnError("No current player set")

        if self.is_game_over():
            raise GameAlreadyOverError("Cannot make moves when game is over")

        if self.current_player.remaining_moves <= 0:
            raise InvalidPlayerTurnError(
                f"Player {self.current_player.name} has no remaining moves"
            )

        pid = self.current_player.player_id

        if from_point == "bar":
            if self.board.bar[pid] == 0:
                raise InvalidMoveError(
                    "bar", to_point, "Player has no checkers on the bar."
                )

            if pid == 1:  # White enters on points 19-24 (18-23)
                move_distance = 25 - (to_point + 1)
            else:  # Black enters on points 1-6 (0-5)
                move_distance = to_point + 1

            if not self.current_player.can_use_dice_for_move(move_distance):
                raise InvalidMoveError(
                    "bar", to_point, "No available dice for this move."
                )

            success = self.board.enter_from_bar(pid, to_point)
            if not success:
                raise InvalidMoveError(
                    "bar", to_point, "Board rejected the move from the bar."
                )

            self.current_player.use_dice_for_move(move_distance)
            self.sync_checkers()

            if self.current_player.remaining_moves <= 0:
                self.current_player.end_turn()
                self.switch_players()

            return True

        # Calculate move distance for moves on the board
        if pid == 1:  # White moves from high to low
            move_distance = from_point - to_point
        else:  # Black moves from low to high
            move_distance = to_point - from_point

        # Validate that move distance matches available dice
        if not self.current_player.can_use_dice_for_move(move_distance):
            return (
                False  # Invalid dice usage, return False instead of raising exception
            )

        try:
            event = self.board.move_checker(pid, from_point, to_point)
        except Exception as e:
            # Re-raise board exceptions as InvalidMoveError for game context
            raise InvalidMoveError(from_point, to_point, str(e)) from e

        if not event.get("moved", False):
            return False

        # Consume the appropriate dice values for this move
        if not self.current_player.use_dice_for_move(move_distance):
            # This shouldn't happen if can_use_dice_for_move returned True
            raise InvalidMoveError(
                from_point, to_point, "Failed to consume dice values"
            )

        # If a hit occurred, Game could update player/checker states
        # (we rely on sync_checkers to reconcile)
        self.sync_checkers()

        # If a bear-off event is to be supported by Board later,
        # handle 'borne_off' here.
        if self.current_player.remaining_moves <= 0:
            self.current_player.end_turn()
            self.switch_players()
        elif not self.has_any_valid_moves():
            self.current_player.end_turn()
            self.switch_players()

        return True

    def switch_players(self):
        """Switch current and other players."""
        if not self.__game_initialized__:
            raise GameNotInitializedError(
                "Game must be initialized before switching players"
            )

        self.current_player, self.other_player = self.other_player, self.current_player

    def is_game_over(self):
        """Return True if a player has borne off all checkers."""
        return self.board.check_winner() != 0

    def get_winner(self):
        """Return player object of the winner or None."""
        winner_id = self.board.check_winner()
        if winner_id == 1:
            return self.player1
        if winner_id == 2:
            return self.player2
        return None

    def get_valid_moves(self, from_point):
        """
        Calculates the valid moves for a given checker.

        Args:
            from_point (int or str): The starting point of the checker, either an integer
                                     representing a point on the board or the string "bar".

        Returns:
            list: A list of valid destination points, which can include integers for
                  points on the board or the string "bear_off".
        """
        valid_moves = []
        if not self.current_player or not self.current_player.available_moves:
            return valid_moves

        player_id = self.current_player.player_id
        opponent_id = 2 if player_id == 1 else 1
        available_dice = set(self.current_player.available_moves)

        if from_point == "bar":
            if self.board.bar[player_id] > 0:
                for dice_value in available_dice:
                    if player_id == 1:  # White enters on points 19-24 (18-23)
                        to_point = 24 - dice_value
                    else:  # Black enters on points 1-6 (0-5)
                        to_point = dice_value - 1

                    if 0 <= to_point < 24:
                        target_player, target_count = self.board.points[to_point]
                        if target_player != opponent_id or target_count < 2:
                            valid_moves.append(to_point)
            return list(set(valid_moves))

        if not isinstance(from_point, int) or not (0 <= from_point < 24):
            return []

        if self.board.bar[player_id] > 0:
            return []

        if self.board.points[from_point][0] != player_id:
            return []

        for dice_value in available_dice:
            if player_id == 1:
                to_point = from_point - dice_value
            else:
                to_point = from_point + dice_value

            if 0 <= to_point < 24 and self.board.is_valid_move(
                player_id, from_point, to_point
            ):
                if self.board.all_checkers_in_home_board(player_id):
                    home_board_range = range(6) if player_id == 1 else range(18, 24)
                    if to_point in home_board_range:
                        valid_moves.append(to_point)
                else:
                    valid_moves.append(to_point)

        if self.board.all_checkers_in_home_board(player_id):
            if player_id == 1:
                home_board_range = range(6)
                required_dice = from_point + 1
            else:
                home_board_range = range(18, 24)
                required_dice = 24 - from_point

            if from_point in home_board_range:
                if self.current_player.can_use_dice_for_move(required_dice):
                    valid_moves.append("bear_off")
                else:
                    # Check if a higher dice roll can be used
                    larger_dice_available = any(
                        d > required_dice for d in available_dice
                    )
                    if larger_dice_available:
                        # Check if this is the highest checker
                        is_highest = True
                        if player_id == 1:
                            for p in range(from_point + 1, 6):
                                if self.board.points[p][0] == player_id:
                                    is_highest = False
                                    break
                        else:  # Player 2
                            for p in range(18, from_point):
                                if self.board.points[p][0] == player_id:
                                    is_highest = False
                                    break
                        if is_highest:
                            valid_moves.append("bear_off")

        return list(set(valid_moves))

    def apply_bear_off_move(self, from_point):
        """
        Applies a bear-off move for the current player.

        Args:
            from_point (int): The point from which to bear off the checker.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if not self.board.all_checkers_in_home_board(self.current_player.player_id):
            raise InvalidMoveError(
                from_point, "off", "Not all checkers are in home board."
            )

        player_id = self.current_player.player_id

        if player_id == 1:
            required_dice = from_point + 1
        else:
            required_dice = 24 - from_point

        dice_to_use = 0
        if self.current_player.can_use_dice_for_move(required_dice):
            dice_to_use = required_dice
        else:
            available_dice = self.current_player.available_moves
            larger_dice = [d for d in available_dice if d > required_dice]
            if larger_dice:
                is_highest_checker = True
                if player_id == 1:
                    for p in range(from_point + 1, 6):
                        if self.board.points[p][0] == player_id:
                            is_highest_checker = False
                            break
                else:
                    for p in range(18, from_point):
                        if self.board.points[p][0] == player_id:
                            is_highest_checker = False
                            break

                if is_highest_checker:
                    dice_to_use = min(larger_dice)

        if dice_to_use == 0:
            raise InvalidMoveError(
                from_point, "off", "No valid dice available for bearing off."
            )

        success = self.board.bear_off(player_id, from_point)
        if not success:
            raise InvalidMoveError(from_point, "off", "Board rejected bear off.")

        self.current_player.use_dice_for_move(dice_to_use)
        self.sync_checkers()

        if self.current_player.remaining_moves <= 0:
            self.current_player.end_turn()
            self.switch_players()
        elif not self.has_any_valid_moves():
            self.current_player.end_turn()
            self.switch_players()

        return True

    def has_any_valid_moves(self):
        """
        Checks if the current player has any valid moves with the current dice.

        Returns:
            bool: True if there is at least one valid move, False otherwise.
        """
        player_id = self.current_player.player_id

        # If checkers are on the bar, the only valid moves are to enter the board.
        if self.board.bar[player_id] > 0:
            for dice_value in set(self.current_player.available_moves):
                if len(self.get_valid_moves("bar")) > 0:
                    return True
            return False

        # Check for any valid moves from any point on the board.
        for point_idx in range(24):
            if self.board.points[point_idx][0] == player_id:
                # Check for standard moves
                if self.get_valid_moves(point_idx):
                    return True
                # Check for bear-off moves
                if self.board.all_checkers_in_home_board(
                    player_id
                ) and self.is_valid_bear_off_move(point_idx):
                    return True

        return False

    def is_valid_bear_off_move(self, from_point):
        """
        Checks if a bear-off move is valid for the selected checker.

        Args:
            from_point (int or str): The point of the checker to bear off.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if not isinstance(from_point, int):
            return False

        if not self.board.all_checkers_in_home_board(self.current_player.player_id):
            return False

        player_id = self.current_player.player_id

        if player_id == 1:
            required_dice = from_point + 1
        else:
            required_dice = 24 - from_point

        if self.current_player.can_use_dice_for_move(required_dice):
            return True

        available_dice = self.current_player.available_moves
        larger_dice = [d for d in available_dice if d > required_dice]
        if larger_dice:
            is_highest_checker = True
            if player_id == 1:
                for p in range(from_point + 1, 6):
                    if self.board.points[p][0] == player_id:
                        is_highest_checker = False
                        break
            else:
                for p in range(18, from_point):
                    if self.board.points[p][0] == player_id:
                        is_highest_checker = False
                        break

            if is_highest_checker:
                return True

        return False
