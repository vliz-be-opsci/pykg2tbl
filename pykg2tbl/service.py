import csv
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import pandas as pd
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

log = logging.getLogger(__name__)


class QueryResult(ABC):
    """
    Class that incompases the result from a performed query

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
        """
        convert and outputs csv file from result query

        :param fileoutputlocation: location + filename where the csv
            should be written to.
        :param sep: delimiter that should be used for writing the csv file.
        """
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
        """
        Returns the list of query responses

        :return: List of query responses
        :rtype: list
        """
        return self._data

    def to_dict(self) -> dict:
        """
        Converts the result query to a dictionary.
            Each key having a list with every query row.

        :return: Query as a dictionary.
        :rtype: dict
        """
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
        """
        Converts the result query to a pandas dataframe.

        :return: Query as a dataframe.
        :rtype: pd.Dataframe
        """
        query_df = pd.DataFrame()
        for row in self.to_list():
            query_df = pd.concat(
                [query_df, pd.DataFrame(row, index=[0])], ignore_index=True
            )

        return query_df

    # In future the design to match UDAL will require to also expose metadata


# Create abstract class for making a contract by design for devs ##
class KGSource(ABC):
    @abstractmethod
    def query_result_to_dict(reslist: list) -> List:
        """
        From the query result build a standard list of dicts,
            where each key is the relation in the triplet.

        :param reslist: list with the query.
        """
        pass

    @abstractmethod
    def query(self, sparql: str) -> QueryResult:
        """
        Function that queries data with the given sparql

        :param sparql: sparql statement logic for querying data.
        """
        pass


# Create classes for making the kg context and query factory graph
class KGFileSource(KGSource):
    """
    Class that makes a KGSource from given turtle file(s)

    :param *files: turtle files that should be converted into a single
        knowlegde graph.
    """

    def __init__(self, *files):
        super().__init__()
        self.graph = None
        g = Graph()
        print(files)
        for f in files:
            log.debug(f"loading graph from file {f}")
            graph_to_add = g.parse(f)
            self.graph = (
                graph_to_add
                if self.graph is None
                else self.graph + graph_to_add
            )

    @staticmethod
    def query_result_to_dict(reslist: list):
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult(self.query_result_to_dict(reslist))


# Create class for KG based on endpoint
class KG2EndpointSource(KGSource):
    """
    Class that makes a KGSource from given url endpoint

    :param url: url of the endpoint to make the KGSource from.
    """

    def __init__(self, *url):
        super().__init__()
        self.endpoints = [f for f in url]

    @staticmethod
    def query_result_to_dict(reslist: list):
        return [
            {k: row[k]["value"] for k in row}
            for row in reslist["results"]["bindings"]
        ]

    def query(self, sparql: str) -> QueryResult:
        reslist = []
        for url in self.endpoints:
            ep = SPARQLWrapper(url)
            ep.setQuery(sparql)
            ep.setReturnFormat("json")
            resdict = ep.query().convert()
            reslist = reslist + self.query_result_to_dict(resdict)

        query_result = QueryResult(reslist)
        return query_result


def check_source(source: Union[str, Tuple[str, ...], List]) -> str:
    if isinstance(source, tuple) or isinstance(source, list):
        return check_source(source[0])
    source_type = "file"
    if source.startswith("http"):
        source_type = "endpoint"
    return source_type


def KG2TblFactory(*source: Union[str, Tuple[str, ...], List]):
    """
    Kg2tbl main builder
        export a tabular data file based on the users preferences.

    :param source: source of graph
    """

    source_type = check_source(source)

    localizers = {
        "file": KGFileSource,
        "endpoint": KG2EndpointSource,
    }

    return localizers[source_type](*source)


# class tbl service
class KG2TblService:
    """
    Service that will make query a provided kgsource and
        export a tabular data file based on the users preferences.

    :param source: source of graph
    """

    # TODO: We could just do the exec function inside KGSource and
    #   delete this class
    def __init__(self, *source) -> None:
        self.kgsource = KG2TblFactory(*source)

    def exec(self, query: str, output_file: str, sep: str):
        result = self.kgsource.query(query)
        result.as_csv(output_file, sep)


class SparqlBuilder(ABC):
    # TODO: check this
    @abstractmethod
    def build_sparql_query(self, name: str, **variables):
        """
        Builds the named sparql query by applying the provided params

        :param name: Name of the query.
        :param variables: Dict of all the variables given to the template to
            make the sparql query.

        :type name: str
        """
        pass

    @abstractmethod
    def variables_in_query(self, name: str):
        """
        Return the set of all the variable names applicable to the named query

        :param name: [Name of the query.]
        :type name: str

        :return: the set of all variables applicable to the named query.
        :rtype: set

        """
        pass
