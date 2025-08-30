# Changelog 30/08/2025

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created Dice class with the following functionality:
  - Rolling two dice with random values between 1-6
  - Detecting when doubles are rolled (same value on both dice)
  - Special handling for doubles in backgammon (each die value can be used four times)
  - Initial roll functionality to determine which player goes first
  - Function to determine the highest roller in the initial roll
- Implemented comprehensive test suite for the Dice class following TDD methodology
