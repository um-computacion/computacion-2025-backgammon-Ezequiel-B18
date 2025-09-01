from enum import Enum, auto

class CheckerColor(Enum):
    """Enum representing the possible colors of a checker."""
    WHITE = auto()
    BLACK = auto()

class CheckerState(Enum):
    """Enum representing the possible states of a checker."""
    ON_BOARD = auto()  # Checker is on the board
    ON_BAR = auto()    # Checker is on the bar (after being hit)
    BORNE_OFF = auto() # Checker has been borne off (removed from board)

class Checker:
    """
    Represents a backgammon checker (piece).
    Handles checker state, position, and movement rules.
    """
    def __init__(self, color):
        """
        Initialize a checker with a specific color.
        
        Args:
            color (CheckerColor): The color of the checker (WHITE or BLACK)
        """
        self.color = color
        self.state = CheckerState.ON_BOARD
        self.position = None
    
    def set_position(self, position):
        """
        Set the initial position of the checker on the board.
        
        Args:
            position (int): Point index (0-23) where the checker is placed
        """
        if not (0 <= position <= 23):
            raise ValueError(f"Position must be between 0-23, got {position}")
        
        self.position = position
        self.state = CheckerState.ON_BOARD
    
    def move_to_position(self, new_position):
        """
        Move the checker to a new position on the board.
        
        Args:
            new_position (int): Target point index (0-23)
        """
        if not (0 <= new_position <= 23):
            raise ValueError(f"Position must be between 0-23, got {new_position}")
        
        self.position = new_position
        self.state = CheckerState.ON_BOARD
    
    def calculate_new_position(self, dice_value):
        """
        Calculate the new position based on a dice value.
        White checkers move in increasing order (0->23)
        Black checkers move in decreasing order (23->0)
        
        Args:
            dice_value (int): Value of the dice roll (1-6)
            
        Returns:
            int: The new position after the move
        """
        if self.state != CheckerState.ON_BOARD:
            raise ValueError("Cannot calculate new position: checker not on board")
        
        if self.position is None:
            raise ValueError("Cannot calculate new position: no current position")
            
        if self.color == CheckerColor.WHITE:
            return self.position + dice_value
        else:  # BLACK
            return self.position - dice_value
    
    def send_to_bar(self):
        """Send this checker to the bar (after being hit)"""
        self.state = CheckerState.ON_BAR
        self.position = None
    
    def enter_from_bar(self, position):
        """
        Enter the checker from the bar to the board.
        
        Args:
            position (int): Target point index (0-23)
            
        Raises:
            ValueError: If the position is not a valid entry point for this color
        """
        if self.state != CheckerState.ON_BAR:
            raise ValueError("Cannot enter from bar: checker not on bar")
        
        # White enters on points 0-5, Black enters on points 18-23
        valid_entry_points = range(0, 6) if self.color == CheckerColor.WHITE else range(18, 24)
        
        if position not in valid_entry_points:
            valid_range = "0-5" if self.color == CheckerColor.WHITE else "18-23"
            raise ValueError(f"{self.color.name} checkers must enter on points {valid_range}")
        
        self.position = position
        self.state = CheckerState.ON_BOARD
    
    def bear_off(self):
        """
        Bear off the checker (remove it from the board).
        
        Raises:
            ValueError: If the checker is not in its home board
        """
        if self.state != CheckerState.ON_BOARD:
            raise ValueError("Cannot bear off: checker not on board")
        
        if not self.is_in_home_board():
            raise ValueError("Cannot bear off: checker not in home board")
        
        self.state = CheckerState.BORNE_OFF
        self.position = None
    
    def is_in_home_board(self):
        """
        Check if the checker is in its home board.
        
        Returns:
            bool: True if the checker is in its home board, False otherwise
        """
        if self.state != CheckerState.ON_BOARD or self.position is None:
            return False
        
        # White home board is points 18-23
        if self.color == CheckerColor.WHITE:
            return 18 <= self.position <= 23
        
        # Black home board is points 0-5
        return 0 <= self.position <= 5
    
    def can_bear_off_with_value(self, dice_value):
        """
        Check if the checker can be borne off with a specific dice value.
        
        Args:
            dice_value (int): Value of the dice roll (1-6)
            
        Returns:
            bool: True if the checker can be borne off with this value, False otherwise
        """
        if not self.is_in_home_board():
            return False
        
        # For white, calculate distance to bear off (24 - position)
        if self.color == CheckerColor.WHITE:
            distance_to_bear_off = 24 - self.position
            return dice_value >= distance_to_bear_off
        
        # For black, position + 1 is the distance
        return dice_value >= self.position + 1
    
    def __str__(self):
        """String representation of the checker"""
        color_name = "White" if self.color == CheckerColor.WHITE else "Black"
        state_name = self.state.name
        pos_str = f"pos={self.position}"
        return f"{color_name}({state_name}, {pos_str})"
