# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created Dice class with the following functionality: (30/08/2025)
  - Rolling two dice with random values between 1-6
  - Detecting when doubles are rolled (same value on both dice)
  - Special handling for doubles in backgammon (each die value can be used four times)
  - Initial roll functionality to determine which player goes first
  - Function to determine the highest roller in the initial roll
- Implemented comprehensive test suite for the Dice class following TDD methodology

- Created Board class with the following functionality: (31/08/2025)
  - Standard backgammon board representation with 24 points
  - Support for moving checkers between points
  - Rules enforcement for valid moves
  - Bar functionality for hit checkers
  - Bearing off checkers when all are in the home board
  - Win condition detection
  - Helper methods for board state queries
- Implemented comprehensive test suite for the Board class following TDD methodology

- Created Checker class with the following functionality: (01/09/2025)
  - Representing individual checkers with color and state
  - Tracking checker position on the board
  - Handling moves according to player color (direction)
  - Supporting placement on the bar when hit
  - Supporting re-entry from the bar
  - Supporting bearing off from the home board
  - Validation for all checker operations
- Implemented comprehensive test suite for the Checker class following TDD methodology

- Created Player class with the following functionality: (02/09/2025)
  - Managing player identity (name, color, player ID)
  - Tracking turn status and remaining moves
  - Managing a collection of 15 checkers
  - Distributing checkers to starting positions
  - Providing methods to query checker states (on board, bar, borne off)
  - Checking win conditions
  - Strict separation of responsibilities from other classes
- Implemented comprehensive test suite for the Player class following TDD and SOLID principles

### Fixed
- Resolved test failures in checker and board classes: (11/09/2025)
  - Fixed checker test to properly place checker in home board before bearing off
  - Corrected board bear-off logic for proper range checking
  - Updated test expectations to match actual behavior of test setups
  - Improved test isolation to prevent state pollution between tests
  - Ensured all tests follow proper backgammon rules and TDD principles

### Changed
- Updated CI workflow to run on entire project structure: (13/09/2025)
  - Modified test discovery to automatically find all test files in tests directory
  - Updated Pylint analysis to scan all Python files in the project
  - Improved workflow scalability and maintainability
  - Enhanced code coverage and quality analysis across the entire codebase
