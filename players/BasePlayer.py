from abc import ABC, abstractmethod
from utils.utils import playerNameGenerator, generate_shortuuid_id
from env.dtos import resultsDto, actionDto
from env.enums import actionNameEnum

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
    
    def give_cards(self, cards: list):
        self.current_cards = cards
        
    def pay_blinds(self, blind_type: actionNameEnum, blind_amount: int, keep_bankroll: bool = False):
        all_in_flag = False
        amount = blind_amount
        if blind_amount >= self.bankroll:
            all_in_flag = True
            self.all_in_flag = True
            amount = self.bankroll
            self.bankroll = 0
        else:
            if not keep_bankroll:
                self.bankroll -= blind_amount

        action_dto = actionDto(
            action=blind_type,
            player_id=self.player_id,
            action_amount=amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )

        return action_dto
    
    def check(self):
        return actionDto(
            action=actionNameEnum.CHECK,
            player_id=self.player_id,
            action_amount=0,
            bankroll_left=self.bankroll,
            all_in_flag=False
        )

    def fold(self):
        return actionDto(
            action=actionNameEnum.FOLD,
            player_id=self.player_id,
            action_amount=0,
            bankroll_left=self.bankroll,
            all_in_flag=False
        )

    def raise_pot(self, amount: int, keep_bankroll: bool = False):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            if not keep_bankroll:
                self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.BET,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )
        return action_dto

    def call(self, amount: int, keep_bankroll: bool = False):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            if not keep_bankroll:
                self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.CALL,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )        
        return action_dto

    def bet(self, amount: int, keep_bankroll: bool = False):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            if not keep_bankroll:
                self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.BET,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )

        
        return action_dto
    
    @abstractmethod
    def update_policy(self):
        pass

    @abstractmethod
    def make_action(self):
        pass
