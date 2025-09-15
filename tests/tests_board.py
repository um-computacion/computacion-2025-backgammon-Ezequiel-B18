import unittest
from core.board import Board

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_board_initialization(self):
        """Test that a new Board object is initialized with correct starting positions"""
        self.assertIsNotNone(self.board)
        
        # Check that the board has 24 points numbered from 0 to 23
        self.assertEqual(len(self.board.points), 24)
        
        # Check the starting position for white checkers (player 1)
        self.assertEqual(self.board.points[0], (1, 2))  # 2 white checkers on point 0
        self.assertEqual(self.board.points[11], (1, 5)) # 5 white checkers on point 11
        self.assertEqual(self.board.points[16], (1, 3)) # 3 white checkers on point 16
        self.assertEqual(self.board.points[18], (1, 5)) # 5 white checkers on point 18
        
        # Check the starting position for black checkers (player 2)
        self.assertEqual(self.board.points[23], (2, 2)) # 2 black checkers on point 23
        self.assertEqual(self.board.points[12], (2, 5)) # 5 black checkers on point 12
        self.assertEqual(self.board.points[7], (2, 3))  # 3 black checkers on point 7
        self.assertEqual(self.board.points[5], (2, 5))  # 5 black checkers on point 5
        
        # Check that both bars start empty
        self.assertEqual(self.board.bar[1], 0)  # No white checkers on the bar
        self.assertEqual(self.board.bar[2], 0)  # No black checkers on the bar
        
        # Check that both homes start empty
        self.assertEqual(self.board.home[1], 0)  # No white checkers in home
        self.assertEqual(self.board.home[2], 0)  # No black checkers in home

    def test_move_checker(self):
        """Test moving a checker from one point to another"""
        # Move a white checker from point 0 to point 3
        self.assertTrue(self.board.move_checker(1, 0, 3))
        self.assertEqual(self.board.points[0], (1, 1))  # One white checker left on point 0
        self.assertEqual(self.board.points[3], (1, 1))  # One white checker now on point 3
        
        # Move a black checker from point 5 to point 3
        self.assertTrue(self.board.move_checker(2, 5, 3))
        self.assertEqual(self.board.points[5], (2, 4))  # Four black checkers left on point 5
        self.assertEqual(self.board.points[3], (2, 1))  # Point 3 now has one black checker (hit the white)
        
        # Check that the white checker was sent to the bar
        self.assertEqual(self.board.bar[1], 1)  # One white checker on the bar

    def test_checkers_on_bar(self):
        """Test that checkers on the bar must be moved first"""
        # Put a white checker on the bar
        self.board.bar[1] = 1
        
        # Try to move a regular checker (should fail because bar must be emptied first)
        self.assertFalse(self.board.is_valid_move(1, 0, 3))
        
        # Move the checker from the bar (for white, entering from point 0-5)
        self.assertTrue(self.board.enter_from_bar(1, 3))
        self.assertEqual(self.board.bar[1], 0)  # Bar now empty
        self.assertEqual(self.board.points[3], (1, 1))  # Checker entered at point 3

    def test_bearing_off(self):
        """Test bearing off checkers (moving them to home)"""
        # Setup: Move all white checkers to the home board (last quadrant)
        self.board = Board(test_bearing_off=True)  # Special test setup with all checkers in home board
        
        # Count white checkers in the home board
        white_checkers_in_home_board = sum(count for player, count in 
                                          [self.board.points[i] for i in range(18, 24)]
                                          if player == 1)
        self.assertEqual(white_checkers_in_home_board, 15)  # All 15 white checkers in home board
        
        # Bear off a checker from point 23
        self.assertTrue(self.board.bear_off(1, 23))
        self.assertEqual(self.board.points[23], (1, 2))  # One checker removed
        self.assertEqual(self.board.home[1], 1)  # One checker in home
        
        # Try to bear off when checkers exist on a higher point (should fail)
        self.assertFalse(self.board.bear_off(1, 18))  # Invalid because checkers exist on higher points
        
        # Bear off remaining checkers
        self.assertTrue(self.board.bear_off(1, 23))
        self.assertTrue(self.board.bear_off(1, 23))
        self.assertEqual(self.board.points[23], (0, 0))  # No more checkers
        self.assertEqual(self.board.home[1], 3)  # Three checkers in home

    def test_check_winner(self):
        """Test checking for a winner"""
        # No winner at the start
        self.assertEqual(self.board.check_winner(), 0)
        
        # Create a fresh board for this test
        test_board = Board()
        
        # Put all white checkers in home
        test_board.home[1] = 15
        self.assertEqual(test_board.check_winner(), 1)
        
        # Reset and put all black checkers in home
        test_board.home[1] = 0
        test_board.home[2] = 15
        self.assertEqual(test_board.check_winner(), 2)
        
        # Both players with all checkers borne off (impossible scenario)
        test_board.home[1] = 15
        test_board.home[2] = 15
        # In this case, we still return the first winner found (white)
        self.assertEqual(test_board.check_winner(), 1)
    
    def test_get_player_at_point(self):
        """Test getting the player owning checkers at a point"""
        self.assertEqual(self.board.get_player_at_point(0), 1)  # White at point 0
        self.assertEqual(self.board.get_player_at_point(5), 2)  # Black at point 5
        self.assertEqual(self.board.get_player_at_point(1), 0)  # No checkers at point 1
    
    def test_get_checkers_count(self):
        """Test getting the number of checkers at a point"""
        self.assertEqual(self.board.get_checkers_count(0), 2)   # 2 checkers at point 0
        self.assertEqual(self.board.get_checkers_count(11), 5)  # 5 checkers at point 11
        self.assertEqual(self.board.get_checkers_count(1), 0)   # No checkers at point 1

    def test_all_checkers_in_home_board(self):
        """Test checking if all player's checkers are in their home board"""
        # At the start, not all checkers are in home board
        self.assertFalse(self.board.all_checkers_in_home_board(1))
        self.assertFalse(self.board.all_checkers_in_home_board(2))
        
        # Setup a test case with all white checkers in home board
        self.board = Board(test_bearing_off=True)
        self.assertTrue(self.board.all_checkers_in_home_board(1))
        # Black checkers are also in their home board in this test setup
        self.assertTrue(self.board.all_checkers_in_home_board(2))
