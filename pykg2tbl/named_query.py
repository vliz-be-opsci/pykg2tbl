import csv
import logging
from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from pykg2tbl.exceptions import WrongInputFormat

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
        pass

    @abstractmethod
    def to_list(self) -> List:
        """
        Returns the list of query responses

        :return: List of query responses
        :rtype: list
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Converts the result query to a dictionary.
            Each key having a list with every query row.

        :return: Query as a dictionary.
        :rtype: dict
        """
        pass

    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the result query to a pandas dataframe.

        :return: Query as a dataframe.
        :rtype: pd.Dataframe
        """
        pass


class QueryResultFromListDict(QueryResult):
    """
    Class that incompases the result from a performed query.
        When the result is return as a list of dictionaries.

    :param list data: query result data in the form of a list of dictionaries
    :param str query: query

    """

    def __init__(self, data: list, query: str = ""):
        # log.info(data)
        self._data = data
        self.query = query

    def __str__(self):
        # TODO consider something smarter then this:
        return str(self._data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        # The iterator can work as the kind of choise, default to list.
        for i in self.to_list():
            yield i

    def as_csv(self, fileoutputlocation: str, sep: str = ","):
        try:
            data = self.to_dataframe()
        except Exception as e:
            log.error(e)
            data = self.to_list()
        if isinstance(data, pd.DataFrame):
            data.to_csv(fileoutputlocation, sep=sep)
        else:
            # open the file in the write mode
            with open(fileoutputlocation, "w", newline="") as f:
                # create the csv writer
                writer = csv.DictWriter(f, data[0].keys(), delimiter=sep)
                # write a row to the csv file
                for row in data:
                    writer.writerow(row)

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


def NamedQuery(data: list, query: str = "") -> QueryResult:
    """
    Named main builder
        Accepts a query response and a query.

    :param list data: query response. A list of dictionaries.
    :param str query: query made.
    :return: QueryResult class apropriate for the query response.
    :rtype: QueryResult
    """

    if isinstance(data, list):
        if isinstance(data[0], dict):
            return QueryResultFromListDict(data, query)
        else:
            raise WrongInputFormat
    else:
        raise WrongInputFormat
