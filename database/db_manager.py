# postGreSQL DataBase:
import psycopg2
from logger.logger_config import Logging
from players import Player
from env.dtos import actionDto, resultsDto
import os
import csv

log_config = Logging()
logger = log_config.get_logger('database')

class DatabaseManager:
    _instance = None
    
    def __new__(cls, db_name: str=None, user: str=None, password: str=None, host: str=None, port: str=None, csv_path: str = 'database/csv_exports'):
        if cls._instance is None:
            logger.info('initialising database manager singleton')      
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls.db_name = db_name
            cls.user = user
            cls.password = password
            cls.host = host
            cls.port = port
            cls.csv_path = csv_path
            cls.connection = None
            cls.cursor = None
            cls.paths = {
                'wipe_tables_path': 'database/sql/wipe_tables.sql',
                'create_tables_path': 'database/sql/create_tables.sql'
            }
            cls._instance.run_setup()
        return cls._instance
        
    def run_setup(self):
        self.create_connection()
        self.wipe_tables()
        self.create_tables()
        
    def create_connection(self):
        logger.info('creating connection')
        
        connection_config = {
            'dbname': self.db_name,
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'port': self.port
        }
                
        self.connection = psycopg2.connect(**connection_config)
        
        logger.info('CONNECTION ESTABLISHED')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        
    def wipe_tables(self):
        logger.info('Preparing to wipe tables')
        with open(self.paths['wipe_tables_path']) as file:
            script = file.read()
        self.cursor.execute(script)
        self.connection.commit()
        logger.info('Successfully Wiped Tables')
        
    def create_tables(self):
        logger.info('creating tables')
        with open(self.paths['create_tables_path'], 'r') as file:
            script = file.read()
        self.cursor.execute(script)
        self.connection.commit()
        logger.info('Tables created successfully')
        
    def add_agent(self, agent: Player=None):
        sql = 'INSERT INTO tbl_agents (id, name, initial_bankroll) \n'
        data = (agent.player_id,
                agent.player_name,
                agent.initial_bankroll
        )
        sql += 'VALUES (%s, %s, %s)'
                
        self.cursor.execute(sql, data)
        self.connection.commit()
        logger.info(f'Added Player: {agent.player_id} to DB')
        
    def add_action(self, action: actionDto=None, round_count:int=0):
        logger.info('Adding Action')
        sql = 'INSERT INTO tbl_actions (player_id, action_type, round, amount, all_in_flag) \n'
        data = (
            action.player_id,
            action.action.name,
            round_count,
            action.action_amount,
            action.all_in_flag
        )
        sql += 'VALUES (%s, %s, %s, %s, %s)'
        
        self.cursor.execute(sql, data)
        self.connection.commit()
        logger.info(f'added action {action.action.name}')
        
    def add_result(self, result: resultsDto = None, round_count:int = 0):
        
        self.update_player_bet_values(result)
        
        sql = 'INSERT INTO tbl_results (round, player_id, amount_won, amount_bet, reward, final_hand_value)'
                
        data = (
            round_count,
            result.player_id,
            result.amount_won,
            result.amount_bet,
            result.reward,
            result.final_hand_value.name
        )
        
        sql += 'VALUES (%s, %s, %s, %s, %s, %s)'
        
        self.cursor.execute(sql, data)
        self.connection.commit()
        logger.info('Successfully added Result')
    
    def update_player_bet_values(self, result: resultsDto = None):
        sql = '''
        UPDATE tbl_agents
        SET total_won = total_won + %s, 
            total_bet = total_bet + %s
        WHERE id = %s
        '''
        data = (
            result.amount_won,
            result.amount_bet,
            str(result.player_id)
        )
        
        self.cursor.execute(sql, data)
        self.connection.commit()
        logger.info('Successfully updated Player Bet Values')

    def add_round(self, data: tuple = None):
        sql = 'INSERT INTO tbl_rounds (table_cards, round_duration, id) \n'
        sql += 'VALUES (%s, %s, %s)'
                
        self.cursor.execute(sql, data)
        self.connection.commit()
        
    def update_round(self, data: tuple = None):
        sql = '''
        UPDATE tbl_rounds
        SET table_cards = %s,
            round_duration = %s
        WHERE id = %s
        '''
        self.cursor.execute(sql, data)
        self.connection.commit()
        
        
    def save_tables_to_csv(self):
        # Define the tables to be saved and their respective CSV file paths
        tables = ['tbl_agents', 'tbl_rounds', 'tbl_actions', 'tbl_results']

        if not os.path.exists(self.csv_path):
            os.makedirs(self.csv_path)

        for table in tables:
            file_path = os.path.join(self.csv_path, f'{table}.csv')
            logger.info(f'Saving table {table} to {file_path}')

            sql = f'SELECT * FROM {table}'
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()

            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write the header
                writer.writerow([desc[0] for desc in self.cursor.description])
                # Write the data rows
                writer.writerows(rows)

            logger.info(f'Table {table} saved successfully')
        
    def close_connection(self, save_results: bool = False):
        if save_results:
            self.save_tables_to_csv()

        if self.cursor:
            logger.info('Closing cursor')
            self.cursor.close()

        if self.connection:
            logger.info('Closing database connection')
            self.connection.close()
            logger.info('Database connection closed')   
    