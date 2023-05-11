import os

from util4tests import log, run_single_test

from pykg2tbl.j2.jinja_sparql_builder import J2SparqlBuilder
from pykg2tbl.service import KG2EndpointSource, KGFileSource

ALL_TRIPLES_SPARQL = "SELECT * WHERE { ?s ?p ?o. } LIMIT 25"
# TODO provide some registry of endpoints to choose from --> issue #4
#   then replace next line!
BODC_ENDPOINT = "http://vocab.nerc.ac.uk/sparql/sparql"


def test_basic_filesource():
    file_base = os.path.join(os.path.abspath(os.path.dirname(__file__)), "sources")
    log.debug(f"test using files in {file_base}")

    # TODO provide better input files to test with
    test_source = KGFileSource(
        os.path.join(file_base, "02-person.ttl"),
        os.path.join(file_base, "01-persons-shape.ttl"),
    )
    result = test_source.query(ALL_TRIPLES_SPARQL)
    log.debug(result)
    assert result is not None, "result should exist"
    log.debug(f"result ==> {result}")

    # TODO some decent result iteration / representation / dataframe?
    #   allow it to assert
    #       -  length of result
    #       -  content being present or not


def test_basic_endpoint():
    test_source = KG2EndpointSource(BODC_ENDPOINT)
    result = test_source.query(ALL_TRIPLES_SPARQL)
    # log.debug(result)
    assert result is not None, "result should exist"
    # TODO more elaborate assertions


def test_full_search():
    # make full search on the endpoint of BODC to see what it returns test on the BODC
    #   server itself first
    test_source = KG2EndpointSource(BODC_ENDPOINT)
    # make test qry using template from BODC
    log.info("full test")
    j2sqb = J2SparqlBuilder()

    qry = j2sqb.build_sparql_query("bodc-find.sparql", collections=["P01"], regex=".*orca.*")
    log.debug(f"query = {qry}")
    result = test_source.query(qry)
    log.debug(f"result = {result}")

    # TODO provide actual assertions on length and content once we have some
    #   decent result-set wrapper/inspection model / dataframe?


if __name__ == "__main__":
    run_single_test(__file__)
