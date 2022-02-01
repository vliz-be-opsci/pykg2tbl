import unittest
import pytest
import sys
import os
from util4tests import enable_test_logging, run_single_test, log

from pykg2tbl import KG2TblService, KGFileSource


class TestService(unittest.TestCase):

    def test_basic(self):
        file_base = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sources')
        log.debug(f"test using files in {file_base}")
        test_source  = KGFileSource(os.path.join(file_base, '01-persons-shape.ttl'),
                                    os.path.join(file_base, '02-person.ttl'))
        #TODO send some default sparql query e.g. listing all triples
        result = test_source.query("SELECT * WHERE { ?s ?p ?o. }")
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")


if __name__ == "__main__":
    run_single_test(__file__)
