from monopyly import Board
from monopyly import Square


def test_number_of_squares():
    '''
    Tests that the board has the number of squares we expect.
    '''
    board = Board()
    assert len(board.squares) == Board.NUMBER_OF_SQUARES


def test_square_indexes():
    '''
    Tests that the board indexes are as we expect.
    '''
    board = Board()
    assert board.get_index_list(Square.Name.GO) == [0]
    assert board.get_index_list(Square.Name.OLD_KENT_ROAD) == [1]
    assert board.get_index_list(Square.Name.COMMUNITY_CHEST) == [2, 17, 33]
    assert board.get_index_list(Square.Name.CHANCE) == [7, 22, 36]
    assert board.get_index_list(Square.Name.MARYLEBONE_STATION) == [15]
    assert board.get_index_list(Square.Name.TRAFALGAR_SQUARE) == [24]
    assert board.get_index_list(Square.Name.MAYFAIR) == [39]
