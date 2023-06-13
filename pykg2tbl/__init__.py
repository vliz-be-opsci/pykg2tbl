""" pykg2tbl

.. module:: pykg2tbl
    :synopsis: Py Project to extra table data from knowwledge-graphs using
        sparql templates

.. moduleauthor:: Marc Portier <marc.portier@gmail.com>

"""

import logging

from pykg2tbl.j2.jinja_sparql_builder import (
    J2SparqlBuilder as DefaultSparqlBuilder,
)
from pykg2tbl.kg2tbl import KGSource
from pykg2tbl.query import QueryResult

log = logging.getLogger(__name__)

__all__ = ["DefaultSparqlBuilder", "KGSource", "QueryResult"]
