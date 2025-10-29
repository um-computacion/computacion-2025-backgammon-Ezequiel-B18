# Backgammon

**Nombre:** Ezequiel Blajevitch

## How to Run the Game

This project now uses a client-server architecture with Redis for game state persistence.

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed and running.
- [Python 3](https://www.python.org/downloads/) installed.

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Start the Redis Database

In your terminal, navigate to the project's root directory and run the following command to start the Redis container:

```bash
docker-compose up -d
```

### 3. Run the Game Server

Next, open a new terminal window, navigate to the project's root directory, and run the following command to start the Flask game server:

```bash
python server/main.py
```

### 4. Launch the Pygame UI

Finally, in a third terminal window, navigate to the project's root directory and run the following command to launch the Pygame client:

```bash
python -m pygame_ui.ui
```

You can now play the game. The game state will be automatically saved after every move.

**Resuming a Game:** If you close the game and restart it later, you will be prompted to either resume the saved game or start a new one.

---

## Development

### Running Tests

To run the test suite and generate a coverage report, use the following command:

```bash
coverage run -m unittest discover tests && coverage report -m && coverage xml
```
