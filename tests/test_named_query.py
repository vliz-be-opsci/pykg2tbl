import pytest
from util4tests import TTL_FILES_QUERY_RESULT, run_single_test

from pykg2tbl.exceptions import WrongInputFormat
from pykg2tbl.named_query import NamedQuery, QueryResultFromListDict


@pytest.mark.parametrize(
    "query_response, QueryType",
    [
        (TTL_FILES_QUERY_RESULT, QueryResultFromListDict),
    ],
)
def test_factory_choice(query_response, QueryType):
    query_result = NamedQuery(query_response)
    assert type(query_result) == QueryType


@pytest.mark.parametrize(
    "query_response, CustomException",
    [(["test"], WrongInputFormat), ("test", WrongInputFormat)],
)
def test_factory_raises(query_response, CustomException):
    with pytest.raises(CustomException) as exc:
        NamedQuery(query_response)
    assert exc.type == CustomException


if __name__ == "__main__":
    run_single_test(__file__)
