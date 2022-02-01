# Use this file to describe the datamodel handled by this module
# we recommend using abstract classes to achieve proper service and interface insulation
from abc import ABC, abstractmethod
import rdflib, csv

class QueryResult():
    def __init__(self, data: dict):
        self._data = data #TODO pandas dataframe
    # allow conversion to table / list/ dict/ whatnot with pandas
    
    # be useful towards multiple ways of exporting (e.g. save as csv)
    def as_csv(self, fileoutputlocation:str, sep:str=","):
        pass  #TODO  dmp dict 2 csv using csv module 
    
## create abstract class for making a contract by design for devs ##
class KGSource(ABC): 
    @abstractmethod
    def query(self, sparql:str) -> QueryResult:
        pass
    
    @staticmethod
    def reslist_to_dict(reslist:list):
        return reslist #TODO decide later on proper conversion to remove rdflib specifics and create reusable data dict for conversion through query results (pandas wrapper)

## create classes for making the kg context and query factory graph
class KGFileSource(KGSource):
    def __init__(self, files):
        super().__init__()
        self.graph = None
        #TODO intantiate graph and load it with all files
        for f in files:
            g_add = g_add.parse(f)
            self.graph = self.graph + g_add
        
    def query(self, sparql: str) -> QueryResult:
        reslist = self.graph.query(sparql)
        return QueryResult(KGSource.reslist_to_dict(reslist))
    
## create class for KG based on endpoint
class KG2EndpointSource(KGSource):
    def __init__(self, url):
        super().__init__()
        self.endpoint = None # check how to make an endpoint
    
    def query(self, sparql: str) -> QueryResult:
        reslist = self.endpoint.query(sparql)
        return QueryResult(KGSource.reslist_to_dict(reslist))
    
## class tbl service
class KG2TblService():
    def __init__(self, source:KGSource) -> None:
        self.source = source
        
    def exec(self,query:str, output_file:str):
        result = self.source.query(query)
        result.as_csv(output_file)