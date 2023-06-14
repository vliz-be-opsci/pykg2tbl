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
    Class that encompasses the result from a performed query

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
    Class that encompasses the result from a performed query.
        When the result is return as a list of dictionaries.

    :param list data: query result data in the form of a list of dictionaries
    :param str query: query

    """

    def __init__(self, data: list, query: str = ""):
        self._data = data
        self.query = query

    def __str__(self):
        df = self.to_dataframe()
        _str = ""
        if self.query:
            _str = f"Query: \n{self.query} \n"
        _str = _str + f"Table: \n{str(df)}"
        return _str

    def __len__(self):
        return len(self._data)

    def as_csv(self, file_output_path: str, sep: str = ","):
        data = self.to_dataframe()
        data.to_csv(file_output_path, sep=sep, index=False)

    def to_list(self) -> List:
        return self._data

    def to_dict(self) -> dict:
        """
        Builds a dictionary where each key is a column from the query.
        In each key is a list with all the answer of the query.

        :return: The dictionary mapping the query table
        :rtype: dict
        """
        result_rows = self.to_list()
        result_dict = {}
        for row in result_rows:
            columns = row.keys()
            for key in columns:
                # on first use
                if key not in result_dict:
                    # initialise as list
                    result_dict[key] = list()
                # append to list
                result_dict[key] = result_dict[key] + [row[key]]
        return result_dict

    def to_dataframe(self) -> pd.DataFrame:
        result_df = pd.DataFrame()
        for row in self.to_list():
            result_df = pd.concat(
                [result_df, pd.DataFrame(row, index=[0])], ignore_index=True
            )

        return result_df

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
