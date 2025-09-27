"""Command Line Interface for Backgammon game."""

from core.game import Game
from core.exceptions import (
    GameNotInitializedError,
    InvalidPlayerTurnError,
    GameAlreadyOverError,
    InvalidMoveError,
    NoMovesRemainingError
)


class BackgammonCLI:
    """
    Command Line Interface for playing Backgammon.
    Handles user interaction and game orchestration.
    """

    def __init__(self):
        """Initialize the CLI with a new game."""
        self.game = None
        self.player1_name = None
        self.player2_name = None

    def start_game(self):
        """Start a new backgammon game with player setup."""
        self.display_welcome()
        
        # Get player names
        self.player1_name = input("Enter Player 1 (White) name: ").strip() or "White"
        self.player2_name = input("Enter Player 2 (Black) name: ").strip() or "Black"

        # Initialize game
        self.game = Game(self.player1_name, self.player2_name)

        print(f"\n{self.player1_name} (White) vs {self.player2_name} (Black)")
        print("Setting up the board...")

        # Setup game
        self.game.setup_game()

        # Initial roll to determine who goes first
        print("\n🎲 INITIAL ROLL - Each player rolls one die to determine who goes first!")
        winner = self.game.initial_roll_until_decided()
        print(f"{self.player1_name} rolls: {self.game.dice.initial_values[0]}")
        print(f"{self.player2_name} rolls: {self.game.dice.initial_values[1]}")

        if winner == 1:
            print(f"🏆 {self.player1_name} (White) goes first!")
        else:
            print(f"🏆 {self.player2_name} (Black) goes first!")

        print("\n" + "="*60)
        print("HOW TO PLAY:")
        print("- Points are numbered 1-24 (see board below)")
        print("- White moves from point 1 towards 24, Black from 24 towards 1")
        print("- Enter moves as 'from_point to_point' (e.g., '1 5')")
        print("- You must use all dice values in your turn")
        print("- Hit opponent by landing on their single checker")
        print("- Bear off when all checkers are in your home board (points 19-24 for White, 1-6 for Black)")
        print("- Type 'q' to quit, 'h' for help")
        print("="*60)

        # Start the game loop
        self.game_loop()

    def display_welcome(self):
        """Display welcome message and basic rules."""
        print("🎲 WELCOME TO BACKGAMMON! 🎲")
        print("=" * 60)
        print("Backgammon is a classic board game of strategy and luck.")
        print("The goal is to move all your checkers around the board")
        print("and bear them off before your opponent does!")
        print("=" * 60)

    def game_loop(self):
        """Main game loop handling turns and moves."""
        while not self.game.is_game_over():
            try:
                self.display_board()
                self.display_current_player_info()

                # Start turn (roll dice)
                input(f"\n🎲 {self.game.current_player.name}, press Enter to roll dice...")
                self.game.start_turn()

                self.display_dice_roll()
                self.display_available_moves()

                # Handle moves until turn is over
                while self.game.current_player.remaining_moves > 0:
                    self.handle_player_move()

                # End turn and switch players
                self.game.current_player.end_turn()
                self.game.switch_players()

            except (GameNotInitializedError, InvalidPlayerTurnError,
                    GameAlreadyOverError, InvalidMoveError) as e:
                print(f"❌ Error: {e}")
                continue

        # Game over
        self.display_game_over()

    def display_board(self):
        """Display the current board state in a clear, visual format."""
        board = self.game.board

        print("\n" + "╔" + "═" * 78 + "╗")
        print("║" + " " * 35 + "BACKGAMMON BOARD" + " " * 35 + "║")
        print("╠" + "═" * 78 + "╣")

        # Top row (Black's home board - points 19-24, then bar, then 13-18)
        print("║ 19  20  21  22  23  24    BAR    13  14  15  16  17  18  ║")
        print("║" + "─" * 78 + "║")

        top_row = []
        # Points 18-12 (Black's side, displayed as 19-13)
        for i in range(18, 12, -1):
            player, count = board.points[i]
            if player == 0:
                top_row.append("   ")
            elif player == 1:  # White
                top_row.append(f" W{count}")
            else:  # Black
                top_row.append(f" B{count}")

        # Bar
        bar_white = board.bar[1]
        bar_black = board.bar[2]
        top_row.append(f" W{bar_white} B{bar_black}")

        # Points 12-18 (Black's side, displayed as 13-19, but reversed)
        for i in range(12, 18):
            player, count = board.points[i]
            if player == 0:
                top_row.append("   ")
            elif player == 1:  # White
                top_row.append(f" W{count}")
            else:  # Black
                top_row.append(f" B{count}")

        print("║" + "".join(f"{x:>3}" for x in top_row) + " ║")

        # Middle section
        print("║" + " " * 78 + "║")
        print("║" + " " * 78 + "║")

        # Bottom row (White's home board - points 1-6, then bar, then 7-12)
        print("║  1   2   3   4   5   6    BAR     7   8   9  10  11  12  ║")
        print("║" + "─" * 78 + "║")

        bottom_row = []
        # Points 0-5 (White's side, displayed as 1-6)
        for i in range(6):
            player, count = board.points[i]
            if player == 0:
                bottom_row.append("   ")
            elif player == 1:  # White
                bottom_row.append(f" W{count}")
            else:  # Black
                bottom_row.append(f" B{count}")

        # Bar (already added above)
        bottom_row.append(f" W{bar_white} B{bar_black}")

        # Points 6-11 (White's side, displayed as 7-12)
        for i in range(6, 12):
            player, count = board.points[i]
            if player == 0:
                bottom_row.append("   ")
            elif player == 1:  # White
                bottom_row.append(f" W{count}")
            else:  # Black
                bottom_row.append(f" B{count}")

        print("║" + "".join(f"{x:>3}" for x in bottom_row) + " ║")
        print("╚" + "═" * 78 + "╝")

        # Display borne off checkers
        home_white = board.home[1]
        home_black = board.home[2]
        print(f"\n🏠 Borne Off - White: {home_white}, Black: {home_black}")

    def display_current_player_info(self):
        """Display information about the current player."""
        player = self.game.current_player
        print(f"\n👤 Current Player: {player.name} ({player.color.name})")
        print(f"🎯 Remaining moves: {player.remaining_moves}")

    def display_dice_roll(self):
        """Display the current dice values."""
        dice_values = self.game.dice.values
        print(f"🎲 Dice roll: {dice_values}")

        if self.game.dice.is_doubles():
            print("💥 DOUBLES! You can use each die value 4 times.")
        else:
            print("📋 Available moves:", self.game.dice.get_moves())

    def display_available_moves(self):
        """Display helpful information about available moves."""
        player = self.game.current_player
        print(f"\n💡 {player.name}, you need to make {player.remaining_moves} more move(s)")
        print("💡 Enter moves as 'from_point to_point' (e.g., '1 5' to move from point 1 to point 5)")
        print("💡 White moves from low to high numbers (1→24), Black from high to low (24→1)")
        if self.game.board.bar[player.player_id] > 0:
            entry_points = "1-6" if player.player_id == 1 else "19-24"
            print(f"⚠️  You have checkers on the bar! You must enter them first (points {entry_points})")

    def handle_player_move(self):
        """Handle a single move from the current player."""
        while True:
            try:
                move_input = input(
                    f"🎯 Enter move (from_point to_point) or 'h' for help, 'q' to quit: "
                ).strip().lower()

                if move_input == 'q':
                    print("👋 Game ended by player.")
                    exit(0)
                elif move_input == 'h':
                    self.display_help()
                    continue

                # Parse move
                parts = move_input.split()
                if len(parts) != 2:
                    print("❌ Invalid input. Please enter two numbers separated by space (e.g., '1 5').")
                    continue

                try:
                    from_point = int(parts[0])
                    to_point = int(parts[1])
                    
                    # Validate range (user enters 1-24, we convert to 0-23)
                    if not (1 <= from_point <= 24 and 1 <= to_point <= 24):
                        print("❌ Invalid points. Points must be between 1-24.")
                        continue
                    
                    from_point -= 1  # Convert to 0-based
                    to_point -= 1
                    
                except ValueError:
                    print("❌ Invalid input. Please enter valid numbers.")
                    continue

                # Attempt the move
                success = self.game.apply_move(from_point, to_point)

                if success:
                    print(f"✅ Move successful: {from_point + 1} → {to_point + 1}")
                    break
                else:
                    print("❌ Invalid move. Try again or check the board.")

            except (InvalidMoveError, NoMovesRemainingError) as e:
                print(f"❌ Move error: {e}")
                continue

    def display_help(self):
        """Display help information."""
        print("\n" + "="*60)
        print("🎲 BACKGAMMON HELP")
        print("="*60)
        print("📋 BASIC RULES:")
        print("• White moves from point 1 towards 24")
        print("• Black moves from point 24 towards 1")
        print("• Use all dice values in your turn")
        print("• Land on opponent's single checker to hit it")
        print("• Bear off when all checkers are in home board")
        print()
        print("🎯 HOW TO MOVE:")
        print("• Enter: 'from_point to_point' (e.g., '1 5')")
        print("• Points are numbered 1-24 as shown on board")
        print("• You must enter checkers from bar first if any")
        print("• Doubles let you use each value 4 times")
        print()
        print("🏠 BEARING OFF:")
        print("• White: All checkers in points 19-24")
        print("• Black: All checkers in points 1-6")
        print("• Bear off by moving exact dice value or higher")
        print("="*60)

    def display_game_over(self):
        """Display game over information."""
        winner = self.game.get_winner()
        if winner:
            print(f"\n🎉 🎊 GAME OVER! 🎊 🎉")
            print(f"🏆 Winner: {winner.name} ({winner.color.name})")
            print("🎊 Congratulations! 🎊")
        else:
            print("Game ended without a winner.")


def main():
    """Main entry point for the CLI application."""
    cli = BackgammonCLI()
    try:
        cli.start_game()
    except KeyboardInterrupt:
        print("\n👋 Game interrupted by user.")
    except Exception as e:
        print(f"💥 An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
