from pykg2tbl import SparqlBuilder
import os
from jinja2 import Environment, FileSystemLoader, meta
import logging

log=logging.getLogger(__name__)
  
class J2SparqlBuilder(SparqlBuilder):
    """
    Generic class to perform templated SPARQL searches versus a given SPARQL endpoint

    :param endpoint: sparql endpoint URL of the service to call upon
    :param templates_folder: location of the folder containing the sparql templates
    """
    def __init__(self, templates_folder: str = None):
        if templates_folder is None:
            templates_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
        self._templates_env = Environment(loader=FileSystemLoader(templates_folder))

    def _get_qry_template(self, name: str):
        """Gets the template"""
        return self._templates_env.get_template(name)

    def variables_in_query(self, name:str) -> set:
        """
        The set of variables to make this template work
        
        :param name: name of the template to inspect
        :returns: set of variable-names
        :rtype: set of str
        """
        template_name = name
        templates_env = self._templates_env
        log.debug(f"name template: {template_name}")
        template_source = templates_env.loader.get_source(templates_env, template_name)
        log.debug(f"template source = {template_source}")
        ast = self._templates_env.parse(template_source)
        return meta.find_undeclared_variables(ast)

    def build_sparql_query(self, name: str, **variables) -> str:
        """
        Fills a named template sparql 
        
        :param name: of the template
        :param **variables: named context parameters to apply to the template
        """
        log.debug(f"building sparql query '{name}' with variables={variables}")
        qry = self._get_qry_template(name).render(variables)
        return qry
