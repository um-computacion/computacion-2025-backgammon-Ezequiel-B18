class Board:
    """
    Represents a backgammon board.
    Handles the state of the board, moving checkers, and checking game conditions.
    """
    def __init__(self, test_bearing_off=False):
        """
        Initialize the backgammon board with the standard starting position.
        
        Args:
            test_bearing_off (bool): If True, set up a test position with all white checkers in home board
        """
        # Points are represented as tuples (player, count)
        # player: 0 = empty, 1 = white, 2 = black
        # count: number of checkers at that point
        self.points = [(0, 0) for _ in range(24)]
        
        # Bar holds checkers that have been hit
        # Index 1 = white, 2 = black
        self.bar = {1: 0, 2: 0}
        
        # Home holds checkers that have been borne off
        self.home = {1: 0, 2: 0}
        
        if test_bearing_off:
            # Special setup for bearing off tests
            # All white checkers in home board
            self.points[18] = (1, 2)
            self.points[19] = (1, 2)
            self.points[20] = (1, 3)
            self.points[21] = (1, 2)
            self.points[22] = (1, 3)
            self.points[23] = (1, 3)
            
            # All black checkers in their home board
            self.points[0] = (2, 2)
            self.points[1] = (2, 2)
            self.points[2] = (2, 3)
            self.points[3] = (2, 2)
            self.points[4] = (2, 3)
            self.points[5] = (2, 3)
        else:
            # Standard starting position
            # White (player 1) starting positions
            self.points[0] = (1, 2)   # 2 checkers on point 0
            self.points[11] = (1, 5)  # 5 checkers on point 11
            self.points[16] = (1, 3)  # 3 checkers on point 16
            self.points[18] = (1, 5)  # 5 checkers on point 18
            
            # Black (player 2) starting positions
            self.points[23] = (2, 2)  # 2 checkers on point 23
            self.points[12] = (2, 5)  # 5 checkers on point 12
            self.points[7] = (2, 3)   # 3 checkers on point 7
            self.points[5] = (2, 5)   # 5 checkers on point 5

    def get_player_at_point(self, point):
        """
        Get the player who has checkers at the given point.
        
        Args:
            point (int): Point index (0-23)
            
        Returns:
            int: Player number (0 if empty, 1 for white, 2 for black)
        """
        return self.points[point][0]

    def get_checkers_count(self, point):
        """
        Get the number of checkers at the given point.
        
        Args:
            point (int): Point index (0-23)
            
        Returns:
            int: Number of checkers at the point
        """
        return self.points[point][1]

    def is_valid_move(self, player, from_point, to_point):
        """
        Check if a move is valid.
        
        Args:
            player (int): Player making the move (1 for white, 2 for black)
            from_point (int): Starting point index (0-23)
            to_point (int): Target point index (0-23)
            
        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Check if there are checkers on the bar that must be entered first
        if self.bar[player] > 0:
            return False
        
        # Check if the source point has checkers belonging to the player
        if self.points[from_point][0] != player or self.points[from_point][1] == 0:
            return False
        
        # Check if the target point is blocked by the opponent
        # A point is blocked if it has 2 or more checkers of the opponent
        target_player, target_count = self.points[to_point]
        if target_player != 0 and target_player != player and target_count >= 2:
            return False
        
        return True

    def move_checker(self, player, from_point, to_point):
        """
        Move a checker from one point to another.
        
        Args:
            player (int): Player making the move (1 for white, 2 for black)
            from_point (int): Starting point index (0-23)
            to_point (int): Target point index (0-23)
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        if not self.is_valid_move(player, from_point, to_point):
            return False
        
        # Remove checker from source point
        source_player, source_count = self.points[from_point]
        if source_count == 1:
            # Last checker, point becomes empty
            self.points[from_point] = (0, 0)
        else:
            # Reduce count
            self.points[from_point] = (source_player, source_count - 1)
        
        # Handle target point
        target_player, target_count = self.points[to_point]
        if target_player == 0 or target_player == player:
            # Empty point or same player, add checker
            self.points[to_point] = (player, target_count + 1)
        elif target_count == 1:
            # Hit opponent's blot
            self.points[to_point] = (player, 1)
            self.bar[target_player] += 1
        
        return True

    def enter_from_bar(self, player, point):
        """
        Enter a checker from the bar.
        
        Args:
            player (int): Player entering the checker (1 for white, 2 for black)
            point (int): Target point index (0-23)
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        # Check if player has checkers on the bar
        if self.bar[player] == 0:
            return False
        
        # Check if entry point is valid
        # For white (player 1), enter at points 0-5
        # For black (player 2), enter at points 18-23
        valid_entry_points = range(0, 6) if player == 1 else range(18, 24)
        if point not in valid_entry_points:
            return False
        
        # Check if the entry point is not blocked
        target_player, target_count = self.points[point]
        if target_player != 0 and target_player != player and target_count >= 2:
            return False
        
        # Remove checker from bar
        self.bar[player] -= 1
        
        # Handle target point
        if target_player == 0:
            # Empty point
            self.points[point] = (player, 1)
        elif target_player == player:
            # Same player, add checker
            self.points[point] = (player, target_count + 1)
        else:  # target_player != player and target_count == 1
            # Hit opponent's blot
            self.points[point] = (player, 1)
            self.bar[target_player] += 1
        
        return True

    def all_checkers_in_home_board(self, player):
        """
        Check if all of a player's checkers are in their home board.
        
        Args:
            player (int): Player to check (1 for white, 2 for black)
            
        Returns:
            bool: True if all checkers are in the home board, False otherwise
        """
        # Home board is points 18-23 for white (player 1)
        # Home board is points 0-5 for black (player 2)
        home_board = range(18, 24) if player == 1 else range(0, 6)
        
        # Check if there are any checkers on the bar
        if self.bar[player] > 0:
            return False
        
        # Check all points outside the home board
        non_home_board = range(0, 18) if player == 1 else range(6, 24)
        for point in non_home_board:
            if self.points[point][0] == player and self.points[point][1] > 0:
                return False
        
        return True

    def bear_off(self, player, point):
        """
        Bear off a checker from the board.
        
        Args:
            player (int): Player bearing off (1 for white, 2 for black)
            point (int): Point index (0-23) from which to bear off
            
        Returns:
            bool: True if bearing off was successful, False otherwise
        """
        # Check if all checkers are in the home board
        if not self.all_checkers_in_home_board(player):
            return False
        
        # Check if point is in player's home board
        home_board = range(18, 24) if player == 1 else range(0, 6)
        if point not in home_board:
            return False
        
        # Check if the point has checkers belonging to the player
        if self.points[point][0] != player or self.points[point][1] == 0:
            return False
        
        # For white: check if there are checkers on higher points (18-22 if trying to bear off from 18)
        # For black: check if there are checkers on lower points (1-4 if trying to bear off from 0)
        if player == 1:
            higher_points = range(18, point)
            for p in higher_points:
                if self.points[p][0] == player and self.points[p][1] > 0:
                    return False
        else:  # player == 2
            lower_points = range(point + 1, 6)
            for p in lower_points:
                if self.points[p][0] == player and self.points[p][1] > 0:
                    return False
        
        # Bear off the checker
        count = self.points[point][1]
        if count == 1:
            self.points[point] = (0, 0)  # Point becomes empty
        else:
            self.points[point] = (player, count - 1)  # Reduce count
        
        # Add checker to home
        self.home[player] += 1
        
        return True

    def check_winner(self):
        """
        Check if there is a winner.
        
        Returns:
            int: 0 if no winner, 1 if white wins, 2 if black wins
        """
        if self.home[1] == 15:
            return 1
        elif self.home[2] == 15:
            return 2
        else:
            return 0
