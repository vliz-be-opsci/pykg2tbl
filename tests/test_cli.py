import pytest
import sys
import os
from util4tests import enable_test_logging, run_single_test, log

from pykg2tbl import KG2TblService, KGFileSource, KG2EndpointSource, J2SparqlBuilder
from pykg2tbl.__main__ import main as kg2tbl



def test_basic():
    kg2tbl('-i tests/sources/01-persons-shape.ttl tests/sources/02-person.ttl -o /tmp/test_kg2tbl_vliz.csv -t all.sparql'.split(' '))
    pass

if __name__ == "__main__":
    run_single_test(__file__)
