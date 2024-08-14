import logging
import logging.config
import os
import yaml

class Logging:
    
    def __init__(self):
        
        config_dir = 'logger/logging_config.yaml'
        logs_dir = 'logger/logs'
        
        if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
        
        if os.path.exists(config_dir):
            with open(config_dir, 'rt') as file:
                config = yaml.safe_load(file.read())
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=logging.INFO)
            
    def get_logger(self, name='general'):
        return logging.getLogger(name)