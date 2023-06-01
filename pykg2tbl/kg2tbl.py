import logging
from abc import ABC, abstractmethod
from typing import Generator, Iterable, List, Tuple, Union

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
    def query_result_to_list_dicts(reslist: list) -> List:
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
        # e.g. check if method check_compatibility is present
        if not issubclass(constructor, KGSource):
            raise NotASubClass(parent_class="KGSource")
        if not getattr(constructor, "check_compatibility", False):
            raise NoCompatibilityChecker
        KGSource.registry.add(constructor)

    @staticmethod
    def build(*files):
        """
        Kg2tbl main builder
            export a tabular data file based on the users preferences.
        :param source: source of graph

        :return: KGSource class appropriate files.
        :rtype: KGSource
        """

        for constructor in KGSource.registry:
            if constructor.check_compatibility(*files) is True:
                return constructor(*files)

        raise WrongInputFormat(
            input_format="str, str, ...", class_failed="KGSource"
        )

    @staticmethod
    def detect_source_type(*files: Union[str, Iterable]) -> str:
        """
        From the input sources it will get a list/generator with the types,
            It will check if there is only one type, and return it.
            Otherwise raise error for Multiple Sources.

        :param files: files or endpoints
        :return: The source type of the given inputs.
        :rtype: str
        """
        source_type = generator_of_source_types(*files)
        if isinstance(source_type, Iterable):
            # In case the source type is a generator
            source_type = [f for f in source_type]
            source_type = set(source_type)
            # For multiple inputs they need to have the same source_type
            if len(source_type) != 1:
                raise MultipleSourceTypes
            source_type = list(source_type)[0]
        return source_type


class KGFileSource(KGSource):
    """
    Class that makes a KGSource from given turtle file(s)

    :param *files: turtle files that should be converted into a single
        knowledge graph.
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
    def query_result_to_list_dicts(reslist: list) -> list:
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult.build(
            KGFileSource.query_result_to_list_dicts(reslist), query=sparql
        )

    @staticmethod
    def check_compatibility(*files: Tuple):
        source_type = KGSource.detect_source_type(*files)
        return source_type == "file"


class KG2EndpointSource(KGSource):
    """
    Class that makes a KGSource from given url endpoint

    :param url: url of the endpoint to make the KGSource from.
    """

    def __init__(self, *urls):
        super().__init__()
        self.endpoints = [url for url in urls]

    @staticmethod
    def query_result_to_list_dicts(reslist: list) -> list:
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
            reslist = reslist + KG2EndpointSource.query_result_to_list_dicts(
                resdict
            )

        query_result = QueryResult.build(reslist, query=sparql)
        return query_result

    @staticmethod
    def check_compatibility(*files):
        source_type = KGSource.detect_source_type(*files)
        return source_type == "endpoint"


KGSource.register(KGFileSource)
KGSource.register(KG2EndpointSource)


def detect_single_source_type(source: str) -> str:
    """
    Check the source type. Restrain only to files, or endpoints

    :param source: files or endpoints
    :return: The source type of the given input.
        Endpoint or File
    :rtype: str

    """
    source_type = "file"
    if source.startswith("http"):
        query_ask = "ask where {?s ?p [].}"
        ep = SPARQLWrapper(source)
        ep.setQuery(query_ask)
        content_type = ep.query().info()["content-type"]
        if "sparql" in content_type:
            source_type = "endpoint"
    return source_type


def generator_of_source_types(*source: Union[str, Iterable]) -> Generator:
    """
    Check the source type. Restrain only to files, or endpoints.
        It will return a generator where each item is a source_type.

    :param source: files or endpoints
    """
    for src in source:
        if src and isinstance(src, str):
            yield detect_single_source_type(src)
        else:
            yield None
