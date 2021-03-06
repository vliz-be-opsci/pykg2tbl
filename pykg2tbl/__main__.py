# -*- coding: utf-8 -*-
import argparse
import sys
import os
import logging
import logging.config
import validators
from pykg2tbl import KG2TblService, KGFileSource, KG2EndpointSource, J2SparqlBuilder

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
        '-i',
        '--input',
        type=str,
        nargs='+',
        metavar="FILE",
        action='store',
        help='input file to be turned into datagraph or endpoint of rdf-database'
    )

    parser.add_argument(
        '-e',
        '--endpoint',
        type=str,
        metavar="URL",
        action='store',
        help='sparql endpoint url'
    )

    parser.add_argument(
        '-f',
        '--output_format',
        choices=['csv','tsv'],
        action='store',
        help='output file format',
        default='csv'
    )

    parser.add_argument(
        '-o',
        '--output_location',
        type=str,
        metavar="FILE",
        action='store',
        help='output file location relative to current directory path',
    )

    parser.add_argument(
        '-tf',
        '--template_folder',
        type=str,
        action='store',
        help='template folder location on disk',
    )

    parser.add_argument(
        '-t',
        '--template_name',
        type=str,
        action='store',
        help='template name located in the given template folder',
    )

    parser.add_argument(
        '-v',
        '--variables',
        nargs='*',
        action='store',
        help='List the variable names required for the given template seperated by |'
        )

    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    import yaml   # conditional dependency -- we only need this (for now) when logconf needs to be read
    with open(args.logconf, 'r') as yml_logconf:
        logging.config.dictConfig(yaml.load(yml_logconf, Loader=yaml.SafeLoader))
    log.info(f"Logging enabled according to config in {args.logconf}")

def performe_service(args: argparse.Namespace):
    #check if all necessary variables are given
    if args.input is not None and args.endpoint is not None:
        raise argparse.ArgumentTypeError('Either a fileinput or an endpoint must be supplied, not both.')
    if args.input is None and args.endpoint is None:
        raise argparse.ArgumentTypeError('A fileinput or an endpoint must be supplied.')
    if args.template_folder is None:
        raise argparse.ArgumentTypeError('A template folder must be supplied.')
    if args.template_name is None:
        raise argparse.ArgumentTypeError('A template name must be supplied.')
    if args.output_location is None:
        raise argparse.ArgumentTypeError('An output location must be supplied.')

    #per variable check if they are valid for consumption
    current_folder = os.getcwd()
    if args.input is not None:
        for i in args.input:
            log.debug(os.path.join(current_folder,i))
            if os.path.exists(os.path.join(current_folder,i)) == False:
                raise argparse.ArgumentTypeError(f'file {i} does exist')

    if os.path.exists(os.path.join(current_folder,args.template_folder,args.template_name)) == False:
        i = os.path.join(current_folder,args.template_folder,args.template_name)
        raise argparse.ArgumentTypeError(f'given folder or template name doesnt exist => {i} ')

    if args.endpoint is not None:
        if validators.url(args.endpoint) !=True:
            raise argparse.ArgumentTypeError(f'given endpoint is not a valid url => {args.endpoint} ')

    #check if output path exists
    if args.output_location is not None:
        folder_path_file = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(),args.output_location)))
        log.debug(folder_path_file)
        if os.path.exists(folder_path_file) == False:
            raise argparse.ArgumentTypeError('Supplied output path does not exist on disk.')


def args_values_to_params(argv_list: list) -> dict:
    """
    converts the arg.V list of single_key=value | list_key[]=1,2 | dict_key.one=wan dict_key.two=toe
    into a dict context for the templating engine
    {  'single_key': 'value', 'list_key': ['1','2'], 'dict_key': {'one': 'wan', 'two':'toe'}}

    :param argv_list: the list of -V arguments passed on the command line
    :type argv_list: list of str
    :returns: the params dict
    :rtype: dict
    """
    params = dict()
    log.debug(argv_list)
    for lin in argv_list:
        log.debug(lin)
        line = str(lin)
        key, value = line.split('=')
        if '.' in key:
            parts = key.split('.')
            assert len(parts) == 2, "dict-value key '%s' does not match the single level support provided" % key
            key, subkey = parts[0], parts[1]
            subdict = params.get(key, dict())
            assert isinstance(subdict, dict), "dict-value key '%s' is also used for none-dict value" % key
            subdict[subkey] = value
            params[key] = subdict
        elif key.endswith('[]'):
            key = key[:-2]
            sublist = params.get(key, list())
            assert isinstance(sublist, list), "list-value key '%s' is also used for none-list value" % key
            values = value.split(',')
            sublist.extend(values)
            params[key] = sublist
        else:
            assert key not in params, "single-value key '%s' should not be set twice" % key
            params[key] = value
    return params

def variables_check(variables_template, variables_given):
    for variable in variables_template:
        intemplate = False
        for var in variables_given.keys():
            if var  == variable:
                intemplate = True
        if intemplate == False:
            raise argparse.ArgumentTypeError(f'variable {variable} is not present in template')

    for variable in variables_given.keys():
        intemplate = False
        log.debug(variable)
        for var in variables_template:
            if var  == variable:
                intemplate = True
        if intemplate == False:
            raise argparse.ArgumentTypeError(f'variable {variable} is not present in template')

def makesource(args: argparse.Namespace):
    if args.input is not None:
        return KGFileSource(*args.input)
    if args.endpoint is not None:
        return KG2EndpointSource(args.endpoint)

def getdelimiter(args: argparse.Namespace):
    if args.output_format is not None:
        if args.output_format == "csv":
            return ','
        if args.output_format == "tsv":
            return '\t'
    else:
        return ','

def main(sysargs = None):
    """
    The main entry point to this module.

    """
    print('sysargs=', sysargs)
    args = get_arg_parser().parse_args(sysargs) if sysargs is not None and len(sysargs) > 0 else get_arg_parser().parse_args()
    enable_logging(args)
    log.info("The args passed to %s are: %s." % (sys.argv[0], args))
    log.debug("Performing service")
    performe_service(args)
    params = {}
    template_service = J2SparqlBuilder(os.path.join(os.getcwd(),args.template_folder))
    vars_template = template_service.variables_in_query(args.template_name)
    if args.variables is not None and len(vars_template) > 0:
        params = args_values_to_params(args.variables)
        variables_check(variables_template=vars_template, variables_given=params)
    querry = template_service.build_sparql_query(name=args.template_name, variables= params)
    print(f'Making KGSource')
    source = makesource(args)
    print(f'performing query')
    log.debug("making exec service")
    executive_service = KG2TblService(source)
    log.debug("performing service query")
    executive_service.exec(querry,os.path.join(os.getcwd(),args.output_location),getdelimiter(args))
    log.info("done with query")
    print(f'new file saved on location : {os.path.join(os.getcwd(),args.output_location)}')

if __name__ == '__main__':
    main(sys.argv[1:])
