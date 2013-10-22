from .square import Square


class CommunityChest(Square):
    '''
    Represents one of the Community Chest squares.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.COMMUNITY_CHEST)

