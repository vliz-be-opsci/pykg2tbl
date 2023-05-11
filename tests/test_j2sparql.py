from util4tests import log, run_single_test

from pykg2tbl import J2SparqlBuilder

N = 723
ALL_QUERY = f"""

SELECT *
WHERE {{
    ?s ?p ?o.
}}
LIMIT {N}"""


def test_basic_query_sparql():
    j2sqb = J2SparqlBuilder()
    qry = j2sqb.build_sparql_query("all.sparql", N=N)
    assert qry is not None, "result qry should exist"
    log.debug(f"qry={qry}")
    log.debug(f"expected={ALL_QUERY}")
    assert qry == ALL_QUERY, "unexpected qry result"


def test_get_variables_sparql_query():
    # TODO write test to get all the variables from a sparql template
    j2sqb = J2SparqlBuilder()
    variables = j2sqb.variables_in_query(name="all.sparql")
    log.info(f"all variables {variables}")
    assert variables == {"N"}, "unexpected variables in all.sparql"


if __name__ == "__main__":
    run_single_test(__file__)
