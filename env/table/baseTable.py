from abc import abstractmethod, ABC
from random import randint
from env.objects import Card, roundInformation, PlayerTurnManager
from env.enums import HandValue, BettingStagesEnum
from env.pots import PotManager
from logger.logger_config import Logging

logger_config = Logging()
logger = logger_config.get_logger()

class baseTable(ABC):
    '''
    This class will hold all the information to do with the cards 
    '''
    
    def __init__(self, players: list, blind_amount: int = 20):
        self.players = players
        self.table_cards = []
        self.player_cards = []
        self.num_players = len(players)
        self.round_information = roundInformation(players)
        self.betting_stage = BettingStagesEnum.PRE_FLOP
        self.blind_amount = blind_amount
        self.pot_manager = PotManager(players)
        self.player_turn_manager = PlayerTurnManager(players)
        self.round_index = 1
    
    @staticmethod
    def generate_cards():
        cards = []
        for value in Card.card_values:
            for suit in Card.suits:
                # Map the value to its face card name if it exists, otherwise keep the numeric value
                card_value = Card.face_cards.get(value, value)
                _card = Card(card_value, suit)
                cards.append(_card)
        return cards
    
    def deal_card(self, num_cards=1):
        cards = []
        for _ in range(num_cards):
            i = randint(0, len(self.cards)-1)
            card = self.cards[i]
            self.cards.pop(i)
            cards.append(card)
        return cards
    
    def deal_initial_cards(self):
        self.cards = self.generate_cards()
        for player in self.players:
            cards = self.deal_card(2)
            player.give_cards(cards)
            cards_dict = {
                'player_id': player.player_id,
                'cards': cards
            }
            self.player_cards.append(cards_dict)
        
            
        
        # print('.'*15)
        for player_cards in self.player_cards:
            logger.info(f"[DEAL] - {player_cards['player_id']} {player_cards['cards']}")
            # print(player_cards)
            # print('*'*15)
    
    def deal_flop(self):
        cards = self.deal_card(3)
        # print('[CARDS]', cards)
        self.round_information.table_cards.update(cards)
        return cards

    def deal_turn(self):
        card = self.deal_card()
        # print('[CARDS]', card)
        self.round_information.table_cards.update(card)
        return card

    def deal_river(self):
        card = self.deal_card()
        # print('[CARDS]', card)
        self.round_information.table_cards.update(card)
        return card
    
    def deal_table_cards(self):
        """
        Deal table cards depending on round:
        RETURN:
            cards: (list) list of card objects
        """
        if self.betting_stage == BettingStagesEnum.FLOP:
            cards = self.deal_flop()
            self.round_information.table_cards.update(cards)
            self.table_cards.extend(cards)
        elif self.betting_stage == BettingStagesEnum.TURN:
            cards = self.deal_turn()
            self.table_cards.extend(cards)
            self.round_information.table_cards.update(cards)
        elif self.betting_stage == BettingStagesEnum.RIVER:
            cards = self.deal_river()
            self.table_cards.extend(cards)
            self.round_information.table_cards.update(cards)
    
    # CALCULATING WINNER LOGIC
    def calculate_winner(self):
        # output a list of dicts = {'player_id': x, 'position': 1, 'final_hand':[a of spades, ...], hand_value: enum}
        # several_people can have the same position, 
        player_cards = [player_cards_dict['cards'] for player_cards_dict in self.player_cards]
        final_player_cards, final_player_cards_value = self.evaluate_hands(player_cards, self.round_information.table_cards)

        player_best_hands = []
        for player_id, (best_hand, hand_value) in enumerate(zip(final_player_cards, final_player_cards_value), start=1):
            player_best_hands.append({
                'player_id': self.players[player_id-1].player_id,
                'position': None,  # Position will be assigned later
                'final_hand': best_hand,
                'hand_value': hand_value,
                'amount_bet': 0
            })
            

        # Rank players based on their best hand
        # TODO: I don't think this fully works if an ace appears
        # player_best_hands.sort(key=lambda x: (x['hand_value'].value, [card.value for card in x['final_hand']]), reverse=True)
        player_best_hands.sort(
            key=lambda x: (x['hand_value'].value, 
                       [Card.face_cards[card.value] if card.value in Card.face_cards else card.value for card in x['final_hand']]), 
            reverse=True)
        # Assign positions
        current_position = 1
        previous_best_hand = None
        previous_best_hand_value = None
        
        for index, player in enumerate(player_best_hands):
            if previous_best_hand is not None:
                # Compare hand values first
                if player['hand_value'].value != previous_best_hand_value.value:
                    current_position = index + 1
                else:
                    # If hand values are the same, compare the final hands by card values
                    if [card.value for card in player['final_hand']] != [card.value for card in previous_best_hand]:
                        current_position = index + 1

            player['position'] = current_position
            previous_best_hand = player['final_hand']
            previous_best_hand_value = player['hand_value']
        return player_best_hands

    def evaluate_hands(self, player_cards, table_cards):
        final_player_cards = []
        final_player_cards_value = []

        for i, player_hand in enumerate(player_cards):
            cards = list(table_cards) + player_hand
            hand_value, best_cards = self.get_best_hand(cards)
            final_player_cards.append(best_cards)
            final_player_cards_value.append(hand_value)

        return final_player_cards, final_player_cards_value
    
    @staticmethod
    def get_best_hand(cards):
        # Convert face card values to their numeric equivalents
        face_cards = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        numeric_values = [face_cards[card.value] if card.value in face_cards else card.value for card in cards]
        card_value_map = {card: face_cards[card.value] if card.value in face_cards else card.value for card in cards}

        suits = [card.suit for card in cards]
        value_counts = {v: numeric_values.count(v) for v in numeric_values}
        suit_counts = {s: suits.count(s) for s in suits}
        
        is_flush = max(suit_counts.values()) >= 5
        sorted_values = sorted(numeric_values, reverse=True)
        is_straight = any(sorted_values[i:i+5] == list(range(sorted_values[i], sorted_values[i]+5)) for i in range(len(sorted_values)-4))
        
        best_hand_cards = []

        def get_n_highest_cards(n, exclude=[]):
            return [card for card in sorted(cards, key=lambda x: card_value_map[x], reverse=True) if card_value_map[card] not in exclude][:n]

        if is_flush and is_straight:
            best_hand_cards = [card for card in cards if card.suit == max(suit_counts, key=suit_counts.get)]
            best_hand_cards.sort(key=lambda x: card_value_map[x], reverse=True)
            best_hand_cards = best_hand_cards[:5]
            if sorted_values[0] == 14:
                return HandValue.ROYAL_FLUSH, best_hand_cards
            return HandValue.STRAIGHT_FLUSH, best_hand_cards
        
        if 4 in value_counts.values():
            four_kind_value = max(value_counts, key=lambda k: value_counts[k] if value_counts[k] == 4 else 0)
            best_hand_cards = [card for card in cards if card_value_map[card] == four_kind_value]
            best_hand_cards += get_n_highest_cards(1, exclude=[four_kind_value])
            return HandValue.FOUR_OF_A_KIND, best_hand_cards
        
        if 3 in value_counts.values() and 2 in value_counts.values():
            three_kind_value = max(value_counts, key=lambda k: value_counts[k] if value_counts[k] == 3 else 0)
            pair_value = max(value_counts, key=lambda k: value_counts[k] if value_counts[k] == 2 else 0)
            best_hand_cards = [card for card in cards if card_value_map[card] == three_kind_value or card_value_map[card] == pair_value]
            return HandValue.FULL_HOUSE, best_hand_cards[:5]
        
        if is_flush:
            best_hand_cards = [card for card in cards if card.suit == max(suit_counts, key=suit_counts.get)]
            best_hand_cards.sort(key=lambda x: card_value_map[x], reverse=True)
            return HandValue.FLUSH, best_hand_cards[:5]
        
        if is_straight:
            for i in range(len(sorted_values) - 4):
                if sorted_values[i:i+5] == list(range(sorted_values[i], sorted_values[i]+5)):
                    best_hand_cards = [card for card in cards if card_value_map[card] in sorted_values[i:i+5]]
                    best_hand_cards.sort(key=lambda x: card_value_map[x], reverse=True)
                    return HandValue.STRAIGHT, best_hand_cards[:5]
        
        if 3 in value_counts.values():
            three_kind_value = max(value_counts, key=lambda k: value_counts[k] if value_counts[k] == 3 else 0)
            best_hand_cards = [card for card in cards if card_value_map[card] == three_kind_value]
            best_hand_cards += get_n_highest_cards(2, exclude=[three_kind_value])
            return HandValue.THREE_OF_A_KIND, best_hand_cards[:5]
        
        if list(value_counts.values()).count(2) == 2:
            pairs = sorted([k for k in value_counts if value_counts[k] == 2], reverse=True)
            best_hand_cards = [card for card in cards if card_value_map[card] in pairs]
            best_hand_cards += get_n_highest_cards(1, exclude=pairs)
            return HandValue.TWO_PAIR, best_hand_cards[:5]
        
        if 2 in value_counts.values():
            pair_value = max(value_counts, key=lambda k: value_counts[k] if value_counts[k] == 2 else 0)
            best_hand_cards = [card for card in cards if card_value_map[card] == pair_value]
            best_hand_cards += get_n_highest_cards(3, exclude=[pair_value])
            return HandValue.ONE_PAIR, best_hand_cards[:5]
        
        best_hand_cards = get_n_highest_cards(5)
        return HandValue.HIGH_CARD, best_hand_cards
    

    # HELPER FUNCTIONS
    def get_current_player(self):
        current_idx = self.player_turn_manager.get_next_index()
        return self.players[current_idx]

    def remove_players(self):
        """
        Remove players who have a bankroll of 0
        """
        for player in self.players:
            if player.bankroll <= 0:
                # print(f'PLAYER ELIMINATED: {player.player_id}')
                logger.info(f'PLAYER ELIMINATED: {player.player_id}')
                
        self.players = [player for player in self.players if player.bankroll > 0]

    # ABSTRACT METHODS - for real table implementation
    @abstractmethod
    def start_round(self):
        pass
    
    @abstractmethod
    def end_round(self):
        """
        TODO: increase BettingStageEnum
        """
        pass
    
    @abstractmethod
    def step(self):
        pass
    
    