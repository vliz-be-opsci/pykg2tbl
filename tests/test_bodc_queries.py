# TODO the imports for clients should be able to be just on the toplevel:
# from pykg2tbl import KGSource, QueryResult, DefaultQueryBuilder
from const import BODC_ENDPOINT, FAKE_DUMP_FILE, P06_DUMP_FILE

from pykg2tbl.j2.jinja_sparql_builder import \
    J2SparqlBuilder as DefaultQueryBuilder
from pykg2tbl.kg2tbl import KGSource
from pykg2tbl.query import QueryResult


def test_bodc_listing_published_P06():
    nerc_server: KGSource = KGSource.build(BODC_ENDPOINT)
    qry: str = DefaultQueryBuilder().build_sparql_query(
        name="bodc-listing.sparql", cc="P06"
    )

    result: QueryResult = nerc_server.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) > 0, "the result should not be empty"


def test_bodc_listing_knowndump_P06():
    ttl_dump = P06_DUMP_FILE
    assert (
        ttl_dump.exists()
    ), f"need input file { str(ttl_dump) } for test to work"
    in_memory: KGSource = KGSource.build(str(ttl_dump))
    qry: str = DefaultQueryBuilder().build_sparql_query(
        name="bodc-listing.sparql", cc="P06"
    )

    result: QueryResult = in_memory.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) == 418, "the known dated dump had exactly 24 members"


def test_bodc_listing_fakedump():
    ttl_dump = FAKE_DUMP_FILE
    assert (
        ttl_dump.exists()
    ), f"need input file { str(ttl_dump) } for test to work"
    in_memory: KGSource = KGSource.build(str(ttl_dump))
    qry: str = DefaultQueryBuilder().build_sparql_query(
        name="bodc-listing.sparql", cc="fake"
    )

    result: QueryResult = in_memory.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) == 3, "the known fake dump has exactly 3 members"
