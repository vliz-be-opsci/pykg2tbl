import glob
import os

import pandas as pd
import pytest
from util4tests import log, run_single_test

from pykg2tbl.j2.jinja_sparql_builder import J2SparqlBuilder
from pykg2tbl.service import KG2EndpointSource, KG2TblFactory, KGFileSource

ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
# TODO provide some registry of endpoints to choose from --> issue #4
#   then replace next line!
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"

FILES_SOURCE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "sources"
)
TTL_FILES_TO_TEST = glob.glob(f"{FILES_SOURCE}/*.ttl")


@pytest.mark.parametrize(
    "source, KGType",
    [(TTL_FILES_TO_TEST, KGFileSource), (BODC_ENDPOINT, KG2EndpointSource)],
)
def test_factory_choice(source, KGType):
    if isinstance(source, str):
        source = [source]
    source_KG2tbl = KG2TblFactory(*source)
    assert type(source_KG2tbl) == KGType


@pytest.mark.parametrize(
    "source, query, query_response_length",
    [
        (TTL_FILES_TO_TEST, ALL_TRIPLES_SPARQL, 20),
        (BODC_ENDPOINT, ALL_TRIPLES_SPARQL, 25),
    ],
)
def test_query(source, query, query_response_length):
    if isinstance(source, str):
        source = [source]
    source_KG2tbl = KG2TblFactory(*source)
    result = source_KG2tbl.query(query)
    assert result._data is not None
    assert set(result._data[0].keys()) == set(["s", "o", "p"])
    assert len(result._data) == query_response_length


def test_query_functions():
    source_KG2tbl = KG2TblFactory(*TTL_FILES_TO_TEST)
    result = source_KG2tbl.query(ALL_TRIPLES_SPARQL)

    assert type(result.to_list()) == list
    assert type(result.to_dict()) == dict
    assert type(result.to_dataframe()) == pd.DataFrame


def test_full_search():
    # make full search on the endpoint of BODC to see what it returns test on
    #   the BODC server itself first
    test_source = KG2EndpointSource(BODC_ENDPOINT)
    # make test qry using template from BODC
    log.info("full test")
    j2sqb = J2SparqlBuilder()

    qry = j2sqb.build_sparql_query(
        "bodc-find.sparql", collections=["P01"], regex=".*orca.*"
    )
    log.debug(f"query = {qry}")
    result = test_source.query(qry)
    log.debug(f"result = {result}")
    assert result._data is not None
    assert set(result._data[0].keys()) == set(
        ["uri", "identifier", "prefLabel"]
    )
    assert len(result._data) == 2


if __name__ == "__main__":
    run_single_test(__file__)
