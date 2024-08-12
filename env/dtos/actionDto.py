from typing import NamedTuple
from env.enums import actionNameEnum

class actionDto(NamedTuple):
    '''
    action: (string) the action to be taken by the player
    player_id: (int) the id of the player 
    action_amount: (int) the value that is being added to the pot
    bankroll_left: (int) the value left in the players acccount
    all_in_flag: (bool) if user has gone all in
    '''
    action: actionNameEnum
    player_id: int
    action_amount: int
    bankroll_left: int
    all_in_flag: bool = False