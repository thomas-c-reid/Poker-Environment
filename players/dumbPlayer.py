from players.BasePlayer import BasePlayer
from env.enums import BettingStagesEnum
from env.dtos import  resultsDto
from env.objects import roundInformation

class Player(BasePlayer):
    def __init__(self, player_id: str = None, player_name: str = None, initial_bankroll: int = 1000):
        super().__init__(player_id, player_name, initial_bankroll)
        self.current_cards = []
        
    def give_cards(self, cards: list):
        return super().give_cards(cards)
        
    def pay_blinds(self, blind_type, amount):
        return super().pay_blinds(blind_type, amount)
    
    def check(self):
        return super().check()
    
    def fold(self):
        return super().fold()
    
    def raise_pot(self, amount: int):
        return super().raise_pot(amount)
    
    def call(self, amount: int):
        return super().call(amount)
    
    def bet(self, amount: int):
        return super().bet(amount)
    
    def update_policy(self, result: resultsDto):
        return super().update_policy(result)
    
    def make_action(self, round_information: roundInformation, betting_stage: BettingStagesEnum):
        '''
        Determines the action the player should take based on the current round information and betting stage.
        
        Args:
            round_information (roundInformation): The current round information.
            betting_stage (BettingStagesEnum): The current betting stage.
            
        Returns:
            actionDto: The action the player decides to take.
        '''
        
        # Look at current_hand - For first round just consider which 