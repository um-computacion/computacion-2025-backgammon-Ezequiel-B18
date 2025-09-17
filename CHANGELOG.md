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
