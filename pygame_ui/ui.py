"""
Pygame UI for the Backgammon game.

This module provides a graphical user interface for the Backgammon game using Pygame.
It includes a start screen for player name input, a game screen with the board, checkers,
and an information panel, and handles user input for checker movement, including
the bar and bearing off.
"""

import pygame
import sys
import requests

# --- Constants ---
# Colors used in the UI, based on the provided image.
CREAM = (255, 248, 220)  # Lighter cream for better contrast
LIGHT_BROWN = (205, 133, 63)  # A more distinct brown
TAN = (210, 180, 140)  # Tan color for the board points
DARK_BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (173, 216, 230, 150)  # Semi-transparent blue for highlighting moves.

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Board dimensions
BOARD_MARGIN = 20
BAR_WIDTH = 50
POINT_HEIGHT = 300
POINT_WIDTH = (SCREEN_WIDTH - 2 * BOARD_MARGIN - BAR_WIDTH - 200) / 12
CHECKER_RADIUS = int(POINT_WIDTH / 2) - 2

API_URL = "http://127.0.0.1:8000"


class APIClient:
    """A simple client to interact with the backgammon server."""

    def get_game(self):
        """Fetches the current game state."""
        try:
            response = requests.get(f"{API_URL}/game")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching game state: {e}")
            return None

    def new_game(self, player1_name, player2_name):
        """Starts a new game."""
        try:
            payload = {"player1_name": player1_name, "player2_name": player2_name}
            response = requests.post(f"{API_URL}/game", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error starting new game: {e}")
            return None

    def roll_dice(self):
        """Rolls the dice for the current player."""
        try:
            response = requests.post(f"{API_URL}/game/roll")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error rolling dice: {e}")
            return None

    def move(self, from_point, to_point):
        """Applies a move for the current player."""
        try:
            payload = {"from_point": from_point, "to_point": to_point}
            response = requests.post(f"{API_URL}/game/move", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making move: {e}")
            return None

    def bear_off(self, from_point):
        """Applies a bear-off move for the current player."""
        try:
            payload = {"from_point": from_point}
            response = requests.post(f"{API_URL}/game/bear_off", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error bearing off: {e}")
            return None

    def get_valid_moves(self, from_point):
        """Gets valid moves for a given point."""
        try:
            response = requests.get(f"{API_URL}/game/valid_moves/{from_point}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting valid moves: {e}")
            return []


class BackgammonUI:
    """
    The main class for the Backgammon UI.

    This class handles the game loop, drawing the UI elements, and processing user input.
    """

    def __init__(self):
        """Initializes the Pygame UI."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Backgammon")
        self.running = True
        self.font = pygame.font.SysFont(None, 32)
        self.game_state = "START_SCREEN"
        self.player1_name = ""
        self.player2_name = ""
        self.active_input = "player1"
        self.input_boxes = {
            "player1": pygame.Rect(400, 200, 200, 40),
            "player2": pygame.Rect(400, 300, 200, 40),
        }
        self.api_client = APIClient()
        self.game_data = None
        self.selected_checker_point = None
        self.highlighted_moves = []
        self.dice_rolled_this_turn = False
        self.point_rects = self.calculate_point_rects()
        bar_x = BOARD_MARGIN + 6 * POINT_WIDTH
        self.bar_rects = {
            1: pygame.Rect(
                bar_x, BOARD_MARGIN, BAR_WIDTH, SCREEN_HEIGHT / 2 - BOARD_MARGIN
            ),
            2: pygame.Rect(
                bar_x, SCREEN_HEIGHT / 2, BAR_WIDTH, SCREEN_HEIGHT / 2 - BOARD_MARGIN
            ),
        }
        self.bear_off_rects = {
            1: pygame.Rect(
                SCREEN_WIDTH - 100, BOARD_MARGIN, 80, SCREEN_HEIGHT / 2 - BOARD_MARGIN
            ),
            2: pygame.Rect(
                SCREEN_WIDTH - 100,
                SCREEN_HEIGHT / 2,
                80,
                SCREEN_HEIGHT / 2 - BOARD_MARGIN,
            ),
        }
        panel_x = SCREEN_WIDTH - 200 - BOARD_MARGIN
        self.bear_off_button = pygame.Rect(panel_x + 25, SCREEN_HEIGHT - 100, 150, 50)
        self.play_again_button = pygame.Rect(0, 400, 200, 50)
        self.play_again_button.centerx = SCREEN_WIDTH // 2
        self.resume_button = pygame.Rect(0, 250, 200, 50)
        self.resume_button.centerx = SCREEN_WIDTH // 2
        self.start_new_button = pygame.Rect(0, 350, 200, 50)
        self.start_new_button.centerx = SCREEN_WIDTH // 2
        self.start_button = pygame.Rect(0, 400, 200, 50)
        self.start_button.centerx = SCREEN_WIDTH // 2

    def calculate_point_rects(self):
        """
        Calculates the rectangular areas for each point on the board.

        This is used to detect clicks on the points.
        """
        rects = []
        for i in range(24):
            if i < 12:  # Bottom half
                x = BOARD_MARGIN + (11 - i) * POINT_WIDTH
                if (11 - i) >= 6:
                    x += BAR_WIDTH
                rect = pygame.Rect(
                    x,
                    SCREEN_HEIGHT - BOARD_MARGIN - POINT_HEIGHT,
                    POINT_WIDTH,
                    POINT_HEIGHT,
                )
            else:  # Top half
                x = BOARD_MARGIN + (i - 12) * POINT_WIDTH
                if (i - 12) >= 6:
                    x += BAR_WIDTH
                rect = pygame.Rect(x, BOARD_MARGIN, POINT_WIDTH, POINT_HEIGHT)
            rects.append(rect)
        return rects

    def draw_board(self):
        """Draws the Backgammon board, including the triangles, bar, and point numbers."""
        self.screen.fill(CREAM)
        board_rect = pygame.Rect(
            BOARD_MARGIN,
            BOARD_MARGIN,
            SCREEN_WIDTH - 2 * BOARD_MARGIN - 200,
            SCREEN_HEIGHT - 2 * BOARD_MARGIN,
        )
        pygame.draw.rect(self.screen, LIGHT_BROWN, board_rect)

        bar_x = BOARD_MARGIN + 6 * POINT_WIDTH
        bar_rect = pygame.Rect(
            bar_x, BOARD_MARGIN, BAR_WIDTH, SCREEN_HEIGHT - 2 * BOARD_MARGIN
        )
        pygame.draw.rect(self.screen, DARK_BROWN, bar_rect)

        for i in range(12):
            x = BOARD_MARGIN + i * POINT_WIDTH
            if i >= 6:
                x += BAR_WIDTH

            top_color = DARK_BROWN if i % 2 != 0 else TAN
            pygame.draw.polygon(
                self.screen,
                top_color,
                [
                    (x, BOARD_MARGIN),
                    (x + POINT_WIDTH, BOARD_MARGIN),
                    (x + POINT_WIDTH / 2, BOARD_MARGIN + POINT_HEIGHT),
                ],
            )

            bottom_color = TAN if i % 2 != 0 else DARK_BROWN
            pygame.draw.polygon(
                self.screen,
                bottom_color,
                [
                    (x, SCREEN_HEIGHT - BOARD_MARGIN),
                    (x + POINT_WIDTH, SCREEN_HEIGHT - BOARD_MARGIN),
                    (x + POINT_WIDTH / 2, SCREEN_HEIGHT - BOARD_MARGIN - POINT_HEIGHT),
                ],
            )

        for i in range(12):
            # Top numbers (13-24, left to right)
            num_text_top = str(13 + i)
            text_surface_top = self.font.render(num_text_top, True, WHITE)
            x_top = (
                BOARD_MARGIN
                + i * POINT_WIDTH
                + (POINT_WIDTH / 2)
                - (text_surface_top.get_width() / 2)
            )
            if i >= 6:
                x_top += BAR_WIDTH
            self.screen.blit(text_surface_top, (x_top, BOARD_MARGIN + 5))

            # Bottom numbers (12-1, left to right)
            num_text_bottom = str(12 - i)
            text_surface_bottom = self.font.render(num_text_bottom, True, WHITE)
            x_bottom = (
                BOARD_MARGIN
                + i * POINT_WIDTH
                + (POINT_WIDTH / 2)
                - (text_surface_bottom.get_width() / 2)
            )
            if i >= 6:
                x_bottom += BAR_WIDTH
            self.screen.blit(
                text_surface_bottom,
                (
                    x_bottom,
                    SCREEN_HEIGHT - BOARD_MARGIN - text_surface_bottom.get_height() - 5,
                ),
            )

    def draw_checkers(self):
        """Draws the checkers on the board based on the current game state."""
        if not self.game_data:
            return
        for i, (player, count) in enumerate(self.game_data["board"]["points"]):
            if count > 0:
                color = WHITE if player == 1 else BLACK
                for j in range(count):
                    if i >= 12:
                        x = BOARD_MARGIN + (i - 12) * POINT_WIDTH + POINT_WIDTH / 2
                        if (i - 12) >= 6:
                            x += BAR_WIDTH
                        y = BOARD_MARGIN + j * (2 * CHECKER_RADIUS) + CHECKER_RADIUS
                    else:
                        x = BOARD_MARGIN + (11 - i) * POINT_WIDTH + POINT_WIDTH / 2
                        if (11 - i) >= 6:
                            x += BAR_WIDTH
                        y = (
                            SCREEN_HEIGHT
                            - BOARD_MARGIN
                            - j * (2 * CHECKER_RADIUS)
                            - CHECKER_RADIUS
                        )

                    if j < 5:
                        pygame.draw.circle(
                            self.screen, color, (int(x), int(y)), CHECKER_RADIUS
                        )
                    elif j == 5:
                        num_text = self.font.render(
                            str(count), True, WHITE if player == 2 else BLACK
                        )
                        self.screen.blit(
                            num_text,
                            (
                                x - num_text.get_width() / 2,
                                y - num_text.get_height() / 2 - CHECKER_RADIUS,
                            ),
                        )
                        break

    def draw_bar_checkers(self):
        """Draws the checkers on the bar."""
        if not self.game_data:
            return
        bar_x = BOARD_MARGIN + 6 * POINT_WIDTH + BAR_WIDTH / 2
        for player_id, count in self.game_data["board"]["bar"].items():
            if count > 0:
                color = WHITE if int(player_id) == 1 else BLACK
                for i in range(count):
                    if int(player_id) == 1:  # White checkers on top part of the bar
                        y = (
                            BOARD_MARGIN
                            + 150
                            + i * (2 * CHECKER_RADIUS)
                            + CHECKER_RADIUS
                        )
                    else:  # Black checkers on bottom part of the bar
                        y = (
                            SCREEN_HEIGHT
                            - BOARD_MARGIN
                            - 150
                            - i * (2 * CHECKER_RADIUS)
                            - CHECKER_RADIUS
                        )
                    pygame.draw.circle(
                        self.screen, color, (int(bar_x), int(y)), CHECKER_RADIUS
                    )

    def draw_bear_off_area(self):
        """Draws the bear-off areas for both players."""
        if not self.game_data:
            return
        pygame.draw.rect(self.screen, TAN, self.bear_off_rects[1])
        pygame.draw.rect(self.screen, TAN, self.bear_off_rects[2])

        for player_id, count in self.game_data["board"]["home"].items():
            if count > 0:
                color = WHITE if int(player_id) == 1 else BLACK
                for i in range(count):
                    if int(player_id) == 1:  # White checkers (top right)
                        x = self.bear_off_rects[1].centerx
                        y = (
                            self.bear_off_rects[1].bottom
                            - (i * CHECKER_RADIUS * 1.5)
                            - CHECKER_RADIUS
                        )
                    else:  # Black checkers (bottom right)
                        x = self.bear_off_rects[2].centerx
                        y = (
                            self.bear_off_rects[2].bottom
                            - (i * CHECKER_RADIUS * 1.5)
                            - CHECKER_RADIUS
                        )

                    if y > self.bear_off_rects[int(player_id)].top + CHECKER_RADIUS:
                        pygame.draw.circle(
                            self.screen, color, (int(x), int(y)), CHECKER_RADIUS
                        )

    def draw_highlights(self):
        """Highlights the valid moves for the selected checker."""
        if not self.game_data:
            return
        current_player_ref = self.game_data.get("current_player")
        if not current_player_ref:
            return
        current_player = self.game_data[current_player_ref]
        player_id = 1 if current_player["color"] == "WHITE" else 2

        for move in self.highlighted_moves:
            if move == "bear_off":
                highlight_surface = pygame.Surface(
                    (
                        self.bear_off_rects[player_id].width,
                        self.bear_off_rects[player_id].height,
                    ),
                    pygame.SRCALPHA,
                )
                highlight_surface.fill(HIGHLIGHT_COLOR)
                self.screen.blit(
                    highlight_surface,
                    self.bear_off_rects[player_id].topleft,
                )
            else:
                to_point = move
                highlight_surface = pygame.Surface(
                    (
                        self.point_rects[to_point].width,
                        self.point_rects[to_point].height,
                    ),
                    pygame.SRCALPHA,
                )
                highlight_surface.fill(HIGHLIGHT_COLOR)
                self.screen.blit(highlight_surface, self.point_rects[to_point].topleft)

    def draw_info_panel(self):
        """Draws the information panel, which displays game state information."""
        panel_x = SCREEN_WIDTH - 200 - BOARD_MARGIN
        panel_y = BOARD_MARGIN
        panel_rect = pygame.Rect(
            panel_x, panel_y, 200, SCREEN_HEIGHT - 2 * BOARD_MARGIN
        )
        pygame.draw.rect(self.screen, LIGHT_BROWN, panel_rect)

        # Draw a separating line
        pygame.draw.line(
            self.screen,
            DARK_BROWN,
            (panel_x - 5, panel_y),
            (panel_x - 5, panel_y + panel_rect.height),
            2,
        )

        if self.game_data and self.game_data.get("current_player"):
            current_player_ref = self.game_data["current_player"]
            current_player = self.game_data[current_player_ref]
            player_name = current_player["name"]
            player_color = "White" if current_player["color"] == "WHITE" else "Black"

            # Truncate long player names
            if len(player_name) > 10:
                player_name = player_name[:10] + "..."

            # (userName)'s Turn
            turn_text_str = f"{player_name}'s Turn"
            turn_text = self.font.render(turn_text_str, True, BLACK)
            text_x = panel_x + (panel_rect.width - turn_text.get_width()) / 2
            self.screen.blit(turn_text, (text_x, panel_y + 20))

            # (White)/(Black)
            color_text = self.font.render(player_color, True, BLACK)
            color_text_x = panel_x + (panel_rect.width - color_text.get_width()) / 2
            self.screen.blit(color_text, (color_text_x, panel_y + 50))

            # Roll Dice / Numbers
            roll_button = pygame.Rect(panel_x + 25, panel_y + 110, 150, 50)
            if not self.dice_rolled_this_turn:
                pygame.draw.rect(self.screen, DARK_BROWN, roll_button)
                roll_text = self.font.render("Roll Dice", True, WHITE)
                roll_text_rect = roll_text.get_rect(center=roll_button.center)
                self.screen.blit(roll_text, roll_text_rect)
            else:
                moves = current_player["available_moves"]
                dice_text_str = str(moves)
                dice_text = self.font.render(dice_text_str, True, BLACK)
                text_x = panel_x + (panel_rect.width - dice_text.get_width()) / 2
                self.screen.blit(dice_text, (text_x, panel_y + 125))

            # Bear off counters
            home_white = self.game_data["board"]["home"].get("1", 0)
            home_black = self.game_data["board"]["home"].get("2", 0)

            bear_off_title = self.font.render("Borne Off", True, BLACK)
            title_x = panel_x + (panel_rect.width - bear_off_title.get_width()) / 2
            self.screen.blit(bear_off_title, (title_x, panel_y + 200))

            # White bear off counter
            pygame.draw.rect(self.screen, WHITE, (panel_x + 25, panel_y + 240, 50, 50))
            white_count_text = self.font.render(str(home_white), True, BLACK)
            self.screen.blit(white_count_text, (panel_x + 40, panel_y + 255))

            # Black bear off counter
            pygame.draw.rect(self.screen, BLACK, (panel_x + 125, panel_y + 240, 50, 50))
            black_count_text = self.font.render(str(home_black), True, WHITE)
            self.screen.blit(black_count_text, (panel_x + 140, panel_y + 255))

            # Bear Off Button
            can_bear_off = "bear_off" in self.highlighted_moves
            button_color = DARK_BROWN if can_bear_off else LIGHT_BROWN
            pygame.draw.rect(self.screen, button_color, self.bear_off_button)
            bear_off_text = self.font.render(
                "Bear Off", True, WHITE if can_bear_off else BLACK
            )
            bear_off_text_rect = bear_off_text.get_rect(
                center=self.bear_off_button.center
            )
            self.screen.blit(bear_off_text, bear_off_text_rect)

    def draw_start_screen(self):
        """Draws the start screen, which prompts for player names."""
        self.screen.fill(CREAM)
        title_text = self.font.render("Backgammon", True, BLACK)
        self.screen.blit(
            title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100)
        )

        pygame.draw.rect(self.screen, WHITE, self.input_boxes["player1"])
        pygame.draw.rect(self.screen, BLACK, self.input_boxes["player1"], 2)
        player1_text = self.font.render(self.player1_name, True, BLACK)
        self.screen.blit(
            player1_text,
            (self.input_boxes["player1"].x + 5, self.input_boxes["player1"].y + 5),
        )
        player1_label = self.font.render("Player 1 (White):", True, BLACK)
        self.screen.blit(
            player1_label,
            (self.input_boxes["player1"].x - 200, self.input_boxes["player1"].y + 5),
        )

        pygame.draw.rect(self.screen, WHITE, self.input_boxes["player2"])
        pygame.draw.rect(self.screen, BLACK, self.input_boxes["player2"], 2)
        player2_text = self.font.render(self.player2_name, True, BLACK)
        self.screen.blit(
            player2_text,
            (self.input_boxes["player2"].x + 5, self.input_boxes["player2"].y + 5),
        )
        player2_label = self.font.render("Player 2 (Black):", True, BLACK)
        self.screen.blit(
            player2_label,
            (self.input_boxes["player2"].x - 200, self.input_boxes["player2"].y + 5),
        )

        pygame.draw.rect(self.screen, DARK_BROWN, self.start_button)
        start_text = self.font.render("Start Game", True, WHITE)
        start_text_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_text_rect)

    def draw_winner_screen(self):
        """Draws the winner screen."""
        self.screen.fill(CREAM)
        winner = self.game_data.get("winner")
        winner_name = winner["name"] if winner else "Unknown"

        title_text = self.font.render(f"{winner_name} Wins!", True, BLACK)
        self.screen.blit(
            title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200)
        )

        pygame.draw.rect(self.screen, DARK_BROWN, self.play_again_button)
        play_again_text = self.font.render("Play Again", True, WHITE)
        play_again_text_rect = play_again_text.get_rect(
            center=self.play_again_button.center
        )
        self.screen.blit(play_again_text, play_again_text_rect)

    def draw_resume_screen(self):
        """Draws the screen asking to resume or start a new game."""
        self.screen.fill(CREAM)
        title_text = self.font.render("Resume Game?", True, BLACK)
        self.screen.blit(
            title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150)
        )

        pygame.draw.rect(self.screen, DARK_BROWN, self.resume_button)
        resume_text = self.font.render("Resume Game", True, WHITE)
        resume_text_rect = resume_text.get_rect(center=self.resume_button.center)
        self.screen.blit(resume_text, resume_text_rect)

        pygame.draw.rect(self.screen, DARK_BROWN, self.start_new_button)
        new_game_text = self.font.render("Start New Game", True, WHITE)
        new_game_text_rect = new_game_text.get_rect(
            center=self.start_new_button.center
        )
        self.screen.blit(new_game_text, new_game_text_rect)

    def show_no_moves_message(self):
        """Displays a message indicating that there are no valid moves."""
        message_text = self.font.render("No valid moves. Switching turns.", True, BLACK)
        message_rect = message_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        )

        # Create a semi-transparent background for the message
        background_rect = message_rect.inflate(20, 20)
        background_surface = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background_surface.fill((255, 255, 255, 180))

        self.screen.blit(background_surface, background_rect)
        self.screen.blit(message_text, message_rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # Display message for 2 seconds

    def handle_click(self, pos):
        """Handles mouse clicks for checker movement and UI interaction."""
        panel_x = SCREEN_WIDTH - 200 - BOARD_MARGIN
        panel_y = BOARD_MARGIN
        roll_button = pygame.Rect(panel_x + 25, panel_y + 110, 150, 50)

        if roll_button.collidepoint(pos) and not self.dice_rolled_this_turn:
            self.game_data = self.api_client.roll_dice()
            self.dice_rolled_this_turn = True
            if self.game_data and self.game_data["turn_was_skipped"]:
                self.show_no_moves_message()
            return

        if (
            "bear_off" in self.highlighted_moves
            and self.bear_off_button.collidepoint(pos)
            and self.selected_checker_point is not None
        ):
            self.game_data = self.api_client.bear_off(self.selected_checker_point)
            if self.game_data and self.game_data.get("turn_was_skipped"):
                self.show_no_moves_message()
            self.selected_checker_point = None
            self.highlighted_moves = []
            return

        if self.selected_checker_point is not None:
            for move in self.highlighted_moves:
                if isinstance(move, int) and self.point_rects[move].collidepoint(pos):
                    self.game_data = self.api_client.move(
                        self.selected_checker_point, move
                    )
                    if self.game_data and self.game_data.get("turn_was_skipped"):
                        self.show_no_moves_message()
                    self.selected_checker_point = None
                    self.highlighted_moves = []
                    return

        current_player_ref = self.game_data["current_player"]
        current_player = self.game_data[current_player_ref]
        player_id_str = "1" if current_player["color"] == "WHITE" else "2"
        if int(self.game_data["board"]["bar"][player_id_str]) > 0:
            if self.bar_rects[int(player_id_str)].collidepoint(pos):
                self.selected_checker_point = "bar"
                self.highlighted_moves = self.api_client.get_valid_moves("bar")
            return

        for i, rect in enumerate(self.point_rects):
            if rect.collidepoint(pos):
                self.selected_checker_point = i
                self.highlighted_moves = self.api_client.get_valid_moves(i)
                return

    def run(self):
        """The main game loop."""
        self.game_data = self.api_client.get_game()
        if self.game_data:
            self.game_state = "RESUME_SCREEN"
        else:
            self.game_state = "START_SCREEN"
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()

                if self.game_state == "RESUME_SCREEN":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.resume_button.collidepoint(event.pos):
                            self.game_state = "GAME_SCREEN"
                        elif self.start_new_button.collidepoint(event.pos):
                            self.game_state = "START_SCREEN"
                            self.game_data = None
                elif self.game_state == "START_SCREEN":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.input_boxes["player1"].collidepoint(event.pos):
                            self.active_input = "player1"
                        elif self.input_boxes["player2"].collidepoint(event.pos):
                            self.active_input = "player2"
                        elif self.start_button.collidepoint(event.pos):
                            if self.player1_name and self.player2_name:
                                self.game_data = self.api_client.new_game(
                                    self.player1_name, self.player2_name
                                )
                                if self.game_data:
                                    self.game_state = "GAME_SCREEN"

                    if event.type == pygame.KEYDOWN:
                        if self.active_input == "player1":
                            if event.key == pygame.K_BACKSPACE:
                                self.player1_name = self.player1_name[:-1]
                            else:
                                self.player1_name += event.unicode
                        elif self.active_input == "player2":
                            if event.key == pygame.K_BACKSPACE:
                                self.player2_name = self.player2_name[:-1]
                            else:
                                self.player2_name += event.unicode

                elif self.game_state == "GAME_SCREEN":
                    if self.game_data:
                        current_player_ref = self.game_data.get("current_player")
                        if current_player_ref:
                            current_player = self.game_data[current_player_ref]
                            if current_player["remaining_moves"] == 0:
                                self.dice_rolled_this_turn = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            self.handle_click(event.pos)
                        if self.game_data and self.game_data["winner"]:
                            self.game_state = "WINNER_SCREEN"

                elif self.game_state == "WINNER_SCREEN":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.play_again_button.collidepoint(event.pos):
                            self.game_state = "START_SCREEN"
                            self.player1_name = ""
                            self.player2_name = ""
                            self.game_data = None

            if self.game_state == "RESUME_SCREEN":
                self.draw_resume_screen()
            elif self.game_state == "START_SCREEN":
                self.draw_start_screen()
            elif self.game_state == "GAME_SCREEN":
                self.draw_board()
                self.draw_checkers()
                self.draw_bar_checkers()
                self.draw_bear_off_area()
                self.draw_highlights()
                self.draw_info_panel()
            elif self.game_state == "WINNER_SCREEN":
                self.draw_winner_screen()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    ui = BackgammonUI()
    ui.run()
