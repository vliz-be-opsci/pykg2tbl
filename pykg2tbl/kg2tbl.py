import logging
from abc import ABC, abstractmethod
from typing import Callable, Generator, Iterable, List, Tuple, Union

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

from pykg2tbl.exceptions import (
    CompatibilityCheckerNotCallable,
    MultipleSourceTypes,
    NoCompatibilityChecker,
    NoGraphSource,
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

    registry = set()

    @staticmethod
    def register(constructor):
        # assert that constructor is for a subclass of QueryResult
        # e.g. check if method check_compatibility is present
        if not issubclass(constructor, KGSource):
            raise NotASubClass(parent_class="KGSource")
        check_compatibility_function = getattr(
            constructor, "check_compatibility", False
        )
        if not check_compatibility_function:
            raise NoCompatibilityChecker
        if not isinstance(check_compatibility_function, Callable):
            raise CompatibilityCheckerNotCallable
        KGSource.registry.add(constructor)

    @staticmethod
    def build(*sources):
        """
        Kg2tbl main builder
            export a tabular data file based on the users preferences.
        :param sources: source of graph

        :return: KGSource class appropriate files.
        :rtype: KGSource
        """

        for constructor in KGSource.registry:
            if constructor.check_compatibility(*sources) is True:
                return constructor(*sources)

        raise WrongInputFormat(
            input_format="str, str, ...", class_failed="KGSource"
        )

    @staticmethod
    def detect_source_type(*sources: Union[str, Iterable]) -> str:
        """
        From the input sources it will get a list/generator with the types,
            It will check if there is only one type, and return it.
            Otherwise raise error for Multiple Sources.

        :param sources: files or endpoints
        :return: The source type of the given inputs.
        :rtype: str
        """
        source_type = generator_of_source_types(*sources)
        if isinstance(source_type, Iterable):
            # In case the source type is a generator
            source_type = [f for f in source_type]
            source_type = set(source_type)
            # For multiple inputs they need to have the same source_type
            if len(source_type) > 1:
                raise MultipleSourceTypes
            source_type = list(source_type)[0]
        return source_type


class KGGraphSource(KGSource):
    """
    Class that makes a KGSource from instatiated graphs.

    :param graph: rdf knowledge graph.
    """

    def __init__(self, graph: Graph) -> None:
        super().__init__()
        assert graph is not None, NoGraphSource
        self.graph = graph

    def parse(self, *sources):
        for f in sources:
            log.debug(f"loading graph from file {f}")
            try:
                self.graph.parse(f)
            except Exception as e:
                log.exception(e)
                file_extension = f.split(".")[-1]
                self.graph.parse(f, format=file_extension)

    @staticmethod
    def query_result_to_list_dicts(reslist: list) -> list:
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult.build(
            KGGraphSource.query_result_to_list_dicts(reslist), query=sparql
        )

    @staticmethod
    def check_compatibility(*graph):
        return isinstance(graph[0], Graph)


class KGFileSource(KGGraphSource):
    """
    Class that makes a KGSource from given turtle file(s)

    :param *sources: turtle files that should be converted into a single
        knowledge graph.
    """

    def __init__(self, *sources):
        graph = Graph()
        super().__init__(graph)
        self.parse(*sources)

    @staticmethod
    def check_compatibility(*sources: Tuple):
        source_type = KGSource.detect_source_type(*sources)
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

    def query(self, sparql: str, return_format="json") -> QueryResult:
        reslist = []
        for url in self.endpoints:
            ep = SPARQLWrapper(url)
            ep.setQuery(sparql)
            # TODO: Allow reading the format from the endpoint.
            ep.setReturnFormat(return_format)
            resdict = ep.query().convert()
            reslist = reslist + KG2EndpointSource.query_result_to_list_dicts(
                resdict
            )

        query_result = QueryResult.build(reslist, query=sparql)
        return query_result

    @staticmethod
    def check_compatibility(*sources):
        source_type = KGSource.detect_source_type(*sources)
        return source_type == "endpoint"


KGSource.register(KGGraphSource)
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
        ep.setReturnFormat("json")
        query_info = ep.query().info()
        content_type = query_info.get("content-type", "")
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
