from loguru import logger
import yaml
import os
from dotenv import load_dotenv
load_dotenv()
cfg = os.environ

DB_CONNECTION_STR=cfg['DB_CONNECTION']

if not cfg['logging']:
    logger.remove()