import unittest
import pytest
import sys
import os
from util4tests import enable_test_logging, run_single_test, log

from pykg2tbl import KG2TblService, KGFileSource, KG2EndpointSource, J2SparqlBuilder


ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 10"
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"


class TestBuilder(unittest.TestCase):
    def test_basic_query_sparql(self):
        template_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sparql_templates')
        j2sqb = J2SparqlBuilder(template_folder)
        qry = j2sqb.build_sparql_query("all.sparql")
        self.assertIsNotNone(qry, "result qry should exist")
        self.assertEqual('''SELECT * 
WHERE { 
    ?s ?p ?o. 
} 
LIMIT 10''',qry,'unexpected qry result')


if __name__ == "__main__":
    run_single_test(__file__)