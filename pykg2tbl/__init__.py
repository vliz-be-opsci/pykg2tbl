""" pykg2tbl

.. module:: pykg2tbl
    :synopsis: Py Project to extra table data from knowwledge-graphs using sparql templates

.. moduleauthor:: Marc Portier <marc.portier@gmail.com>

"""

from .service import *  #TODO define the classes that need to be added with __all__
from .j2.jinja_sparql_builder import * # ** 
import logging

#__all__ = ['MyModel'] #TODO add all imported classes from above

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
