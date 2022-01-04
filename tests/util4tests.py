import logging
import logging.config
import os
import yaml
from dotenv import load_dotenv
from pykg2tbl import log


def enable_test_logging():
    load_dotenv()
    if 'PYTEST_LOGCONF' in os.environ:
        logconf = os.environ['PYTEST_LOGCONF']
        with open(logconf, 'r') as yml_logconf:
            logging.config.dictConfig(yaml.load(yml_logconf, Loader=yaml.SafeLoader))
        log.info(f"Logging enabled according to config in {logconf}")
