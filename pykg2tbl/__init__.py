""" pykg2tbl

.. module:: pykg2tbl
    :synopsis: Py Project to extra table data from knowwledge-graphs using sparql templates

.. moduleauthor:: Marc Portier <marc.portier@gmail.com>

"""

from .extractor import MyModel
import logging

__all__ = ['MyModel']

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
