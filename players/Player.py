from players.BasePlayer import BasePlayer
from env.enums import actionNameEnum, BettingStagesEnum
from env.dtos import actionDto, resultsDto
from env.objects import roundInformation

class Player(BasePlayer):
    def __init__(self, player_id: str = None, player_name: str = None, initial_bankroll: int = 1000):
        super().__init__(player_id, player_name, initial_bankroll)
        self.current_cards = []
        self.histories = []

    def give_cards(self, cards: list):
        self.current_cards = cards

    def pay_blinds(self, blind_type: actionNameEnum, blind_amount: int):
        all_in_flag = False
        amount = blind_amount
        if blind_amount >= self.bankroll:
            all_in_flag = True
            self.all_in_flag = True
            amount = self.bankroll
            self.bankroll = 0
        else:
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

    def raise_pot(self, amount: int):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.BET,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )
        return action_dto

    def call(self, amount: int):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.CALL,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )        
        return action_dto

    def bet(self, amount: int):
        all_in_flag = False
        if amount >= self.bankroll:
            all_in_flag = True
            self.bankroll = 0
        else:
            self.bankroll -= amount

        action_dto = actionDto(
            action=actionNameEnum.BET,
            player_id=self.player_id,
            action_amount=amount if amount < self.bankroll else amount,
            bankroll_left=self.bankroll,
            all_in_flag=all_in_flag
        )

        
        return action_dto
    
    def make_action(self, round_information: roundInformation, betting_stage: BettingStagesEnum):
        '''
        Determines the action the player should take based on the current round information and betting stage.
        
        Args:
            round_information (roundInformation): The current round information.
            betting_stage (BettingStagesEnum): The current betting stage.
            
        Returns:
            actionDto: The action the player decides to take.
        '''
        
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
        
        # MAKE DECISION
        if self.player_id == 3:
            return self.fold()
        
        if value_to_bet > 0:
            if value_to_bet > self.bankroll:
                return self.call(self.bankroll)
            return self.call(value_to_bet)
        else:
            if self.player_id == 2:
                return self.raise_pot(10)
            return self.check()

    def update_policy(self, result: resultsDto):
        self.histories.append(result)
        
        if result.amount_won > 0:
            self.bankroll += result.amount_won
        
        self.print_round_summary(result)
