import logging
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from pykg2tbl.exceptions import (
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)

log = logging.getLogger(__name__)


class QueryResult(ABC):
    """
    Class that incompases the result from a performed query

    :param list data: query result data
    :param str query: query

    """

    @abstractmethod
    def as_csv(self, fileoutputlocation: str, sep: str = ","):
        """
        From the query result build a standard list of dicts,
            where each key is the relation in the triplet.

        :param reslist: list with the query.
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_list(self) -> List:
        """
        Returns the list of query responses

        :return: List of query responses
        :rtype: list
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Converts the result query to a dictionary.
            Each key having a list with every query row.

        :return: Query as a dictionary.
        :rtype: dict
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the result query to a pandas dataframe.

        :return: Query as a dataframe.
        :rtype: pd.Dataframe
        """
        pass  # pragma: no cover

    registry = set()

    @staticmethod
    def register(constructor):
        if not issubclass(constructor, QueryResult):
            raise NotASubClass
        if not getattr(constructor, "check_compatibility", False):
            raise NoCompatibilityChecker
        QueryResult.registry.add(constructor)

    @staticmethod
    def build(data: list, query: str = ""):
        """
        QueryResult main builder
            Accepts a query response and a query.

        :param list data: query response.
        :param str query: query made.
        :return: QueryResult class apropriate for the query response.
        :rtype: QueryResult
        """

        for constructor in QueryResult.registry:
            if constructor.check_compatibility(data, query) is True:
                return constructor(data, query)

        raise WrongInputFormat


class QueryResultFromListDict(QueryResult):
    """
    Class that incompases the result from a performed query.
        When the result is return as a list of dictionaries.

    :param list data: query result data in the form of a list of dictionaries
    :param str query: query

    """

    def __init__(self, data: list, query: str = ""):
        self._data = data
        self.query = query

    def __str__(self):
        df = self.to_dataframe()
        return str(df)

    def __len__(self):
        return len(self._data)

    def as_csv(self, fileoutputlocation: str, sep: str = ","):
        data = self.to_dataframe()
        data.to_csv(fileoutputlocation, sep=sep)

    def to_list(self) -> List:
        return self._data

    def to_dict(self) -> dict:
        list_data = self.to_list()
        dict_keys = list_data[0].keys()
        query_dict = {}
        for row in list_data:
            for key in dict_keys:
                if key in query_dict:
                    query_dict[key] = query_dict[key] + [row[key]]
                else:
                    query_dict[key] = [row[key]]
        return query_dict

    def to_dataframe(self) -> pd.DataFrame:
        query_df = pd.DataFrame()
        for row in self.to_list():
            query_df = pd.concat(
                [query_df, pd.DataFrame(row, index=[0])], ignore_index=True
            )

        return query_df

    # In future the design to match UDAL will require to also expose metadata
    @staticmethod
    def check_compatibility(data, query) -> bool:
        is_list_of_dicts = False
        if isinstance(data, list):
            is_list_of_dicts = True
            for iter in data:
                is_list_of_dicts = isinstance(iter, dict) and is_list_of_dicts

        return is_list_of_dicts and isinstance(query, str)


QueryResult.register(QueryResultFromListDict)


class SparqlBuilder(ABC):
    @abstractmethod
    def build_sparql_query(self, name: str, **variables):
        """
        Builds the named sparql query by applying the provided params

        :param name: Name of the query.
        :param variables: Dict of all the variables given to the template to
            make the sparql query.

        :type name: str
        """
        pass  # pragma: no cover

    @abstractmethod
    def variables_in_query(self, name: str):
        """
        Return the set of all the variable names applicable to the named query

        :param name: [Name of the query.]
        :type name: str

        :return: the set of all variables applicable to the named query.
        :rtype: set

        """
        pass  # pragma: no cover
