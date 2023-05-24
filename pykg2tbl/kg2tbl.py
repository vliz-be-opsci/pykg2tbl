import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

from pykg2tbl.named_query import NamedQuery, QueryResult

log = logging.getLogger(__name__)


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

    def exec(self, query: str, output_file: str, sep: str):
        """
        Service that will make query a provided kgsource and
            export a tabular data file based on the users preferences.

        :param str query: named template sparql
        :param str output_file: file to write query output as a table
        :param str sep: table separator

        """
        result = self.query(query)
        result.as_csv(output_file, sep)


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
        for f in files:
            log.debug(f"loading graph from file {f}")
            try:
                graph_to_add = g.parse(f)
            except Exception as e:
                log.exception(e)
                file_extension = f.split(".")[-1]
                graph_to_add = g.parse(f, format=file_extension)

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
        return NamedQuery(KGFileSource.query_result_to_dict(reslist))


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
            # TODO: Allow for mutiple return formats,
            #   even reading the format from the endpoint.
            ep.setReturnFormat("json")
            resdict = ep.query().convert()
            reslist = reslist + KG2EndpointSource.query_result_to_dict(resdict)

        query_result = NamedQuery(reslist)
        return query_result


def check_source(source: Union[str, Tuple[str, ...], List]) -> str:
    """
    Check the source type. Restrain only to files, or endpoints.
        If there is multiple sources, it will only get the type of the first
        path, which means it does not allow for different source types
        be passed in the same object.

    :param source: source of graph
    """
    if isinstance(source, tuple) or isinstance(source, list):
        return check_source(source[0])
    source_type = "file"
    if source.startswith("http"):
        query_ask = "ask where {?s ?p [].}"
        ep = SPARQLWrapper(source)
        ep.setQuery(query_ask)
        content_type = ep.query().info()["content-type"]
        if "sparql" in content_type:
            source_type = "endpoint"
    return source_type


def KG2Table(*source: Union[str, Tuple[str, ...], List]):
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
