from env.enums import BettingStagesEnum, actionNameEnum
from env.dtos import actionDto
from env.objects import roundInformation

class PlayerTurnManager:
    """
    Manages the player turns, blinds, and dealer position for a poker game.

    Attributes:
        players (list): List of Player objects.
        num_players (int): Number of players in the game.
        current_turn_idx (int): Index of the player whose turn it is.
        dealer_idx (int): Index of the current dealer.
        small_blind_idx (int): Index of the current small blind.
        big_blind_idx (int): Index of the current big blind.
    """
    
    def __init__(self, players: list):
        self.current_turn_idx = 0
        self.round_max_bet = 0
        
        # DATA STUCTURE TO TRACK TURNS
        self.create_player_statuses(players)
        
        self.small_blind_idx = 0
        self.big_blind_idx = self.get_next_index()
        self.dealer_idx = self.big_blind_idx
        
    def create_player_statuses(self, players: list):
        self.num_players = len(players)
        self.player_statuses = [
            {
                'player_id': player.player_id,
                'has_bet': False,
                'amount_bet': 0,
                'all_in': False,
                'in_play': True
            } for player in players
        ]
        
    def get_next_index(self, next_idx=None):
        """
        Gets the next index of the player who is eligible to bet within the round.

        Args:
            current_idx (int): The current index.

        Returns:
            int: The next index of the eligible player, or None if no eligible player is found.
        """
        if next_idx == None:
            next_idx = (self.current_turn_idx + 1) % self.num_players
        else:
            next_idx = (next_idx + 1) % self.num_players    

    
        num_checked = 0
        while num_checked < self.num_players:
            player_status = self.player_statuses[next_idx]
            
            if player_status['in_play'] and not player_status['all_in'] and not player_status['has_bet']:
                self.current_turn_idx = next_idx
                return next_idx  # Found the next eligible player

            # Move to the next player index
            next_idx = (next_idx + 1) % self.num_players
        
        return None
        
    def update_blinds_and_dealer(self):
        self.big_blind_idx = self.get_next_index(self.big_blind_idx)
        self.small_blind_idx = self.get_next_index(self.small_blind_idx)
        self.dealer_idx = self.get_next_index(self.dealer_idx)

    def update_player_status(self, action: actionDto):
        """
        update the status of the player based on given action
        """
        
        player_status_dict = next(player_status for player_status in self.player_statuses if player_status['player_id'] == action.player_id)
        
        if action.action == actionNameEnum.FOLD:
            player_status_dict['in_play'] = False        
        else:
            player_status_dict['amount_bet'] += action.action_amount
            if action.action != actionNameEnum.BIG_BLIND:
                player_status_dict['has_bet'] = True
            if action.all_in_flag:
                player_status_dict['all_in'] = True
        
        if player_status_dict['amount_bet'] > self.round_max_bet:
            self.reset_has_bet_status(player_id=action.player_id)
            self.round_max_bet = player_status_dict['amount_bet']
            
    def reset_has_bet_status(self, player_id: int = None):
        """
        Reset every players 'has_bet' status except for player_id provided
        """
        for player_status_dict in self.player_statuses:
            if player_status_dict['player_id'] != player_id:
                player_status_dict['has_bet'] = False   
                        
    def check_game_status(self, betting_stage: BettingStagesEnum):
        """
        Checks whether the current betting round and the overall game are complete.

        Args:
            round (BettingStagesEnum): The current stage of the betting round.

        Returns:
            - round_complete (bool): `True` if current betting round is complete, else `False`.
            - game_complete (bool): `True` if overall game is complete, else `False`.
        """
        betting_complete = True
        round_complete = False
        
        for player_status_dict in self.player_statuses:
            if player_status_dict['in_play']:
                if not player_status_dict['has_bet']:
                    if not player_status_dict['all_in']:
                        betting_complete = False
        
        if betting_complete and betting_stage == BettingStagesEnum.RIVER:
            round_complete = True 
            
        return betting_complete, round_complete
    
    def end_round(self, players: list):
        self.create_player_statuses(players)
        self.update_blinds_and_dealer()
        self.round_max_bet = 0
    
    