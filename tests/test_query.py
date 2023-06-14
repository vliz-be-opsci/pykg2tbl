import pytest

from pykg2tbl import KGSource, QueryResult
from pykg2tbl.exceptions import (
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)
from pykg2tbl.query import QueryResultFromListDict
from tests.const import TTL_FILES_QUERY_RESULT
from tests.util4tests import run_single_test


@pytest.mark.parametrize(
    "query_response, QueryType",
    [
        (TTL_FILES_QUERY_RESULT, QueryResultFromListDict),
    ],
)
def test_factory_choice(query_response, QueryType):
    query_result = QueryResult.build(query_response)
    assert type(query_result) == QueryType


class DummyQueryResult(QueryResult):
    pass  # pragma: no cover


@pytest.mark.parametrize(
    "constructor, CustomException",
    [(KGSource, NotASubClass), (DummyQueryResult, NoCompatibilityChecker)],
)
def test_class_register_raises(constructor, CustomException):
    with pytest.raises(CustomException) as exc:
        QueryResult.register(constructor)
    assert exc.type == CustomException


@pytest.mark.parametrize(
    "query_response, CustomException",
    [(["test"], WrongInputFormat), ("test", WrongInputFormat)],
)
def test_class_build_raises(query_response, CustomException):
    with pytest.raises(CustomException) as exc:
        QueryResult.build(query_response)
    assert exc.type == CustomException


if __name__ == "__main__":
    run_single_test(__file__)
