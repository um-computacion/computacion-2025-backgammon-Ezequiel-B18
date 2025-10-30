from cli.cli import main as cli_main
from pygame_ui.ui import BackgammonUI


def main():
    """Run the Backgammon game.

    Presents a menu to the user to choose between CLI or Pygame UI.
    """
    print("=" * 50)
    print("\nChoose an interface:")
    print("  1. CLI")
    print("  2. Pygame UI")
    print("\nEnter your choice (1 or 2): ", end="")

    choice = input().strip()

    if choice == "1":
        print("\nStarting CLI mode...\n")
        cli_main()
    elif choice == "2":
        print("\nStarting Pygame UI mode...\n")
        ui = BackgammonUI()
        ui.run()
    else:
        print("\nInvalid choice. Please run the program again and select 1 or 2.")


if __name__ == "__main__":
    main()
