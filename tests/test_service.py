import unittest
import pytest
import sys
import os
from util4tests import enable_test_logging, run_single_test, log

from pykg2tbl import KG2TblService, KGFileSource, KG2EndpointSource, J2SparqlBuilder


ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"


class TestService(unittest.TestCase):

    def test_basic_filesource(self):
        file_base = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sources')
        log.debug(f"test using files in {file_base}")
        test_source  = KGFileSource(os.path.join(file_base, '02-person.ttl'),
                                    os.path.join(file_base, '01-persons-shape.ttl'))
        result = test_source.query(ALL_TRIPLES_SPARQL)
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")
        self.assertGreater(len(result.__dict__['_data']),0,"result should have a length greater then 0")
        self.assertEqual(len(result.__dict__['_data']),20,"result should be equal to 10")
        ispresentC = False
        for row in result.__dict__['_data']: #TODO:ask marc for a better way to handle this
            if row["o"] == "Cedric Decruw":
                ispresentC = True
        self.assertTrue(ispresentC,"object Cedric Decruw was not present in the results")
        #TODO add assertion to check if len list result > 0 and check if the ammout of triples in both ttls are == len result object and check if object has name cedric in it like in ttl2 file

    def test_basic_endpoint(self):
        test_source  = KG2EndpointSource(BODC_ENDPOINT)
        result = test_source.query(ALL_TRIPLES_SPARQL)
        #log.debug(result)
        self.assertIsNotNone(result, "result should exist")
        
    def test_full_search(self):
        #make full search on the endpoint of BODC to see what it returns // test on the BODC server itself first
        test_source  = KG2EndpointSource(BODC_ENDPOINT)
        #make test qry using template from BODC
        log.info("full test")
        template_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sparql_templates')
        log.debug(f"template folder =  {template_folder}")
        j2sqb = J2SparqlBuilder(template_folder)
        variables = j2sqb.variables_in_query(name="rdf-predicates.sparql")
        log.info(f"all variables {variables}")
        querry = j2sqb.build_sparql_query(name="rdf-predicates.sparql", variables= {'regex':"http://www.w3.org/1999/02/22-rdf-syntax-ns#type"})
        log.debug(querry)
        result = test_source.query(querry)
        log.debug(result)
        self.assertIsNotNone(result, "result should exist")
        self.assertGreater(len(result.__dict__['_data']),0,"length result should be greater then 0")
        self.assertEqual(len(result.__dict__['_data']),1,"result should be equal to 1")
        ispresentC = False
        for row in result.__dict__['_data']: #TODO:ask marc for a better way to handle this
            if row["predicate"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                ispresentC = True
        self.assertTrue(ispresentC,"predicate http://www.w3.org/1999/02/22-rdf-syntax-ns#type was not present in the results")
if __name__ == "__main__":
    run_single_test(__file__)
