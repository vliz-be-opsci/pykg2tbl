import logging
from abc import ABC, abstractmethod
from typing import Iterable, List, Union

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

from pykg2tbl.exceptions import (
    MultipleSourceTypes,
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)
from pykg2tbl.query import QueryResult

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
        pass  # pragma: no cover

    @abstractmethod
    def query(self, sparql: str) -> QueryResult:
        """
        Function that queries data with the given sparql

        :param sparql: sparql statement logic for querying data.
        """
        pass  # pragma: no cover

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

    registry = set()

    @staticmethod
    def register(constructor):
        # assert that constructor is for a subclass of QueryResult
        # e.g. check if method check_compatability is present
        if not issubclass(constructor, KGSource):
            raise NotASubClass
        if not getattr(constructor, "check_compatability", False):
            raise NoCompatibilityChecker
        KGSource.registry.add(constructor)

    @staticmethod
    def build(*files):
        """
        Named main builder
            Accepts a query response and a query.

        :param list data: query response. A list of dictionaries.
        :param str query: query made.
        :return: QueryResult class apropriate for the query response.
        :rtype: QueryResult
        """

        for constructor in KGSource.registry:
            if constructor.check_compatability(*files) is True:
                return constructor(*files)

        raise WrongInputFormat


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
    def query_result_to_dict(reslist: list) -> list:
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult.build(
            KGFileSource.query_result_to_dict(reslist), query=sparql
        )

    @staticmethod
    def check_compatability(*files):
        source_type = get_single_type_from_source_list(files)
        return source_type == "file"


class KG2EndpointSource(KGSource):
    """
    Class that makes a KGSource from given url endpoint

    :param url: url of the endpoint to make the KGSource from.
    """

    def __init__(self, *url):
        super().__init__()
        self.endpoints = [f for f in url]

    @staticmethod
    def query_result_to_dict(reslist: list) -> list:
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

        query_result = QueryResult.build(reslist, query=sparql)
        return query_result

    @staticmethod
    def check_compatability(*files):
        source_type = get_single_type_from_source_list(files)
        return source_type == "endpoint"


KGSource.register(KGFileSource)
KGSource.register(KG2EndpointSource)


def detect_single_source_type(source: str) -> str:
    source_type = "file"
    if source.startswith("http"):
        query_ask = "ask where {?s ?p [].}"
        ep = SPARQLWrapper(source)
        ep.setQuery(query_ask)
        content_type = ep.query().info()["content-type"]
        if "sparql" in content_type:
            source_type = "endpoint"
    return source_type


def detect_source_type(source: Union[str, Iterable]) -> str:
    """
    Check the source type. Restrain only to files, or endpoints.
        If there is multiple sources, it will only get the type of the first
        path, which means it does not allow for different source types
        be passed in the same object.

    :param source: source of graph
    """
    if isinstance(source, Iterable):
        for src in source:
            if src:
                yield detect_single_source_type(src)
    else:
        return detect_single_source_type(source)


def get_single_type_from_source_list(files: Union[str, Iterable]) -> str:
    source_type = detect_source_type(files)
    if isinstance(source_type, Iterable):
        # In case the source type is a generator
        source_type = [f for f in source_type]
        source_type = set(source_type)
        # For multiple inputs they need to have the same source_type
        if len(source_type) != 1:
            raise MultipleSourceTypes
        source_type = list(source_type)[0]
    return source_type
