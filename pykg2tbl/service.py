# Use this file to describe the datamodel handled by this module
# we recommend using abstract classes to achieve proper service and interface insulation
from abc import ABC, abstractmethod
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper
import logging
import csv, json

log = logging.getLogger(__name__)

class QueryResult():

    def __init__(self, data: dict):
        self._data = data #TODO pandas dataframe
    # allow conversion to table / list/ dict/ whatnot with pandas

    def __str__(self):
        # TODO consider something smarter then this:
        return str(self._data)

    # be useful towards multiple ways of exporting (e.g. save as csv)
    def as_csv(self, fileoutputlocation:str, sep:str=","):
        pass  #TODO  dmp dict 2 csv using csv module

## create abstract class for making a contract by design for devs ##
class KGSource(ABC):
    @abstractmethod
    def query(self, sparql:str) -> QueryResult:
        pass

## create classes for making the kg context and query factory graph
class KGFileSource(KGSource):
    def __init__(self, *files):
        super().__init__()
        self.graph = None
        #TODO intantiate graph and load it with all files
        g = Graph()
        for f in files:
            log.debug(f"loading graph from file {f}")
            graph_to_add = g.parse(f)
            self.graph = graph_to_add if self.graph is None else self.graph + graph_to_add

    @staticmethod
    def reslist_to_dict(reslist:list):
        return [{str(v):str(row[v]) for v in reslist.vars} for row in reslist]
        #TODO decide later on proper conversion to remove rdflib specifics and create reusable data dict for conversion through query results (pandas wrapper)

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult(KGFileSource.reslist_to_dict(reslist))

## create class for KG based on endpoint
class KG2EndpointSource(KGSource):
    def __init__(self, url):
        super().__init__()
        self.endpoint = url

    @staticmethod
    def reslist_to_dict(reslist:list):
        return [{k: row[k]["value"] for k in row} for row in reslist["results"]["bindings"]]
        #TODO decide later on proper conversion to remove rdflib specifics and create reusable data dict for conversion through query results (pandas wrapper)

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
    def variables_in_query(self, name:str):
        """
        Return the set of all the variable names applicable to the named query

        :param name: [Name of the query.]
        :type name: str
        
        :return: the set of all variables applicable to the named query.
        :rtype: set
        
        """
        pass

## class tbl service
class KG2TblService():
    def __init__(self, source:KGSource) -> None:
        self.source = source

    def exec(self,query:str, output_file:str):
        result = self.source.query(query)
        result.as_csv(output_file)
