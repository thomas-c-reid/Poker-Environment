from dataclasses import dataclass
from env.enums import HandValueEnum

@dataclass
class resultsDto:
    """
    Represents the result of a player's action in the game.

    Attributes:
        player_id (str): The ID of the player.
        amount_won (int): The amount of money won by the player.
        amount_bet (int): The amount of money the player has bet.
        reward (int): The reward amount given to the player.
    """
    player_id: str
    amount_won: int
    amount_bet: int
    reward: int
    final_hand: list
    final_hand_value: HandValueEnum
    
    def print_results(self):
        print('player_id: ', self.player_id)
        print('amount_won: ', self.amount_won)
        print('amount_bet: ', self.amount_bet)
        print('reward: ', self.reward)
        print('final_hand: ', self.final_hand)
        print('final_hand_value: ', self.final_hand_value)
