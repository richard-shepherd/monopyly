from monopyly import Board


def test_number_of_squares():
    '''
    Tests that the board has the number of squares we expect.
    '''
    board = Board()
    assert len(board.squares) == Board.NUMBER_OF_SQUARES

