# Use this file to describe the datamodel handled by this module
# we recommend using abstract classes to achieve proper service and interface 
# insulation
import csv
import logging
from abc import ABC, abstractmethod

from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

log = logging.getLogger(__name__)


class QueryResult:
    """
    Class that incompases the result from a performed query

    :param data: query result data in the form of a list of dictionaries
    """

    def __init__(self, data: dict):
        log.info(data)
        self._data = data  # TODO pandas dataframe

    def __str__(self):
        # TODO consider something smarter then this:
        return str(self._data)

    # be useful towards multiple ways of exporting (e.g. save as csv)
    # TODO allow conversion to table / list/ dict/ whatnot with pandas
    def as_csv(self, fileoutputlocation: str, sep: str = ","):
        """
        convert and outputs csv file from result query

        :param fileoutputlocation: location + filename where the csv should be written to.
        :param sep: delimiter that should be used for writing the csv file.
        """
        # open the file in the write mode
        f = open(fileoutputlocation, "w", newline="")
        # create the csv writer
        writer = csv.DictWriter(f, self._data[0].keys(), delimiter=sep)
        # write a row to the csv file
        for row in self._data:
            writer.writerow(row)
        # close the file
        f.close()


## create abstract class for making a contract by design for devs ##
class KGSource(ABC):
    @abstractmethod
    def query(self, sparql: str) -> QueryResult:
        """
        function that queries data with the given sparql

        :param sparql: sparql statement logic for querying data.
        """
        pass


## create classes for making the kg context and query factory graph
class KGFileSource(KGSource):
    """
    Class that makes a KGSource from given turtle file(s)

    :param *files: turtle files that should be converted into a single knowlegde graph.
    """

    def __init__(self, *files):
        super().__init__()
        self.graph = None
        g = Graph()
        for f in files:
            log.debug(f"loading graph from file {f}")
            graph_to_add = g.parse(f)
            self.graph = (
                graph_to_add
                if self.graph is None
                else self.graph + graph_to_add
            )

    @staticmethod
    def reslist_to_dict(reslist: list):
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]
        # TODO decide later on proper conversion to remove rdflib specifics and create reusable data dict for conversion through query results (pandas wrapper)

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult(KGFileSource.reslist_to_dict(reslist))


## create class for KG based on endpoint
class KG2EndpointSource(KGSource):
    """
    Class that makes a KGSource from given url endpoint

    :param url: url of the endpoint to make the KGSource from.
    """

    def __init__(self, url):
        super().__init__()
        self.endpoint = url

    @staticmethod
    def reslist_to_dict(reslist: list):
        return [
            {k: row[k]["value"] for k in row}
            for row in reslist["results"]["bindings"]
        ]
        # TODO decide later on proper conversion to remove rdflib specifics and create reusable data dict for conversion through query results (pandas wrapper)

    def query(self, sparql: str) -> QueryResult:
        ep = SPARQLWrapper(self.endpoint)
        ep.setQuery(sparql)
        ep.setReturnFormat("json")
        reslist = ep.query().convert()
        return QueryResult(KG2EndpointSource.reslist_to_dict(reslist))


class SparqlBuilder(ABC):
    @abstractmethod
    def build_sparql_query(self, name: str, **variables):
        """
        Builds the named sparql query by applying the provided params

        :param name: Name of the query.
        :param variables: Dict of all the variables to give to the template to make the sparql query.

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


## class tbl service
class KG2TblService:
    """
    Service that will make query a provided kgsource and export a tabular data file based on the users preferences.

    :param source: source of graph
    """

    def __init__(self, source: KGSource) -> None:
        self.source = source

    def exec(self, query: str, output_file: str, sep: str):
        result = self.source.query(query)
        result.as_csv(output_file, sep)
