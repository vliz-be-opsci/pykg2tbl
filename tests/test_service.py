import unittest
import pytest
import sys
import os
from util4tests import enable_test_logging, run_single_test, log

from pykg2tbl import KG2TblService, KGFileSource, KG2EndpointSource


ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 10"
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"


class TestService(unittest.TestCase):

    def test_basic_filesource(self):
        file_base = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sources')
        log.debug(f"test using files in {file_base}")
        test_source  = KGFileSource(os.path.join(file_base, '01-persons-shape.ttl'),
                                    os.path.join(file_base, '02-person.ttl'))
        result = test_source.query(ALL_TRIPLES_SPARQL)
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")

    def test_basic_endpoint(self):
        test_source  = KG2EndpointSource(BODC_ENDPOINT)
        result = test_source.query(ALL_TRIPLES_SPARQL)
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")
        
    def test_full_search(self):
        #make full search on the endpoint of BODC to see what it returns // test on the BODC server itself first
        test_source  = KG2EndpointSource(BODC_ENDPOINT)
        #make test qry using template from BODC
        result = test_source.query(ALL_TRIPLES_SPARQL)
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")


if __name__ == "__main__":
    run_single_test(__file__)
