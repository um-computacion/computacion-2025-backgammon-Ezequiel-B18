#!/bin/bash
set -e

case "${1:-test}" in
    test)
        echo "Running test suite with coverage..."
        coverage run -m unittest discover -s tests -v
        coverage report
        coverage xml
        ;;
    cli)
        echo "Starting Backgammon CLI..."
        python -m cli.cli
        ;;
    pygame)
        echo "Starting Pygame UI..."
        python -m pygame_ui.ui
        ;;
    main)
        echo " Starting main menu..."
        python main.py
        ;;
    server)
        echo " Starting Flask API server..."
        python -m server.main
        ;;
    *)
        echo "Unknown mode: $1"
        echo "Usage: docker run backgammon [test|cli|pygame|main|server]"
        exit 1
        ;;
esac
