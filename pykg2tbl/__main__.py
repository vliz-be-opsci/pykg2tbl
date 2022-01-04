# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import logging.config
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Defines the arguments to this script by using Python's [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = argparse.ArgumentParser(description='Py Project to extra table data from knowwledge-graphs using sparql templates',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-l',
        '--logconf',
        type=str,
        action='store',
        help='location of the logging config (yml) to use',
    )

    # TODO define your own command line arguments
    parser.add_argument(
        '-o',
        '--option',
        type=str,
        action='store',
        help='Some Option',
        default='TheOptionValue',
    )
    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    import yaml   # conditional dependency -- we only need this (for now) when logconf needs to be read
    with open(args.logconf, 'r') as yml_logconf:
        logging.config.dictConfig(yaml.load(yml_logconf, Loader=yaml.SafeLoader))
    log.info(f"Logging enabled according to config in {args.logconf}")
    
    
class QueryResult():
    def __init__(self, data: dict):
        self._data = data
    # allow conversion to table / list/ dict/ whatnot
    # be useful towards multiple ways of exporting (e.g. save as csv)

## create abstract class for making a contract by design for devs ##
class KG2TContext(ABC): 
    @abstractmethod
    def query(self) -> QueryResult:
        pass
    
## create classes for making the kg context and query factory graph
class KG2FileDumpContext(KG2TContext):
    def __init__(self, files):
        super().__init__()
        self.graph = None 
        # todo sintantiate graph and load it with all files
        for f in files:
            pass
        
    def query(self, sparql: str) -> QueryResult:
        reslist = self.graph.query(sparql)
        return QueryResult(KG2FileDumpContext.reslist_to_dict(reslist))
        
    @staticmethod
    def reslist_to_dict(reslist):
        return dict(reslist)
    
 
## create class for KG based on endpoint
class KG2EndpointContext(KG2TContext):
    def __init__(self, url):
        super().__init__()
        self.endpoint = None # check how to make an endpoint
    
    def query(self, sparql: str) -> QueryResult:
        resdict = self.endpoint.query(sparql)
        return QueryResult(resdict)

def main():
    """
    The main entry point to this module.

    """
    args = get_arg_parser().parse_args()
    enable_logging(args)

    log.info("The args passed to %s are: %s." % (sys.argv[0], args))
    log.debug("Some Logging")


if __name__ == '__main__':
    main()
