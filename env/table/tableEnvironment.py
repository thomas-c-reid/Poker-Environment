from env.table import baseTable
from env.dtos import actionDto
from env.enums import actionNameEnum, BettingStagesEnum
from utils.utils import increase_betting_round
from logger.logger_config import Logging
from time import sleep

logging_config = Logging()
logger = logging_config.get_logger()

class tableEnvironment(baseTable):
    
    def __init__(self, players: list, blind_amount: int, action_delay: bool):
        super().__init__(players=players, blind_amount=blind_amount, action_delay=action_delay)
        self.round_count = 0
        
    def start_round(self):
        
        self.round_count += 1
        self.round_information.update_indexes(self.player_turn_manager.return_indexes())
        self.database.add_round(self.round_information.to_db())
        
        logger.info('='*50)
        logger.info(f'Starting Round - {self.round_count}')
        logger.info('='*50)
        
        self.player_cards = []
        self.deal_initial_cards()
        
        # SMALL BLIND
        small_blind = self.players[self.player_turn_manager.small_blind_idx].pay_blinds(actionNameEnum.SMALL_BLIND, self.blind_amount/2)
        self.round_information.add_to_matricies(small_blind)
        
        
        self.pot_manager.add_action(small_blind)
        self.player_turn_manager.update_player_status(small_blind)
        self.database.add_action(small_blind, self.round_information.current_round_number)
        # BIG BLIND
        big_blind = self.players[self.player_turn_manager.big_blind_idx].pay_blinds(actionNameEnum.BIG_BLIND, self.blind_amount)
        self.round_information.add_to_matricies(big_blind)
        self.pot_manager.add_action(big_blind)
        self.player_turn_manager.update_player_status(big_blind)
        self.database.add_action(big_blind, self.round_information.current_round_number)
        
        return small_blind, big_blind
            
    def step(self, action: actionDto = None):
        
        if self.action_delay:
            sleep(0.5)
            
        self.round_information.add_to_matricies(action)
        self.pot_manager.add_action(action)
        self.player_turn_manager.update_player_status(action)
        
        betting_complete, round_complete = self.player_turn_manager.check_game_status(self.betting_stage)
        if betting_complete:
            print('BETTING COMPLETE')
        if round_complete:
            print('round_complete')
        
        if round_complete:
            logger.info(f'[ROUND RESULTS] - {self.table_cards}')
            logger.info(f'[ROUND RESULTS] - {self.pot_manager.current_pot_value}')
            
            
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
            
            self.pot_manager.reset_round(self.players, self.round_index)
            self.round_information.increase_round_information()
        
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
        self.database.update_round(self.round_information.to_db())
        
        self.remove_players()
        self.pot_manager.pots = []
        self.table_cards = []
        self.betting_stage = BettingStagesEnum.PRE_FLOP
        
        self.player_turn_manager.end_round(self.players)
        self.round_information.reset_round_information(self.players)
        self.round_index += 1
        
        if len(self.players) <= 1:
            game_terminated = True
        
        return results, game_terminated
    