from abc import ABC, abstractmethod
from uuid import uuid4
from utils.utils import playerNameGenerator, generate_shortuuid_id
from env.dtos import resultsDto

class BasePlayer(ABC):
    '''
    player_id: (str) a random_identifier for each player
    player_name: (str) Name of the player
    initial_bankroll: (int) Amount of money player started with
    bankroll: (int) Players current bankroll
    in_play: (bool) If player still has money in account and can keep playing
    '''

    @abstractmethod
    def __init__(self, player_id=None, player_name=None, initial_bankroll=1000):
        self.player_id = generate_shortuuid_id() if player_id is None else player_id
        self.player_name = playerNameGenerator() if player_name is None else player_name
        self.bankroll = initial_bankroll
        self.initial_bankroll = initial_bankroll
        self.in_play = True
        self.all_in_flag = False

    def print_round_summary(self, result: resultsDto):
        output = ''
        output += '[]' * 25 + '\n'
        output += f'ROUND COMPLETE | player_name: {self.player_name} - ({self.player_id})\n'
        output += f'ROUND COMPLETE | bankroll: {self.bankroll}\n'
        output += f'ROUND COMPLETE | results: (+{result.amount_won}) (-{result.amount_bet})\n'
        output += f'ROUND COMPLETE | cards: {self.current_cards}\n'
        output += f'ROUND COMPLETE | final hand: {result.final_hand}\n'
        output += f'ROUND COMPLETE | hand value: {result.final_hand_value}\n'
        output += '[]' * 25 + '\n'
        return output


    @abstractmethod
    def pay_blinds(self, blind_type, amount):
        pass

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def fold(self):
        pass

    @abstractmethod
    def raise_pot(self, amount):
        pass

    @abstractmethod
    def call(self, amount):
        pass

    @abstractmethod
    def bet(self, amount):
        pass

    @abstractmethod
    def make_action(self):
        pass

    @abstractmethod
    def update_policy(self):
        pass
