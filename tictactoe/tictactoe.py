"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return  [[EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    sum_X = 0
    sum_O = 0
    for row in board:
        print(row)
        for element in row:
            if element == "X":
                sum_X += 1
            elif element == "O":
                sum_O += 1
    if sum_X > sum_O:
        return "O"
    else:
        return "X"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible = set()
    pos_row = 0
    for row in board:
        pos_element = 0
        for element in row:
            if element == None:
                possible.add((pos_row,pos_element))
            pos_element += 1
        pos_row += 1
    return possible


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    possible = actions(board)
    if action not in possible:
        raise Exception("not a valid move")
    else:
        copy_board = copy.deepcopy(board)
        row = list(action)[0]
        column = list(action)[1]

        sign = player(board)
        copy_board[row][column] = sign
        return copy_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check horizontal
    for row in range(0,3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] != None:
            return board[row][0]
    
    # check vertical
        if board[0][row] == board[1][row] == board[2][row] and board[0][row] != None:
            return board[0][row]
    
    # check diagonal
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != None:
        return board[0][0]
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] != None:
        return board[0][2]


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    board_state = actions(board)
    if winner(board) != None or len(board_state) == 0:
        return True
    else:
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0
    

def max_value(board):
    value = -1000
    if terminal(board):
        return utility(board)
    for action in actions(board):
        value = max(value, min_value(result(board, action)))
    return value

def min_value(board):
    value = 1000
    if terminal(board):
        return utility(board)
    for action in actions(board):
        value = min(value, max_value(result(board, action)))
    return value

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    move_X = -math.inf
    move_O = math.inf

    if terminal(board) == True:
        return None
    if player(board) == "X":
        for action in actions(board):
            maximum = min_value(result(board, action))
            if maximum > move_X:
                best_action = action
                move_X = maximum
        return best_action
    else:
        for action in actions(board):
            minimum = max_value(result(board, action))
            if minimum < move_O:
                best_action = action
                move_O = minimum
        return best_action