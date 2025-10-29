import json
import os
import redis
from flask import Flask, jsonify, request

from core.game import Game

app = Flask(__name__)

# Use environment variable for Redis host, default to localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

GAME_ID = "backgammon_game"


def get_game_state(game):
    """Adds a winner key to the game state dictionary."""
    state = game.to_dict()
    winner = game.get_winner()
    state["winner"] = winner.to_dict() if winner else None
    return state


def save_game(game):
    """Saves the game state to Redis."""
    redis_client.set(GAME_ID, json.dumps(get_game_state(game)))


def load_game():
    """Loads the game state from Redis."""
    game_data = redis_client.get(GAME_ID)
    if game_data:
        # We don't need to load the winner key, it's derived
        game_dict = json.loads(game_data)
        game_dict.pop("winner", None)
        return Game.from_dict(game_dict)
    return None


@app.route("/game", methods=["POST"])
def new_game():
    """Starts a new game."""
    data = request.get_json()
    player1_name = data.get("player1_name", "Player 1")
    player2_name = data.get("player2_name", "Player 2")
    game = Game(player1_name=player1_name, player2_name=player2_name)
    game.setup_game()
    game.initial_roll_until_decided()
    save_game(game)
    return jsonify(get_game_state(game))


@app.route("/game", methods=["GET"])
def get_game_route():
    """Gets the current game state."""
    game = load_game()
    if game:
        return jsonify(get_game_state(game))
    return jsonify({"error": "Game not found"}), 404


@app.route("/game/roll", methods=["POST"])
def roll_dice():
    """Rolls the dice for the current player."""
    game = load_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    game.roll_dice_for_turn()
    save_game(game)
    return jsonify(get_game_state(game))


@app.route("/game/move", methods=["POST"])
def move():
    """Applies a move for the current player."""
    data = request.get_json()
    from_point = data.get("from_point")
    # Handle integer conversion for from_point
    if isinstance(from_point, str) and from_point.isdigit():
        from_point = int(from_point)
    to_point = data.get("to_point")

    game = load_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    try:
        game.apply_move(from_point, to_point)
        save_game(game)
        return jsonify(get_game_state(game))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/game/bear_off", methods=["POST"])
def bear_off():
    """Applies a bear-off move for the current player."""
    data = request.get_json()
    from_point = data.get("from_point")

    game = load_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    try:
        game.apply_bear_off_move(from_point)
        save_game(game)
        return jsonify(get_game_state(game))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/game/valid_moves/<from_point_str>", methods=["GET"])
def valid_moves(from_point_str):
    """Gets the valid moves for a given point."""
    game = load_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if from_point_str == "bar":
        from_point = "bar"
    else:
        from_point = int(from_point_str)

    moves = game.get_valid_moves(from_point)
    return jsonify(moves)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
