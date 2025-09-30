# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Created Dice class with comprehensive functionality (30/08/2025):

  - Rolling two dice with random values between 1-6
  - Detecting when doubles are rolled (same value on both dice)
  - Special handling for doubles in backgammon (each die value can be used four times)
  - Initial roll functionality to determine which player goes first
  - Function to determine the highest roller in the initial roll
  - Implemented comprehensive test suite following TDD methodology

- Created Board class with comprehensive functionality (31/08/2025):

  - Standard backgammon board representation with 24 points
  - Support for moving checkers between points
  - Rules enforcement for valid moves
  - Bar functionality for hit checkers
  - Bearing off checkers when all are in the home board
  - Win condition detection
  - Helper methods for board state queries
  - Implemented comprehensive test suite following TDD methodology

- Created Checker class with comprehensive functionality (01/09/2025):

  - Representing individual checkers with color and state
  - Tracking checker position on the board
  - Handling moves according to player color (direction)
  - Supporting placement on the bar when hit
  - Supporting re-entry from the bar
  - Supporting bearing off from the home board
  - Validation for all checker operations
  - Implemented comprehensive test suite following TDD methodology

- Created Player class with comprehensive functionality (02/09/2025):

  - Managing player identity (name, color, player ID)
  - Tracking turn status and remaining moves
  - Managing a collection of 15 checkers
  - Distributing checkers to starting positions
  - Providing methods to query checker states (on board, bar, borne off)
  - Checking win conditions
  - Strict separation of responsibilities from other classes
  - Implemented comprehensive test suite following TDD and SOLID principles

- Created Game orchestrator class to coordinate Board, Dice and Player (14/09/2025):

  - Game setup and initialization
  - Sync logic to maintain consistency between Board and Player states
  - Core turn methods and game flow management
  - Unit tests covering initialization, setup/distribution, initial roll decision and start turn

- Created UML Diagram using PlantUML extension (16/09/2025):

  - Complete class diagram showing all core classes and relationships
  - Documentation of Single Source of Truth pattern
  - Visual representation of SOLID principles implementation

- Created comprehensive exception system in `core/exceptions.py` (27/9/2025):

  - Hierarchical custom exceptions following SOLID principles
  - Base exceptions: `BackgammonError`, `GameError`, `BoardError`, `PlayerError`, `DiceError`, `CheckerError`
  - Specific exceptions for each domain with detailed error messages and context
  - Game state validation to prevent operations on uninitialized or finished games

- Implemented TDD-driven exception system across core classes (27/9/2025):

  - `InvalidPointError` with point validation in Board class methods
  - `InvalidCheckerPositionError` for Checker position validation
  - Enhanced existing Game class exception handling with proper validation
  - Comprehensive test cases for all new exception scenarios

- Comprehensive exception handling tests in proper test file location (27/9/2025):

  - Consistent test file naming across the project (tests\_\*.py pattern)
  - Enhanced test coverage for Game class exception scenarios
  - Test for DiceNotRolledError to verify dice values cannot be accessed before rolling
  - Test for NoMovesRemainingError to verify player move validation
  - Enhanced test coverage for all implemented custom exceptions

- Implemented comprehensive CLI interface in `cli/cli.py` for playing Backgammon (27/9/2025):

  - `BackgammonCLI` class that orchestrates game flow using existing core classes
  - Visual board display showing all 24 points, bar, and borne-off checkers
  - Player turn management with dice rolling and move input
  - Proper error handling for invalid moves and game states
  - Game initialization with player name input and initial roll
  - Game loop with win condition checking and turn switching
  - Followed SOLID principles with clear separation between CLI interaction and game logic
  - Used only built-in Python functions (no external libraries)
  - Prepared foundation for TDD testing of CLI components

- Enhanced CLI interface with improved board display (28/9/2025):

  - Unicode box drawing characters for better visual appeal
  - Comprehensive welcome message and game rules explanation at startup
  - Detailed help system accessible during gameplay with 'h' command
  - Clear instructions for move input with examples and validation feedback
  - Visual indicators for better user experience and clarity
  - Display of available moves and remaining moves counter
  - Enhanced error messages with indicators for better user feedback
  - Special handling instructions for checkers on the bar
  - Improved game flow with better prompts and user guidance throughout the game

- Added tests for the CLI (29/9/2025)
  - Comprehensive test suite for CLI module (tests_cli.py)
  - Tests for all CLI display methods including board rendering and player information
  - Tests for user input handling including move parsing and validation
  - Tests for game loop orchestration and turn management
  - Tests for error handling and exception scenarios
  - Tests for help system and quit functionality
  - Integration tests for main function execution paths

### Changed

- Updated CI workflow to run on entire project structure (13/09/2025):

  - Modified test discovery to automatically find all test files in tests directory
  - Updated Pylint analysis to scan all Python files in the project
  - Improved workflow scalability and maintainability
  - Enhanced code coverage and quality analysis across the entire codebase

- Documented analysis of class responsibilities and potential clashes (15/09/2025):

  - Identified overlapping responsibilities between Board, Player and Checker
  - Recommended refactors to make Board the single source of truth
  - Proposed simplification of Player.distribute_checkers method

- Enforced Board as single source of truth (15/09/2025):

  - Added Board.setup_starting_positions() method
  - Made Board.move_checker return structured events instead of boolean
  - Updated Player.distribute_checkers to no longer mutate board.points
  - Updated Game.setup_game to use Board.setup_starting_positions()
  - Implemented Game.sync_checkers to reconcile Checker objects with Board state

- Implemented encapsulation improvements across all core classes (16/09/2025):

  - Added private backing fields with public properties in all classes
  - All changes are backwards-compatible and maintain existing functionality
  - Improved API clarity and prepared foundation for future validation/access control

- Achieved comprehensive Pylint compliance and code quality improvements (16/09/2025):

  - Added module docstrings to all core and test files for better documentation
  - Added class docstrings to all test classes following Python documentation standards
  - Added missing method docstrings for complete API documentation coverage
  - Fixed line length violations by reformatting long lines to 100 character limit
  - Removed unnecessary else/elif statements after return for cleaner code flow
  - Fixed superfluous parentheses and trailing whitespace issues
  - Resolved unused argument warnings and disallowed name conflicts
  - Simplified comparison operations using 'in' operator for better readability
  - Refactored Game.sync_checkers method to reduce complexity by splitting into focused helper methods
  - Maintained encapsulation improvements while ensuring all property access works correctly
  - Enhanced code maintainability and readability across entire codebase
  - Established professional Python development standards and documentation practices

- Updated `Game` class to use custom exceptions instead of generic RuntimeError (27/9/2025):

  - Improved error messages with more context and specific error types
  - Added game initialization tracking for better state management

- Refactored exceptions.py to follow TDD principles (27/9/2025):

  - Only implementing needed exceptions to avoid over-engineering
  - Updated Checker class to use custom exceptions instead of generic ValueError
  - Enhanced Board class with point validation using custom exceptions
  - Improved error messages with contextual information and specific error attributes

- Standardized test file naming convention to match existing pattern (27/9/2025):

  - Improved test reliability by ensuring proper game initialization
  - Enhanced exception test coverage following TDD methodology

- Enhanced test reliability by ensuring proper exception testing patterns (27/9/2025):

  - Improved consistency between test expectations and actual implementation behavior
  - Updated tests to match the new exception-based error handling approach

### Fixed

- Resolved test failures in checker and board classes (11/09/2025):

  - Fixed checker test to properly place checker in home board before bearing off
  - Corrected board bear-off logic for proper range checking
  - Updated test expectations to match actual behavior of test setups
  - Improved test isolation to prevent state pollution between tests
  - Ensured all tests follow proper backgammon rules and TDD principles

- Fixed TypeError in Player.distribute_checkers() method signature (16/09/2025):

  - Restored missing 'board' parameter that was accidentally removed during encapsulation changes
  - Fixed 4 failing tests that were calling the method with board parameter
  - All unit tests now pass successfully

- Fixed pylint errors for Board.bar property access (17/09/2025):

  - Restored 'bar' property name instead of 'bar_dict' to maintain API consistency
  - Added missing docstring for Checker.position setter method
  - Resolved all E1101 no-member pylint errors while preserving encapsulation
  - All core and test files now correctly access board.bar property

- Corrected exception hierarchy to avoid over-engineering unused exceptions (27/9/2025):

  - Applied SOLID principles properly by implementing exceptions incrementally based on actual needs

- Fixed syntax error in `core/exceptions.py` by removing duplicated class definition (27/9/2025):

  - Fixed duplicate return statement in `core/checker.py`
  - Updated failing test to properly test exception behavior instead of return value
  - Corrected test logic to follow TDD principles with proper game initialization before testing exception scenarios

- Updated legacy `tests/test_game.py` to honor game initialization requirements and new exception flow before calling `start_turn` and `apply_move` (27/9/2025)

- Corrected initial roll logic to follow standard backgammon rules (27/9/2025):

  - Each player rolls one die separately instead of rolling two dice together
  - Updated `Dice.initial_roll()` to simulate separate rolls for each player
  - Modified `Dice.get_highest_roller()` to properly compare the two player rolls
  - Updated tests to reflect the corrected initial roll behavior
  - Ensured game initialization follows proper backgammon rules for determining first player

- Updated CLI to display individual player rolls during initial roll determination (27/9/2025):

  - Clarifying that each player rolls separately according to standard backgammon rules

- Fixed some tests (28/9/2025)

  - Fixed AttributeError in Board class where setup_starting_positions() was trying to assign to read-only points property
  - Corrected checker movement directions: White moves 0→23, Black moves 23→0
  - Fixed home board ranges: White home is points 18-23, Black home is points 0-5
  - Fixed entry points from bar: White enters points 0-5, Black enters points 18-23
  - Updated Board.enter_from_bar() to use internal \_points storage instead of property
  - Fixed Player.get_starting_positions() to return correct positions for each color
  - Corrected checker bear-off calculations for both White and Black checkers

- Fixed CLI tests errors (29/9/2025)
  - Fixed CLI tests hanging with infinite loops during `handle_player_move` testing
  - Fixed `test_handle_player_move_quit` by properly mocking `sys.exit` with `SystemExit` exception
  - Fixed output verification in CLI tests by using `mock_print` instead of `StringIO`
  - Removed duplicate `test_game.py` file that was conflicting with `tests_game.py`
  - Ensured all CLI tests have proper exit conditions and don't cause KeyboardInterrupt

### Improved - 2024-01-XX

- Simplified CLI quit handling by removing sys.exit() dependency
- Added GameQuitException for better separation of concerns in CLI
- Improved CLI testability by using exception-based flow control instead of system exit
- Enhanced SOLID compliance in CLI design (Single Responsibility Principle)

### Technical Details - 2024-01-XX

- Replaced sys.exit() calls with GameQuitException in handle_player_move()
- Updated game_loop() to catch and handle quit exceptions gracefully
- Simplified CLI tests by removing complex sys.exit() mocking
- Added test for game loop quit handling with exception verification
