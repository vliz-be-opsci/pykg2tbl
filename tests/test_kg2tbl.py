import pandas as pd
import pytest

from pykg2tbl import (
    DEFAULT_TEMPLATES_FOLDER,
    DefaultSparqlBuilder,
    KGSource,
    QueryResult,
)
from pykg2tbl.exceptions import (
    CompatibilityCheckerNotCallable,
    MultipleSourceTypes,
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)
from pykg2tbl.kg2tbl import KG2EndpointSource, KGFileSource
from tests.const import (
    ALL_TRIPLES_SPARQL,
    BODC_ENDPOINT,
    TTL_FILE_IN_URI,
    TTL_FILES_TO_TEST,
)
from tests.util4tests import log, run_single_test


@pytest.mark.parametrize(
    "source, KGType",
    [
        (TTL_FILES_TO_TEST, KGFileSource),
        ([BODC_ENDPOINT], KG2EndpointSource),
        ([TTL_FILE_IN_URI], KGFileSource),
    ],
)
def test_factory_choice(source, KGType):
    source_KG2tbl = KGSource.build(*source)
    assert type(source_KG2tbl) == KGType


@pytest.mark.parametrize(
    "source, query, query_response_length",
    [
        (TTL_FILES_TO_TEST, ALL_TRIPLES_SPARQL, 20),
        (BODC_ENDPOINT, ALL_TRIPLES_SPARQL, 25),
        (TTL_FILE_IN_URI, ALL_TRIPLES_SPARQL, 25),
    ],
)
def test_query(source, query, query_response_length):
    if isinstance(source, str):
        source = [source]
    source_KG2tbl = KGSource.build(*source)
    result = source_KG2tbl.query(query)
    assert result._data is not None
    assert set(result._data[0].keys()) == set(["s", "o", "p"])
    assert len(result._data) == query_response_length
    assert len(result) == query_response_length


def test_query_functions():
    source_KG2tbl = KGSource.build(*TTL_FILES_TO_TEST)
    result = source_KG2tbl.query(ALL_TRIPLES_SPARQL)

    assert type(result.to_list()) == list
    assert type(result.to_dict()) == dict
    assert type(result.to_dataframe()) == pd.DataFrame


class DummyKGSource(KGSource):
    pass  # pragma: no cover


class Dummy2KGSource(KGSource):
    @property
    def check_compatibility():
        return None


@pytest.mark.parametrize(
    "constructor, CustomException",
    [
        (QueryResult, NotASubClass),
        (DummyKGSource, NoCompatibilityChecker),
        (Dummy2KGSource, CompatibilityCheckerNotCallable),
    ],
)
def test_class_register_raises(constructor, CustomException):
    with pytest.raises(CustomException) as exc:
        KGSource.register(constructor)
    assert exc.type == CustomException


@pytest.mark.parametrize(
    "files, CustomException",
    [
        ([{"test"}], WrongInputFormat),
        ([BODC_ENDPOINT, *TTL_FILES_TO_TEST], MultipleSourceTypes),
    ],
)
def test_class_build_raises(files, CustomException):
    with pytest.raises(CustomException) as exc:
        KGSource.build(*files)
    assert exc.type == CustomException


def test_full_search():
    # make full search on the endpoint of BODC to see what it returns test on
    #   the BODC server itself first
    test_source = KG2EndpointSource(BODC_ENDPOINT)
    # make test qry using template from BODC
    log.info("full test")
    j2sqb = DefaultSparqlBuilder(DEFAULT_TEMPLATES_FOLDER)

    qry = j2sqb.build_syntax(
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
