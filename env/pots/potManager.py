# from pot import Pot
# from dtos import actionDto, resultsDto
# from enums import actionNameEnum

# class PotManager:
    
#     def __init__(self, players: list):
#         self.all_players = [player.player_id for player in players]
#         self.active_players = [player.player_id for player in players]
#         self.pots = []
#         self.create_bets_player_dicts()
#         self.current_bet_amount = 0
#         self.results = []
#         for player_id in self.all_players:
#             self.results.append(resultsDto(
#                 player_id=player_id,
#                 amount_won=0,
#                 amount_bet=0,
#                 reward=0
#             ))
    
#     def create_bets_player_dicts(self):
#         self.bets_player_dicts = []
#         for player_id in self.all_players:
#             bet_dict = {
#                 'player_id': player_id,
#                 'amount_bet': 0,
#                 'active': True,
#                 'has_bet': False,
#                 'all_in_flag': False
#             }
#             self.bets_player_dicts.append(bet_dict)
        
    
#     def add_action(self, action: actionDto):
#         """
#         will create a bet recipt
        
#         TODO:
        
#         """
#         player_id = action.player_id
#         player_action = action.action
        
#         current_bet_dict = next(bet_dict for bet_dict in self.bets_player_dicts if bet_dict['player_id'] == player_id)
        
#         if player_action != actionNameEnum.FOLD:
            
#             # has bet_amount = True
#             if action.action_amount > self.current_bet_amount:
#                 for bet_dict in self.bets_player_dicts:
#                     bet_dict['has_bet'] = False
                    
#             current_bet_dict['has_bet'] = True
        
#         else:
#             # if a player folds we want him removed from all dicts
#             for pot in self.pots:
#                 pot.remove_player(player_id)
                
#         self.check_round_complete()       
    
#     def create_pots(self):
#         """
#         at end of each round 
#         """
#         pots_ = []
        
#         final_bet_dicts = [bet_dict for bet_dict in self.bets_player_dicts if bet_dict['active']]
#         bet_receipts = [{'player_id': bet_dict['player_id'], 'amount': bet_dict['amount']} for bet_dict in final_bet_dicts]
#         sorted_bet_receipts = sorted(bet_receipts, key=lambda x: x['amount_bet'], reversed=True)
        
        
#         for bet_receipt in sorted_bet_receipts:
            
#             # first need to check if already have a pot to chip in to 
#             for pot in pots_:
#                 pot.add_action(bet_receipt['amount'])
#                 bet_receipt['amount'] -= pot.current_bet()
            
#             if bet_receipt['amount'] > 0:
#                 players_in_pot = [bet_dict['player_id'] for bet_dict in sorted_bet_receipts if bet_dict['amount'] >= bet_receipt['amount']]
#                 pot_ = Pot(player_in_pot=players_in_pot, pot_value=bet_receipt['amount'])
#                 bet_receipt['amount'] = 0
#                 pots_.append(pot_)
                
#         self.pots.extend(pots_)
                
    
#     def check_round_complete(self):
#         round_complete = True
#         pots = None
        
#         for bet_dict in self.bets_player_dicts:
#             if not bet_dict['active']:
                
#                 if not bet_dict['has_bet']:
#                     if not bet_dict['all_in']:
#                         round_complete = False  
                    
#         if round_complete:
#             self.create_pots()              
        
#         return round_complete, pots
    
#     def create_results(self, final_betting_dicts: list):
#         '''
#         generate results items based on winners 
         
#         '''

#         for pot in self.pots:
#             pot_winning_idx = 1
#             pot_winners = []
#             pot_won = False
            
#             for final_betting_dict in final_betting_dicts:
#                 if final_betting_dict['position'] == pot_winning_idx:
#                     if final_betting_dict['player_id'] in pot.players_in_pot:
#                         pot_winners.append(final_betting_dict['player_id'])
#                         pot_won = True
#                 else:
#                     if not pot_won:
#                         pot_winning_idx += 1
                        
#             for result in self.results:
#                 if result.player_id in pot_winners:
#                     result.amount_won += pot.pot_value / len(pot_winners)
                    
#         for result in self.results:
#             result.amount_bet = next(bet_dict['amount'] for bet_dict in self.bets_player_dicts if bet_dict['player_id'] == result.player_id)
#             result.reward = result.amount_won - result.amount_bet            
            
#         return self.results
    


from env.pots import Pot
from env.dtos import actionDto, resultsDto
from env.enums import actionNameEnum

class PotManager:
    """
    Manages the pots and player actions for a poker game.
    """

    def __init__(self, players: list):
        self.players = players
        self.all_players = [player.player_id for player in players]
        self.active_players = [player.player_id for player in players]
        self.pots = []
        self.initialise_lists()
        self.current_bet_amount = 0
        self.current_pot_value = 0
        
    
    def initialise_lists(self):
        """
        Initialize the betting dictionary for each player.
        """
        self.bets_player_dicts = [
            {
                'player_id': player.player_id,
                'amount_bet': 0,
                'active': True,
                'has_bet': False,
                'all_in_flag': False
            }
            for player in self.players
        ]
        
        self.results = [
            resultsDto(player_id=player.player_id, amount_won=0, amount_bet=0, reward=0, final_hand=[], final_hand_value=None)
            for player in self.players
        ]
        
    
    def add_action(self, action: actionDto):
        """
        Updates player status based on the action taken.

        Args:
            action (actionDto): The action performed by a player.
        """
        player_id = action.player_id
        player_action = action.action
        
        current_bet_dict = next(bet_dict for bet_dict in self.bets_player_dicts if bet_dict['player_id'] == player_id)
        
        if player_action != actionNameEnum.FOLD:
            if action.action_amount > self.current_bet_amount:
                self.current_bet_amount = action.action_amount
                for bet_dict in self.bets_player_dicts:
                    bet_dict['has_bet'] = False
            current_bet_dict['has_bet'] = True
            current_bet_dict['amount_bet'] += action.action_amount   
            self.current_pot_value += action.action_amount     
        else:
            current_bet_dict['active'] = False
            for pot in self.pots:
                pot.remove_player(player_id)
                
        # self.check_round_complete()       
    
    # this shouldn't be called internally it should be called from table c
    def create_pots(self, round_index: int):
        """
        Creates pots at the end of each round based on player bets.
        """
        pots_ = []
        final_bet_dicts = [bet_dict for bet_dict in self.bets_player_dicts if bet_dict['active']]
        bet_receipts = [{'player_id': bet_dict['player_id'], 'amount_bet': bet_dict['amount_bet']} for bet_dict in final_bet_dicts]
        sorted_bet_receipts = sorted(bet_receipts, key=lambda x: x['amount_bet'])        
        
        for bet_receipt in sorted_bet_receipts:
            for pot in pots_:
                if pot.current_bet > 0:
                    pot.add_to_pot(bet_receipt['amount_bet'])
                    bet_receipt['amount_bet'] -= pot.current_bet
            if bet_receipt['amount_bet'] > 0:
                players_in_pot = [bet_dict['player_id'] for bet_dict in final_bet_dicts if bet_dict['amount_bet'] >= bet_receipt['amount_bet']]
                pot_ = Pot(players_in_pot=players_in_pot, pot_value=bet_receipt['amount_bet'], round_index=round_index)
                bet_receipt['amount_bet'] = 0
                pots_.append(pot_)
                
        self.pots.extend(pots_)
    
    def create_results(self, final_betting_dicts: list):
        """
        Generates results based on the winners.

        Args:
            final_betting_dicts (list): List of final betting information for each player.
        """
        
        for pot in self.pots:
            pot_winning_idx = 1
            pot_winners = []
            pot_won = False
            
            for final_betting_dict in final_betting_dicts:
                if final_betting_dict['position'] == pot_winning_idx:
                    if final_betting_dict['player_id'] in pot.players_in_pot:
                        final_betting_dict['amount_bet'] += pot.current_bet
                        pot_winners.append(final_betting_dict['player_id'])
                        pot_won = True
                else:
                    if final_betting_dict['player_id'] in pot.players_in_pot:
                        final_betting_dict['amount_bet'] += pot.current_bet
                if not pot_won:
                    pot_winning_idx += 1
                        
            for result in self.results:
                if result.player_id in pot_winners:
                    result.amount_won += pot.pot_value / len(pot_winners)
                    
        for result in self.results:
            result.amount_bet = next(bet_dict['amount_bet'] for bet_dict in final_betting_dicts if bet_dict['player_id'] == result.player_id)
            result.final_hand = next(final_bet_dict['final_hand'] for final_bet_dict in final_betting_dicts if final_bet_dict['player_id'] == result.player_id)
            result.final_hand_value = next(final_bet_dict['hand_value'] for final_bet_dict in final_betting_dicts if final_bet_dict['player_id'] == result.player_id)
            result.reward = result.amount_won - result.amount_bet
            
        self.pots = []
        self.current_pot_value = 0
            
        return self.results
    
    def reset_round(self, players: list, round_index: int):
        
        self.create_pots(round_index)
        
        self.players = players
        self.all_players = [player.player_id for player in players]
        self.active_players = [player.player_id for player in players]
        self.initialise_lists()
        self.current_bet_amount = 0
        
