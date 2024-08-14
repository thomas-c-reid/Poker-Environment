from env.enums import BettingStagesEnum, actionNameEnum
from env.dtos import actionDto
import numpy as np
from copy import deepcopy
from utils.utils import increase_betting_round
from datetime import datetime

class roundInformation():
    '''
    Class which will hold matricies to pass players so they can make their decision
    
    ATTRIBUTES:    
        table_cards (set): A set of 5 cards held by the table.
        player_indices (dict): A dictionary mapping player IDs to their positions in the matrix.
        action_amount_matrix (ndarray): A matrix of dimensions (num_players, num_rounds) containing (action, bet_amount) tuples for each player and round.
        player_all_in_status (ndarray): A boolean array of dimensions (num_players,) indicating whether each player is all-in.
        player_bankroll_amounts (ndarray): An array of dimensions (num_players,) containing the bankroll amounts for each player.
        base_action_space (list): a list of all possible actions that a player can take in a given round based on previous bet history
    '''
    
    def __init__(self, players: list):
        self.table_cards = set()
        self.player_indices = {player.player_id: idx for idx, player in enumerate(players)}
        self.current_round_number = 1
        self.round_started_time = None
        self.round_duration = None
        self.initialise_matricies(players)
        self.base_action_space = self.create_action_space()
        self.current_betting_stage = BettingStagesEnum.PRE_FLOP
        self.total_pot_value = 0 # add this to the DB
        
    def increase_round_information(self):
        self.current_betting_stage = increase_betting_round(self.current_betting_stage)
    
    def reset_round_information(self, players: list):
        self.current_betting_stage = BettingStagesEnum.PRE_FLOP
        self.current_round_number += 1
        self.initialise_matricies(players)
        self.table_cards = set()
        self.player_indices = {player.player_id: idx for idx, player in enumerate(players)}
                        
    def initialise_matricies(self, players: list):
        '''
        Initialize the betting information for the round.
        
        Args:
            players (list): A list of player objects.
            
        Returns:
            - action_amount_matrix (ndarray): A matrix of dimensions (num_players, num_rounds) containing (action, bet_amount) tuples.
            - player_all_in_status (ndarray): A boolean array of dimensions (num_players,) indicating all-in status for each player.
            - player_bankroll_amounts (ndarray): An array of dimensions (num_players,) containing the bankroll amounts for each player.
        '''
                
        num_players = len(players)
        num_rounds = len(BettingStagesEnum)
        
        self.round_started_time = datetime.now()
        
        bet_amounts = np.zeros((num_players, num_rounds))
        actions = np.full((num_players, num_rounds), actionNameEnum.CHECK.value)
        
        self.player_all_in_status = np.zeros(num_players, dtype=bool)
        self.player_bankroll_amounts = np.array([player.bankroll for player in players])
        
        self.action_amount_matrix = np.zeros((num_players, num_rounds), dtype=object)
        for i in range(num_players):
            for j in range(num_rounds):
                self.action_amount_matrix[i][j] = (actions[i][j], bet_amounts[i][j]) 
                
    def add_to_matricies(self, action: actionDto):
        player_idx = self.player_indices[action.player_id]
        
        # UPDATE ACTION_VALUE MATRIX
        amount_bet = self.action_amount_matrix[player_idx][self.current_betting_stage.value][1] + action.action_amount
        self.action_amount_matrix[player_idx][self.current_betting_stage.value] = (action.action.value, amount_bet)
        
        # UPDATE BANKROLLS
        self.player_bankroll_amounts[player_idx] = action.bankroll_left
        
        # UPDATE ALL_IN FLAG
        if action.all_in_flag:
            self.player_all_in_status[player_idx] = True
            
    def create_action_space(self):
        return [action for action in actionNameEnum if action not in (actionNameEnum.BIG_BLIND, actionNameEnum.SMALL_BLIND)]
            
    def get_action_space(self, player_id: str, bettingStage: BettingStagesEnum):
        
        temp_action_space = deepcopy(self.base_action_space)
        player_idx = self.player_indices[player_id]
        
        # This isn't fully correct, i don't know how to get the 'amount bet' from the 
        current_amount_bet = self.action_amount_matrix[player_idx][bettingStage.value][1]
        
        amounts_bet = []
        for idx in self.player_indices:
            if idx != player_idx:
                amount_bet = self.action_amount_matrix[idx][bettingStage.value][1]
                amounts_bet.append(amount_bet)
        max_amount_bet = max(amounts_bet)
        
        if max_amount_bet > current_amount_bet:
            # Player needs to call or raise
            temp_action_space.remove(actionNameEnum.CHECK)
            temp_action_space.remove(actionNameEnum.BET)
        else:
            # Player can check or bet if no one has raised
            temp_action_space.remove(actionNameEnum.CALL)
        
        if current_amount_bet > 0:
            # Player can't bet if they have already bet, they can only raise
            temp_action_space.remove(actionNameEnum.BET)
        else:
            # Player can't raise if they haven't bet anything yet
            temp_action_space.remove(actionNameEnum.RAISE)
        
        return temp_action_space

    def to_db(self):        
        
        if len(self.table_cards) == 0:
            table_cards = None
        else:
            table_cards = '{' + ', '.join([str(card) for card in self.table_cards]) + '}'
        return (
            table_cards,
            datetime.now() - self.round_started_time,
            self.current_round_number,
        )