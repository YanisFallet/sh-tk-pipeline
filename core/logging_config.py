import logging
import os


module_name = os.path.splitext(os.path.basename(__file__))[0]

logger = logging.getLogger(module_name)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('logs/journal.log')

file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
