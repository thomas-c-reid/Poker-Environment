import os
import sys

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True            

from game_runner import GameRunner
import os

if __name__ == '__main__':
    
    # clearing logs
    logs_dir = ['logger/logs/general.log', 'logger/logs/database.log']
    for log_dir in logs_dir:
        if os.path.exists(log_dir):
            with open(log_dir, 'w') as file:
                pass
        
    game_runner = GameRunner()
    game_runner.start_game()
    game_runner.end()