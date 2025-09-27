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

  - Added private backing fields (\_points, \_bar, \_home) with public properties in Board class
  - Added private \_position with public property in Checker class
  - Added private \_values with public property in Dice class
  - Added private \_checkers with public property in Player class
  - Added private \_board, \_dice, \_player1, \_player2 with public properties in Game class
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

### Added - 2024-12-19
- Created comprehensive exception system in `core/exceptions.py`
- Added hierarchical custom exceptions following SOLID principles:
  - Base exceptions: `BackgammonError`, `GameError`, `BoardError`, `PlayerError`, `DiceError`, `CheckerError`
  - Specific exceptions for each domain with detailed error messages and context
- Enhanced error handling in `Game` class with proper exception usage
- Added game state validation to prevent operations on uninitialized or finished games

### Changed - 2024-12-19
- Updated `Game` class to use custom exceptions instead of generic RuntimeError
- Improved error messages with more context and specific error types
- Added game initialization tracking for better state management

### Added - 2024-12-19
- Implemented TDD-driven exception system across core classes
- Added `InvalidPointError` with point validation in Board class methods
- Added `InvalidCheckerPositionError` for Checker position validation
- Enhanced existing Game class exception handling with proper validation
- Added comprehensive test cases for all new exception scenarios

### Changed - 2024-12-19
- Refactored exceptions.py to follow TDD principles (only implementing needed exceptions)
- Updated Checker class to use custom exceptions instead of generic ValueError
- Enhanced Board class with point validation using custom exceptions
- Improved error messages with contextual information and specific error attributes

### Fixed - 2024-12-19
- Corrected exception hierarchy to avoid over-engineering unused exceptions
- Applied SOLID principles properly by implementing exceptions incrementally based on actual needs

### Fixed - 2024-12-19
- Moved all Game class tests from `test_game.py` to `tests_game.py` to follow consistent naming convention
- Fixed syntax errors in `core/exceptions.py` that were causing import issues
- Updated test initialization to properly call `game.setup_game()` before testing exception scenarios
- Ensured all tests follow TDD principles with proper setup and teardown

### Added - 2024-12-19
- Comprehensive exception handling tests in proper test file location
- Consistent test file naming across the project (tests_*.py pattern)
- Enhanced test coverage for Game class exception scenarios

### Changed - 2024-12-19
- Standardized test file naming convention to match existing pattern
- Improved test reliability by ensuring proper game initialization
- Enhanced exception test coverage following TDD methodology

### Fixed - 2024-12-19
- Fixed syntax error in `core/exceptions.py` by removing duplicated class definition
- Fixed duplicate return statement in `core/checker.py`
- Updated failing test `test_apply_move_without_current_player_returns_false` to properly test exception behavior instead of return value
- Corrected test logic to follow TDD principles with proper game initialization before testing exception scenarios

### Changed - 2024-12-19
- Enhanced test reliability by ensuring proper exception testing patterns
- Improved consistency between test expectations and actual implementation behavior
- Updated tests to match the new exception-based error handling approach

### Fixed - 2024-12-19
- Fixed failing dice initialization test by updating it to work with new DiceNotRolledError exception
- Removed duplicate return statement in Checker.__str__ method
- Added proper test coverage for NoMovesRemainingError in Player class
- Enhanced exception testing to verify proper error messages and attributes

### Added - 2024-12-19
- Added test for DiceNotRolledError to verify dice values cannot be accessed before rolling
- Added test for NoMovesRemainingError to verify player move validation
- Enhanced test coverage for all implemented custom exceptions
