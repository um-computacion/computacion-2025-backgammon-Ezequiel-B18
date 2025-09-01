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
