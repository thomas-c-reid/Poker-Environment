import yaml

from env.table import tableEnvironment
from players import Player
from database.db_manager import DatabaseManager
from logger.logger_config import Logging

log_config = Logging()
logger = log_config.get_logger()

class GameRunner:
    
    def __init__(self):
        game_config, database_config = self.load_game_config()
        self.database = DatabaseManager(**database_config)
        self.Table = tableEnvironment(**game_config)
          
    def load_game_config(self, config_file: str = 'game_config.yaml', secret_file: str = 'secrets.yaml'):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        with open(secret_file, 'r') as file:
            secrets = yaml.safe_load(file.read())
        
        players_config = config['game_config']['players']
        self.players = [
            Player(player_name=player['player_name'], 
                initial_bankroll=player['initial_bankroll'], 
                player_id=player['player_id']
            )
            for player in players_config
        ]
        
        database_config = {
            'db_name': config['database_config']['name'],
            'user': secrets['db_user'],
            'host': config['database_config']['host'],
            'password': secrets['db_password'],
            'port': config['database_config']['port'],
            'csv_path': secrets['csv_path'],
            'enable_db_connection': config['database_config']['enable_db_connection']
        }
        
        game_config = {
            'players': self.players,
            'blind_amount': config['game_config']['blind_amount'],
            'action_delay': config['game_config']['action_delay']
        }
                
        return game_config, database_config
        
    def start_game(self):
        game_terminated = False
        round_count = 0
        while not game_terminated:
            round_count += 1
            
            round_terminated = False
            small_blind, big_blind = self.Table.start_round()
            
            logger.info(f'[A] {small_blind.player_id} | {small_blind.action.name} - {small_blind.action_amount} {"~A~" if small_blind.all_in_flag else ""}')
            logger.info(f'[A] {big_blind.player_id} | {big_blind.action.name} - {big_blind.action_amount} {"~A~" if big_blind.all_in_flag else ""}')
                        
            while not round_terminated:
                self.Table.deal_table_cards()
                
                logger.info(f'[TABLE CARDS] - {self.Table.table_cards}')
                
                betting_terminated = False
                
                while not betting_terminated:
                    player = self.Table.get_current_player()
                    
                    action = player.make_action(self.Table.round_information, self.Table.betting_stage)
                    self.database.add_action(action, round_count)
                    
                    logger.info(f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}')
                    betting_terminated, round_terminated = self.Table.step(action)

                    if round_terminated:
                        logger.info('~x~ ROUND TERMINATED ~x~')
                        
                self.Table.end_round()
                
            if round_terminated:
                results, game_terminated = self.Table.settle_round()
                
                for result in results:
                    self.database.add_result(result, round_count)
                
                if game_terminated:
                    logger.info('GAME OVER')
                    # print('GAME OVER')
                    
            # if round_count >= 10:
            #     game_terminated = True

    def end(self):
        self.database.close_connection()
            