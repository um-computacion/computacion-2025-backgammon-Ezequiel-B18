"""Command Line Interface for Backgammon game.

SOLID Principles Applied:
- SRP: Methods grouped by single responsibilities
- ISP: Focused method interfaces
- DIP: Depends on Game abstraction, not concrete implementations
"""

# pylint: disable=too-many-branches,too-many-statements

from core.game import Game
from core.exceptions import (
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
    NoMovesRemainingError,
    GameQuitException,
)


class BackgammonCLI:
    """
    Command Line Interface for playing Backgammon.

    Organized by SOLID principles:
    - Game Flow Control: start_game(), game_loop()
    - User Input: _get_player_names(), handle_player_move()
    - Display: display_*() methods (grouped together)
    - Setup: _setup_initial_game()
    """

    def __init__(self):
        """Initialize the CLI."""
        self.__game__ = None
        self.__player1_name__ = None
        self.__player2_name__ = None

    @property
    def game(self):
        """Get the game instance."""
        return self.__game__

    @game.setter
    def game(self, value):
        """Set the game instance."""
        self.__game__ = value

    @property
    def player1_name(self):
        """Get player 1 name."""
        return self.__player1_name__

    @player1_name.setter
    def player1_name(self, value):
        """Set player 1 name."""
        self.__player1_name__ = value

    @property
    def player2_name(self):
        """Get player 2 name."""
        return self.__player2_name__

    @player2_name.setter
    def player2_name(self, value):
        """Set player 2 name."""
        self.__player2_name__ = value

    # =============================================================================
    # GAME FLOW CONTROL (SRP: Game orchestration responsibility)
    # =============================================================================

    def start_game(self):
        """Start a new backgammon game with player setup."""
        self.display_welcome()
        self._get_player_names()
        self._setup_initial_game()
        self._display_game_instructions()
        self.game_loop()

    def game_loop(self):  # pylint: disable=too-many-branches,too-many-statements
        """Main game loop handling turns and moves."""
        try:  # pylint: disable=too-many-branches,too-many-statements
            while not self.game.is_game_over():
                try:
                    self._execute_player_turn()
                    # Player switching is now handled automatically by apply_move()
                    # when remaining_moves reaches 0

                except (
                    GameNotInitializedError,
                    InvalidPlayerTurnError,
                    GameAlreadyOverError,
                    InvalidMoveError,
                ) as e:
                    print(f"Error: {e}")
                    continue

        except GameQuitException:
            print("Game ended by player.")
            return

        # Game over
        self.display_game_over()

    def _execute_player_turn(self):
        """Execute a single player turn."""
        self.display_board()
        self.display_current_player_info()

        # Start turn (roll dice)
        input(f"\n{self.game.current_player.name}, press Enter to roll dice...")
        self.game.start_turn()

        self.display_dice_roll()
        self.display_available_moves()

        # Handle moves until turn is over
        while self.game.current_player.remaining_moves > 0:
            # Check if any legal moves are possible
            if not self.game.has_any_valid_moves():
                print(
                    f"\n{self.game.current_player.name} has no legal moves available."
                )
                print("Skipping turn...")
                self.game.current_player.end_turn()
                self.game.switch_players()
                break

            self.handle_player_move()

    # =============================================================================
    # GAME SETUP (SRP: Initial game configuration responsibility)
    # =============================================================================

    def _get_player_names(self):
        """Get player names from user input."""
        self.player1_name = input("Enter Player 1 (White) name: ").strip() or "White"
        self.player2_name = input("Enter Player 2 (Black) name: ").strip() or "Black"

    def _setup_initial_game(self):
        """Setup the game and handle initial roll."""
        # Initialize game
        self.game = Game(self.player1_name, self.player2_name)
        print(f"\n{self.player1_name} (White) vs {self.player2_name} (Black)")
        print("Setting up the board...")

        # Setup game
        self.game.setup_game()

        # Initial roll to determine who goes first
        print("\nINITIAL ROLL - Each player rolls one die to determine who goes first!")
        winner = self.game.initial_roll_until_decided()
        print(f"{self.player1_name} rolls: {self.game.dice.initial_values[0]}")
        print(f"{self.player2_name} rolls: {self.game.dice.initial_values[1]}")

        if winner == 1:
            print(f"{self.player1_name} (White) goes first!")
        else:
            print(f"{self.player2_name} (Black) goes first!")

    def _display_game_instructions(self):
        """Display game instructions to players."""
        print("\n" + "=" * 60)
        print("HOW TO PLAY:")
        print("- Points are numbered 1-24 (see board below)")
        print("- White moves from point 24 towards 1, Black from 1 towards 24")
        print("- Enter moves as 'from_point to_point' (e.g., '1 5')")
        print("- Enter from bar: 'bar to_point' (e.g., 'bar 5')")
        print("- Bear off: 'from_point off' (e.g., '24 off')")
        print("- You must use all dice values in your turn")
        print("- Hit opponent by landing on their single checker")
        print(
            "- Bear off when all checkers are in your home board "
            "(points 1-6 for White, 19-24 for Black)"
        )
        print("- Type 'q' to quit, 'h' for help")
        print("=" * 60)

    # =============================================================================
    # USER INPUT HANDLING (SRP: Input parsing and move validation responsibility)
    # =============================================================================

    def handle_player_move(self):
        """Handle a single move from the current player."""
        while True:
            try:
                move_input = (
                    input(
                        "Enter move (from_point to_point) or 'h' for help, 'q' to quit: "
                    )
                    .strip()
                    .lower()
                )

                if move_input == "q":
                    raise GameQuitException()
                if move_input == "h":
                    self.display_help()
                    continue

                # Parse move
                parts = move_input.split()
                if len(parts) != 2:
                    print(
                        "Invalid input. Please enter two numbers separated by space "
                        "(e.g., '1 5'), bear off with 'off' (e.g., '24 off'), "
                        "or enter from bar with 'bar' (e.g., 'bar 5')."
                    )
                    continue

                # Handle entering from bar
                if parts[0].lower() == "bar":
                    try:
                        to_point = int(parts[1])

                        # Validate range (user enters 1-24, we convert to 0-23)
                        if not 1 <= to_point <= 24:
                            print("Invalid point. Points must be between 1-24.")
                            continue

                        to_point -= 1  # Convert to 0-based

                        self.game.apply_move("bar", to_point)
                        break
                    except ValueError:
                        print(
                            "Invalid input. Enter 'bar' followed by a point number (e.g., 'bar 5')."
                        )
                        continue

                try:
                    from_point = int(parts[0])

                    # Handle bearing off
                    if parts[1].lower() == "off":
                        # Validate range (user enters 1-24, we convert to 0-23)
                        if not 1 <= from_point <= 24:
                            print("Invalid point. Points must be between 1-24.")
                            continue

                        from_point -= 1  # Convert to 0-based

                        # Set to_point beyond board for bearing off
                        if self.game.current_player.player_id == 1:  # White
                            to_point = 24  # Beyond the board
                        else:  # Black
                            to_point = -1  # Beyond the board
                    else:
                        to_point = int(parts[1])

                        # Validate range (user enters 1-24, we convert to 0-23)
                        if not (1 <= from_point <= 24 and 1 <= to_point <= 24):
                            print("Invalid points. Points must be between 1-24.")
                            continue

                        from_point -= 1  # Convert to 0-based
                        to_point -= 1

                except ValueError:
                    print(
                        "Invalid input. Please enter valid numbers or 'off' for bearing off."
                    )
                    continue

                # Attempt the move
                if parts[1].lower() == "off":
                    self.game.apply_bear_off_move(from_point)
                    break
                else:
                    # Normal move - apply_move now handles dice validation
                    success = self.game.apply_move(from_point, to_point)
                    if success:
                        move_distance = abs(to_point - from_point)
                        print(
                            f"Move successful: {from_point + 1} → {to_point + 1} "
                            f"(distance: {move_distance})"
                        )
                        break
                    print("Invalid move. Try again or check the board.")

            except (InvalidMoveError, NoMovesRemainingError) as e:
                print(f"Move error: {e}")
                continue

    # =============================================================================
    # DISPLAY METHODS (SRP: User interface and visualization responsibility)
    # =============================================================================

    def display_welcome(self):
        """Display welcome message and basic rules."""
        print("WELCOME TO BACKGAMMON!")
        print("=" * 60)
        print("Backgammon is a classic board game of strategy and luck.")
        print("The goal is to move all your checkers around the board")
        print("and bear them off before your opponent does!")
        print("=" * 60)

    def display_board(self):
        """Display the current board state in a clear, visual format."""
        board = self.game.board
        points = board.points

        def get_checker_char(player_id):
            if player_id == 1:  # White
                return "●"
            if player_id == 2:  # Black
                return "o"
            return " "

        print(" 13  14  15  16  17  18      19  20  21  22  23  24")
        print("+---+---+---+---+---+---+--+--+---+---+---+---+---+---+")

        for i in range(5):
            row_left = []
            for p in range(12, 18):
                player, count = points[p]
                char = " "
                if count > i:
                    if count > 5 and i == 4:
                        char = str(count) if count < 10 else "+"
                    else:
                        char = get_checker_char(player)
                row_left.append(f" {char} ")

            row_right = []
            for p in range(18, 24):
                player, count = points[p]
                char = " "
                if count > i:
                    if count > 5 and i == 4:
                        char = str(count) if count < 10 else "+"
                    else:
                        char = get_checker_char(player)
                row_right.append(f" {char} ")
            print(f"|{'|'.join(row_left)}|--+--|{'|'.join(row_right)}|")

        print("+---+---+---+---+---+---+--+--+---+---+---+---+---+---+")
        print("|                           |                           |")
        print("+---+---+---+---+---+---+--+--+---+---+---+---+---+---+")

        for i in range(4, -1, -1):
            row_left = []
            for p in range(11, 5, -1):
                player, count = points[p]
                char = " "
                if i < count:
                    if count > 5 and i == 4:
                        char = str(count) if count < 10 else "+"
                    else:
                        char = get_checker_char(player)
                row_left.append(f" {char} ")

            row_right = []
            for p in range(5, -1, -1):
                player, count = points[p]
                char = " "
                if i < count:
                    if count > 5 and i == 4:
                        char = str(count) if count < 10 else "+"
                    else:
                        char = get_checker_char(player)
                row_right.append(f" {char} ")
            print(f"|{'|'.join(row_left)}|--+--|{'|'.join(row_right)}|")

        print("+---+---+---+---+---+---+--+--+---+---+---+---+---+---+")
        print(" 12  11  10   9   8   7       6   5   4   3   2   1")

        bar_white = board.bar[1]
        bar_black = board.bar[2]
        home_white = board.home[1]
        home_black = board.home[2]

        print(
            f"Bar: White={bar_white} Black={bar_black} | "
            f"Borne off: White={home_white} Black={home_black}"
        )

    def display_current_player_info(self):
        """Display information about the current player."""
        player = self.game.current_player
        print(f"\nCurrent Player: {player.name} ({player.color.name})")
        print(f"Remaining moves: {player.remaining_moves}")

    def display_dice_roll(self):
        """Display the current dice values."""
        dice_values = self.game.dice.values
        print(f"Dice roll: {dice_values}")

        if self.game.dice.is_doubles():
            print("DOUBLES! You can use each die value 4 times.")

        print("Available moves:", self.game.current_player.available_moves)

    def display_available_moves(self):
        """Display helpful information about available moves."""
        player = self.game.current_player
        print(
            f"\n{player.name}, you need to make {player.remaining_moves} more move(s)"
        )
        print(
            " Enter moves as 'from_point to_point' (e.g., '1 5' to move from point 1 to point 5)"
        )
        print(" If you have checkers on bar, enter: 'bar to_point' (e.g., 'bar 5')")
        print(
            " White moves from high to low numbers (24→1), Black from low to high (1→24)"
        )
        if self.game.board.bar[player.player_id] > 0:
            entry_points = "19-24" if player.player_id == 1 else "1-6"
            print(
                f"You have checkers on the bar! You must enter them first (points {entry_points})"
            )

    def display_help(self):
        """Display help information."""
        print("\n" + "=" * 60)
        print("BACKGAMMON HELP")
        print("=" * 60)
        print("BASIC RULES:")
        print("• White moves from point 24 towards 1")
        print("• Black moves from point 1 towards 24")
        print("• Use all dice values in your turn")
        print("• Land on opponent's single checker to hit it")
        print("• Bear off when all checkers are in home board")
        print()
        print("HOW TO MOVE:")
        print("• Regular move: 'from_point to_point' (e.g., '1 5')")
        print("• Enter from bar: 'bar to_point' (e.g., 'bar 5')")
        print("• Bear off: 'from_point off' (e.g., '24 off')")
        print("• Points are numbered 1-24 as shown on board")
        print("• You must enter checkers from bar first if any")
        print("• Doubles let you use each value 4 times")
        print()
        print("BEARING OFF:")
        print("• White: All checkers in points 1-6")
        print("• Black: All checkers in points 19-24")
        print("• Bear off by moving exact dice value or higher")
        print("=" * 60)

    def display_game_over(self):
        """Display game over information."""
        winner = self.game.get_winner()
        if winner:
            print("\nGAME OVER!")
            print(f"Winner: {winner.name} ({winner.color.name})")
            print("Congratulations!")
        else:
            print("Game ended without a winner.")


def main():
    """Main entry point for the CLI application."""
    cli = BackgammonCLI()
    try:
        cli.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except (GameQuitException, GameNotInitializedError, InvalidPlayerTurnError) as e:
        print(f"Game error: {e}")
    except OSError as e:
        print(f"System error: {e}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
