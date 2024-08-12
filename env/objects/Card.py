class Card:

    card_values: list = [2,3,4,5,6,7,8,9,10,11,12,13,14]
    suits: list =  ['clubs', 'diamonds', 'hearts', 'spades']
    face_cards: dict = {
            'J': 11,
            'Q': 12,
            'K': 13,
            'A': 14,
            11: 'J',
            12: 'Q',
            13: 'K',
            14: 'A',
        }
    
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value} - {self.suit}"

    def __repr__(self):
        return self.__str__()