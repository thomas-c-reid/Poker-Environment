from env.table import baseTable
from env.dtos import actionDto
from env.enums import actionNameEnum, BettingStagesEnum
from utils.utils import increase_betting_round
from logger.logger_config import Logging

logging_config = Logging()
logger = logging_config.get_logger()

class tableEnvironment(baseTable):
    
    def __init__(self, players: list, blind_amount: int):
        super().__init__(players=players, blind_amount=blind_amount)
        
    def start_round(self):
        
        logger.info('='*50)
        logger.info('Starting Round')
        logger.info('='*50)
        
        self.player_cards = []
        self.deal_initial_cards()
        
        # SMALL BLIND
        action = self.players[self.player_turn_manager.small_blind_idx].pay_blinds(actionNameEnum.SMALL_BLIND, self.blind_amount/2)
        self.round_information.add_to_matricies(action)
        self.pot_manager.add_action(action)
        self.player_turn_manager.update_player_status(action)
        
        # print(f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}')
        logger.info(f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}')
        
        # BIG BLIND
        action = self.players[self.player_turn_manager.big_blind_idx].pay_blinds(actionNameEnum.BIG_BLIND, self.blind_amount)
        self.round_information.add_to_matricies(action)
        self.pot_manager.add_action(action)
        self.player_turn_manager.update_player_status(action)
        
        # print(f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}')
        f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}'
            
    def step(self, action: actionDto):
        
        self.round_information.add_to_matricies(action)
        self.pot_manager.add_action(action)
        self.player_turn_manager.update_player_status(action)
        
        betting_complete, round_complete = self.player_turn_manager.check_game_status(self.betting_stage)
        
        if round_complete:
            logger.info(f'[ROUND RESULTS] - {self.table_cards}')
            logger.info(f'[ROUND RESULTS] - {self.pot_manager.current_pot_value}')
            # print('[ROUND RESULTS] ')
            # print(f'Table Cards: {self.table_cards}')
            # print(f'Total Pot Value: {self.pot_manager.current_pot_value}')
        return betting_complete, round_complete
    
    def end_round(self):
        game_terminated = False
        
        self.betting_stage = increase_betting_round(self.betting_stage)
        
        # self.increase_betting_round()
                        
        if len(self.players) < 2:
            game_terminated = True
        else:            
            self.player_turn_manager.reset_has_bet_status()
            self.player_turn_manager.round_max_bet = 0
            # self.player_turn_manager.update_blinds_and_dealer()
            
            self.pot_manager.reset_round(self.players, self.round_index)
            
            self.round_information.reset_round_information(self.players)
        
        return game_terminated
    
    def settle_round(self):
        
        results = []
        game_terminated = False
        
        final_betting_dicts = self.calculate_winner()
        results = self.pot_manager.create_results(final_betting_dicts)
            
        for player in self.players:
            result = next(result for result in results if result.player_id == player.player_id)
            result_message = player.update_policy(result)
            logger.info(result_message)
        
        
        # reset all objects
        self.remove_players()
        self.pot_manager.pots = []
        self.table_cards = []
        self.betting_stage = BettingStagesEnum.PRE_FLOP
        
        self.round_information.table_cards = set()
        self.round_information.current_betting_stage = BettingStagesEnum.PRE_FLOP
        self.player_turn_manager.end_round(self.players)
        self.round_index += 1
        
        return results, game_terminated