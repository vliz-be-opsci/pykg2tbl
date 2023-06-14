""" pykg2tbl

.. module:: pykg2tbl
    :synopsis: Py Project to extra table data from knowwledge-graphs using
        sparql templates

.. moduleauthor:: Marc Portier <marc.portier@gmail.com>

"""

import logging
from pathlib import Path

from pyrdfj2 import J2RDFSyntaxBuilder as DefaultSparqlBuilder

from pykg2tbl.kg2tbl import KGSource
from pykg2tbl.query import QueryResult

log = logging.getLogger(__name__)
DEFAULT_TEMPLATES_FOLDER = (
    Path(__file__).parent.absolute() / "sparql_templates"
)

__all__ = ["DefaultSparqlBuilder", "KGSource", "QueryResult"]
