# postGreSQL DataBase:
import psycopg2
from logger.logger_config import Logging

log_config = Logging()
logger = log_config.get_logger('database')

class DatabaseSetup:
    
    # might need function to wipe logs at start of file 
    
    def __init__(self, db_name: str, user: str, password: str, host: str):
        logger.info('initialising database')
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.connection = None
        self.cursor = None
        self.paths = {
            'create_tables_path': 'create_tables.sql'
        }        
        
        # self.run_setup()
        
    def run_setup(self):
        self.create_connection()
        self.create_database()
        # self.connect_to_db()
        # self.create_tables()
        
    def create_connection(self):
        logger.info('creating connection')
        self.connection = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        
    def create_database(self):
        logger.info('creating database')
        with open(self.paths['create_tables_path'], 'r') as file:
            script = file.read()
        self.cursor.execute(script)
        self.connection.commit()
        logger.info('database created')
    
    def connect_to_db(self):
        pass
    
    def create_tables(self):
        pass
    
    def close_connection(self):
        # this function should save all the data in all the tables to a CSV
        pass
    