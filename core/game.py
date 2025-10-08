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
        player1_name="White",  # First positional for backward compatibility
        player2_name="Black",  # Second positional for backward compatibility
        test_bearing_off=False,  # Third positional for backward compatibility
        board=None,  # Dependency injection parameters as keyword-only
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
        Accepts the event dict returned by board.move_checker.
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

        try:
            event = self.board.move_checker(pid, from_point, to_point)
        except Exception as e:
            # Re-raise board exceptions as InvalidMoveError for game context
            raise InvalidMoveError(from_point, to_point, str(e)) from e

        if not event.get("moved", False):
            return False

        # reduce player's remaining moves
        self.current_player.use_move()

        # If a hit occurred, Game could update player/checker states
        # (we rely on sync_checkers to reconcile)
        self.sync_checkers()

        # If a bear-off event is to be supported by Board later,
        # handle 'borne_off' here.
        if self.current_player.remaining_moves <= 0:
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
