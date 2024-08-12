import os
import sys
import yaml

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

from env.table import tableEnvironment
from players import Player
from database.db_setup import DatabaseSetup

class GameRunner:
    
    def __init__(self):
        game_config, database_config = self.load_game_config()
        self.Table = tableEnvironment(**game_config)
        self.database = DatabaseSetup(**database_config)
            
    def load_game_config(self, config_file='game_config.yaml'):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
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
            'user': config['database_config']['user'],
            'host': config['database_config']['host'],
            'password': config['database_config']['password']
        }
        
        game_config = {
            'players': self.players,
            'blind_amount': config['game_config']['blind_amount']
        }
        
        return game_config, database_config
        
    def start_game(self):
        
        game_terminated = False
        round_count = 0
        while not game_terminated:
            round_count += 1
            
            round_terminated = False
            self.Table.start_round()
            
            while not round_terminated:
                self.Table.deal_table_cards()
                
                betting_terminated = False
                
                while not betting_terminated:
                    player = self.Table.get_current_player()
                    
                    action = player.make_action(self.Table.round_information, self.Table.betting_stage)
                    
                    print(f'[A] {action.player_id} | {action.action.name} - {action.action_amount} {"~A~" if action.all_in_flag else ""}')
                    
                    betting_terminated, round_terminated = self.Table.step(action)

                    if round_terminated:
                        print('~x~ ROUND TERMINATED ~x~')
                        
                self.Table.end_round()
                
            if round_terminated:
                results, game_terminated = self.Table.settle_round()
                if game_terminated:
                    print('GAME OVER')
                    
            if round_count >= 10:
                game_terminated = True

            
            