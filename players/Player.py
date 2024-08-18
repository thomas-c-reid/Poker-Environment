from players.BasePlayer import BasePlayer
from env.enums import BettingStagesEnum, actionNameEnum
from env.dtos import  resultsDto
from env.objects import roundInformation
from random import choice

class Player(BasePlayer):
    def __init__(self, player_id: str = None, player_name: str = None, initial_bankroll: int = 1000):
        super().__init__(player_id, player_name, initial_bankroll)
        self.current_cards = []
        self.model = self.load_model()
        
    def give_cards(self, cards: list):
        
        print(cards)
        return super().give_cards(cards)
        
    def pay_blinds(self, blind_type, amount, keep_bankroll):
        return super().pay_blinds(blind_type, amount, keep_bankroll)
    
    def check(self):
        return super().check()
    
    def fold(self):
        return super().fold()
    
    def raise_pot(self, amount: int, keep_bankroll):
        return super().raise_pot(amount, keep_bankroll)
    
    def call(self, amount: int, keep_bankroll):
        return super().call(amount, keep_bankroll)
    
    def bet(self, amount: int, keep_bankroll):
        return super().bet(amount, keep_bankroll)
    
    def update_policy(self, result: resultsDto, keep_bankroll):
        return super().update_policy(result, keep_bankroll)
    
    def load_model(self):
        # Look for file containing model weights
        # if found, load in the weights from this model
        # return it
        
        # if no model found
        # self.create_ff_network
        
        model_found = False
        
        if model_found:
            model = None
        else:
            model = self.create_ff_network()
        
        return model
    
    def create_ff_network(self):
        # Model for taking in 2 cards and outputing 1 of 5 decisions
        # input_dim = 4
        
        # model = Sequential([
        #     Input(shape=(input_dim,)),
        #     Dense(64, activation='relu'),
        #     Dense(64, activation='relu'),
        #     Dense(5, activation='softmax')
        # ])
        
        # model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        # model.summary()
        
        # return model
        pass

    def make_action(self, round_information: roundInformation, betting_stage: BettingStagesEnum, keep_bankroll: bool = False):
        '''
        Determines the action the player should take based on the current round information and betting stage.
        
        Args:
            round_information (roundInformation): The current round information.
            betting_stage (BettingStagesEnum): The current betting stage.
            
        Returns:
            actionDto: The action the player decides to take.
        '''
        
        action_space = round_information.get_action_space(self.player_id, round_information.current_betting_stage)
        
        value_to_match = 0
        current_player_idx = round_information.player_indices[self.player_id]
        current_amount_bet = round_information.action_amount_matrix[current_player_idx][betting_stage.value][1]
        # get max bet from everyone else:
        for player_idx in range(len(round_information.player_indices)):
            if player_idx != current_player_idx:
                player_bet = round_information.action_amount_matrix[player_idx][betting_stage.value][1]
                if player_bet > value_to_match:
                    value_to_match = player_bet
        # OUTPUT CONSIDDERATIONS BASED ON PREVIOUS BETS THIS ROUND
        value_to_bet = value_to_match - current_amount_bet
        
        
        # Make decision - will need a ff network which takes in player cards and then outputs a value
        #               - how do I do this with a variable output size
        #               - options could include (CHECK, RAISE, FOLD) or (CALL, FOLD) - dont know how to build a network to account for this
        # TO START - Have the whole action space as possible actions, sort based off its predictions, 
        #           then choose which most confident one that exists in action_space
        
        action = choice(action_space)
        
        if action == actionNameEnum.CHECK:
            return self.check()
        elif action == actionNameEnum.CALL:
            return self.call(value_to_bet, keep_bankroll)
        elif action == actionNameEnum.FOLD:
            return self.fold()
        elif action == actionNameEnum.RAISE:
            raise_value = (value_to_match * 2) - current_amount_bet
            return self.raise_pot(raise_value , keep_bankroll)
        elif action == actionNameEnum.BET:
            return self.bet(round_information.blind_amount, keep_bankroll)
        
        
        
        
        # if value_to_bet > 0:
        #     if value_to_bet > self.bankroll:
        #         return self.call(self.bankroll, keep_bankroll)
        #     return self.call(value_to_bet, keep_bankroll)
        # else:
        #     if self.player_id == 2:
        #         return self.raise_pot(round_information.blind_amount, keep_bankroll)
        #     return self.check()
 
    def update_policy(self, result: resultsDto, keep_bankroll: bool = False):
        
        if result.amount_won > 0:
            if not keep_bankroll:
                self.bankroll += result.amount_won
        
        return self.print_round_summary(result)
