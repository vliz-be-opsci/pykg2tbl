import glob
import json
import logging
import logging.config
import os
import sys

import pytest
import yaml
from dotenv import load_dotenv

log = logging.getLogger("tests")

ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
# TODO provide some registry of endpoints to choose from --> issue #4
#   then replace next line!
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"

FILES_SOURCE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "sources"
)
TTL_FILES_TO_TEST = glob.glob(f"{FILES_SOURCE}/*.ttl")

QUERY_RESULT_PATH = f"{FILES_SOURCE}/query_result.json"
with open(QUERY_RESULT_PATH) as src:
    TTL_FILES_QUERY_RESULT = json.load(src)


def enable_test_logging():
    load_dotenv()
    if "PYTEST_LOGCONF" in os.environ:
        logconf = os.environ["PYTEST_LOGCONF"]
        with open(logconf, "r") as yml_logconf:
            logging.config.dictConfig(
                yaml.load(yml_logconf, Loader=yaml.SafeLoader)
            )
        log.info(f"Logging enabled according to config in {logconf}")
        print(logconf)


def run_single_test(testfile):
    enable_test_logging()
    log.info(
        f"Running tests in {testfile} "
        + "with -v(erbose) and -s(no stdout capturing) "
        + "and logging to stdout, "
        + "level controlled by env var ${PYTEST_LOGCONF}"
    )
    sys.exit(pytest.main(["-v", "-s", testfile]))
