#!/bin/bash
# Docker entrypoint script for Backgammon

case "$1" in
  test)
    echo "Running tests with coverage..."
    python -m coverage run -m unittest discover -s tests -p "tests_*.py" -v
    python -m coverage report
    python -m coverage xml
    ;;
  cli)
    echo "Starting CLI game..."
    python -m cli.cli
    ;;
  *)
    echo "Usage: docker run backgammon [test|cli]"
    echo ""
    echo "Commands:"
    echo "  test  - Run unit tests with coverage"
    echo "  cli   - Run the CLI interface"
    exit 1
    ;;
esac
