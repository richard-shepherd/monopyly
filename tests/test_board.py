from monopyly import *


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
    assert board.get_index(Square.Name.GO) == 0
    assert board.get_index(Square.Name.OLD_KENT_ROAD) == 1
    assert board.get_index_list(Square.Name.COMMUNITY_CHEST) == [2, 17, 33]
    assert board.get_index_list(Square.Name.CHANCE) == [7, 22, 36]
    assert board.get_index(Square.Name.MARYLEBONE_STATION) == 15
    assert board.get_index(Square.Name.TRAFALGAR_SQUARE) == 24
    assert board.get_index(Square.Name.MAYFAIR) == 39


def test_sets():
    '''
    Tests that the properties are in the correct sets.
    '''
    board = Board()

    stations_set = board.get_properties_for_set(Property.Set.STATION)
    assert len(stations_set) == 4
    assert stations_set[0].name == Square.Name.KINGS_CROSS_STATION
    assert stations_set[1].name == Square.Name.MARYLEBONE_STATION
    assert stations_set[2].name == Square.Name.FENCHURCH_STREET_STATION
    assert stations_set[3].name == Square.Name.LIVERPOOL_STREET_STATION

    utility_set = board.get_properties_for_set(Property.Set.UTILITY)
    assert len(utility_set) == 2
    assert utility_set[0].name == Square.Name.ELECTRIC_COMPANY
    assert utility_set[1].name == Square.Name.WATER_WORKS

    brown_set = board.get_properties_for_set(Property.Set.BROWN)
    assert len(brown_set) == 2
    assert brown_set[0].name == Square.Name.OLD_KENT_ROAD
    assert brown_set[1].name == Square.Name.WHITECHAPEL_ROAD

    light_blue_set = board.get_properties_for_set(Property.Set.LIGHT_BLUE)
    assert len(light_blue_set) == 3
    assert light_blue_set[0].name == Square.Name.THE_ANGEL_ISLINGTON
    assert light_blue_set[1].name == Square.Name.EUSTON_ROAD
    assert light_blue_set[2].name == Square.Name.PENTONVILLE_ROAD

    purple_set = board.get_properties_for_set(Property.Set.PURPLE)
    assert len(purple_set) == 3
    assert purple_set[0].name == Square.Name.PALL_MALL
    assert purple_set[1].name == Square.Name.WHITEHALL
    assert purple_set[2].name == Square.Name.NORTHUMBERLAND_AVENUE

    orange_set = board.get_properties_for_set(Property.Set.ORANGE)
    assert len(orange_set) == 3
    assert orange_set[0].name == Square.Name.BOW_STREET
    assert orange_set[1].name == Square.Name.MARLBOROUGH_STREET
    assert orange_set[2].name == Square.Name.VINE_STREET

    red_set = board.get_properties_for_set(Property.Set.RED)
    assert len(red_set) == 3
    assert red_set[0].name == Square.Name.STRAND
    assert red_set[1].name == Square.Name.FLEET_STREET
    assert red_set[2].name == Square.Name.TRAFALGAR_SQUARE

    yellow_set = board.get_properties_for_set(Property.Set.YELLOW)
    assert len(yellow_set) == 3
    assert yellow_set[0].name == Square.Name.LEICESTER_SQUARE
    assert yellow_set[1].name == Square.Name.COVENTRY_STREET
    assert yellow_set[2].name == Square.Name.PICCADILLY

    green_set = board.get_properties_for_set(Property.Set.GREEN)
    assert len(green_set) == 3
    assert green_set[0].name == Square.Name.REGENT_STREET
    assert green_set[1].name == Square.Name.OXFORD_STREET
    assert green_set[2].name == Square.Name.BOND_STREET

    dark_blue_set = board.get_properties_for_set(Property.Set.DARK_BLUE)
    assert len(dark_blue_set) == 2
    assert dark_blue_set[0].name == Square.Name.PARK_LANE
    assert dark_blue_set[1].name == Square.Name.MAYFAIR








    