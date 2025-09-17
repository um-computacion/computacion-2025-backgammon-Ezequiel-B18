from core.board import Board
from core.dice import Dice
from core.player import Player, PlayerColor
from core.checker import CheckerState


class Game:
    """
    Orchestrator for a backgammon game.
    - Follows SOLID: Game orchestrates, Board/Dice/Player handle their own responsibilities.
    - Provides testable, small methods for TDD.
    """

    def __init__(
        self, player1_name="White", player2_name="Black", test_bearing_off=False
    ):
        self._board = Board(test_bearing_off=test_bearing_off)
        self._dice = Dice()
        self._player1 = Player(player1_name, PlayerColor.WHITE)
        self._player2 = Player(player2_name, PlayerColor.BLACK)
        self.current_player = None  # Will be set after initial roll
        self.other_player = None

    @property
    def board(self):
        return self._board

    @property
    def dice(self):
        return self._dice

    @property
    def player1(self):
        return self._player1

    @property
    def player2(self):
        return self._player2

    def setup_game(self):
        """Use Board as source of truth for starting positions and sync player checkers."""
        # Board sets up points
        self.board.setup_starting_positions()
        # Players get checker.position set (for convenience / tests)
        self.player1.distribute_checkers(self.board)
        self.player2.distribute_checkers(self.board)
        # Game reconciles Checker objects to match Board
        self.sync_checkers()

    def sync_checkers(self):
        """
        Make Board the source of truth and update Player.checkers states accordingly.
        Deterministic process:
        1) Mark appropriate number of checkers as BORNE_OFF from the end of the list
        2) Mark checkers on the BAR
        3) Assign ON_BOARD positions from board.points in increasing point order
        """
        for player_obj, player_id in ((self.player1, 1), (self.player2, 2)):
            # Reset positions and default state to ON_BOARD; we'll override BORNE_OFF/ON_BAR below
            for c in player_obj.checkers:
                c.position = None
                c.state = CheckerState.ON_BOARD

            # 1) BORNE_OFF: set last N checkers as borne off
            borne_off_count = self.board.home.get(player_id, 0)
            if borne_off_count > 0:
                counter = borne_off_count
                for c in reversed(player_obj.checkers):
                    if counter == 0:
                        break
                    c.state = CheckerState.BORNE_OFF
                    c.position = None
                    counter -= 1

            # 2) ON_BAR: set first available (non-borne-off) checkers to ON_BAR
            bar_count = self.board.bar.get(player_id, 0)
            if bar_count > 0:
                counter = bar_count
                for c in player_obj.checkers:
                    if counter == 0:
                        break
                    if c.state == CheckerState.BORNE_OFF:
                        continue
                    c.state = CheckerState.ON_BAR
                    c.position = None
                    counter -= 1

            # 3) ON_BOARD: assign positions according to board.points counts
            # Iterate points deterministically 0..23
            for point_idx in range(24):
                pt_player, pt_count = self.board.points[point_idx]
                if pt_player != player_id or pt_count == 0:
                    continue
                need = pt_count
                for c in player_obj.checkers:
                    if need == 0:
                        break
                    if c.state == CheckerState.ON_BOARD and c.position is None:
                        c.position = point_idx
                        need -= 1

    def initial_roll_until_decided(self):
        """Perform initial rolls until a non-tie decides who starts. Sets current_player and other_player."""
        while True:
            self.dice.initial_roll()
            winner = self.dice.get_highest_roller()
            if winner == 1:
                self.current_player = self.player1
                self.other_player = self.player2
                return 1
            elif winner == 2:
                self.current_player = self.player2
                self.other_player = self.player1
                return 2
            # else tie -> repeat

    def start_turn(self):
        """Roll dice for the current player and start their turn (sets remaining moves)."""
        if self.current_player is None:
            raise RuntimeError(
                "Current player not set. Call initial_roll_until_decided() first."
            )
        self.dice.roll()
        self.current_player.start_turn(self.dice)

    def apply_move(self, from_point, to_point):
        """
        Apply a move for the current player using the board. Accepts the event dict returned by board.move_checker.
        Returns True if move succeeded, False otherwise.
        """
        if self.current_player is None:
            return False
        pid = self.current_player.player_id
        event = self.board.move_checker(pid, from_point, to_point)

        if not event.get("moved", False):
            return False

        # reduce player's remaining moves if possible
        self.current_player.use_move()
        # If a hit occurred, Game could update player/checker states (we rely on sync_checkers to reconcile)
        self.sync_checkers()

        # If a bear-off event is to be supported by Board later, handle 'borne_off' here.
        if self.current_player.remaining_moves <= 0:
            self.current_player.end_turn()
            self.switch_players()

        return True

    def switch_players(self):
        """Switch current and other players."""
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
