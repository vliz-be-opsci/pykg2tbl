# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import sys
from pathlib import Path

import validators
from pyrdfj2 import J2RDFSyntaxBuilder

from pykg2tbl import DEFAULT_TEMPLATES_FOLDER
from pykg2tbl.exceptions import MultipleSourceTypes
from pykg2tbl.kg2tbl import KGSource

log = logging.getLogger(__name__)


def get_arg_parser():
    """
    Defines the arguments to this script by using Python's
        [argparse](https://docs.python.org/3/library/argparse.html)
    """

    parser = argparse.ArgumentParser(
        description=(
            "Py Project to extra table data from "
            "knowledge-graphs using sparql templates"
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-l",
        "--logconf",
        type=str,
        action="store",
        help="location of the logging config (yml) to use",
    )

    parser.add_argument(
        "-s",
        "--source",
        type=str,
        nargs="+",
        metavar=["FILE", "URL"],
        action="store",
        help=(
            "input file to be turned into datagraph"
            " ,download-point of rdf-dump"
            "or sparql endpoint url"
        ),
    )

    parser.add_argument(
        "-f",
        "--output_format",
        choices=["csv", "tsv"],
        action="store",
        help="output file format",
        default="csv",
    )

    parser.add_argument(
        "-o",
        "--output_location",
        type=str,
        metavar="FILE",
        action="store",
        help="output file location relative to current directory path",
    )

    parser.add_argument(
        "-tf",
        "--template_folder",
        type=str,
        metavar="PATH",
        action="store",
        help="template folder location on disk",
    )

    parser.add_argument(
        "-t",
        "--template_name",
        type=str,
        action="store",
        help="template name located in the given template folder",
    )

    # TODO -- unclear how / why this approach?
    # where to add actual vars vs. subcommand to list vars?
    parser.add_argument(
        "-v",
        "--variables",
        nargs="*",
        action="append",
        help=(
            "List the variable names required for "
            "the given template seperated by |"
        ),
    )

    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    # conditional dependency -- we only need this (for now) when logconf needs
    #   to be read
    import yaml

    with open(args.logconf, "r") as yml_logconf:
        logging.config.dictConfig(
            yaml.load(yml_logconf, Loader=yaml.SafeLoader)
        )
    log.info(f"Logging enabled according to config in {args.logconf}")


def check_arguments(args: argparse.Namespace):
    # check if all necessary variables are given
    # TODO - why do this in __main__ ?? careful considertation --> either
    #   (1) remove,
    #   (2) move to service or
    #   (3) motivate and keep here in cli
    if args.source is None:
        raise argparse.ArgumentTypeError(
            "A fileinput or an endpoint must be supplied."
        )
    if args.template_name is None:
        raise argparse.ArgumentTypeError("A template name must be supplied.")
    if args.output_location is None:
        raise argparse.ArgumentTypeError(
            "An output location must be supplied."
        )

    # per variable check if they are valid for consumption
    # TODO why? why here and not in service?
    # TODO -- why?
    cwd = Path().absolute()
    if args.source is not None:
        try:
            KGSource.detect_source_type(*args.source)
        except MultipleSourceTypes:
            raise argparse.ArgumentTypeError(
                "Either a fileinput or an endpoint must be supplied, not both."
            )

        for src in args.source:
            if src.startswith("http"):
                if not validators.url(src):
                    raise argparse.ArgumentTypeError(
                        f"given endpoint is not a valid url => { src }"
                    )
            else:
                log.debug(str(cwd / src))
                if not (cwd / src).exists():
                    raise argparse.ArgumentTypeError(
                        f"file { src } does exist"
                    )

    # check if output path exists
    if args.output_location is not None:
        folder_path_file = (cwd / args.output_location).parent
        log.debug(str(folder_path_file))
        if not folder_path_file.exists():
            raise argparse.ArgumentTypeError(
                "Supplied output path does not exist on disk."
            )


def args_values_to_params(cli_variables: list) -> dict:
    """
    converts the arg.V list of:
        single_key=value | list_key[]=1,2 | dict_key.one=wan dict_key.two=toe
        into a dict context for the templating engine
        {  'single_key': 'value', 'list_key': ['1','2'],
            'dict_key': {'one': 'wan', 'two':'toe'}}

    :param argv_list: the list of -V arguments passed on the command line
    :type argv_list: list of str
    :returns: the params dict
    :rtype: dict
    """
    # TODO why?  from pyvocab search?  other technique available in argsparse?
    params = dict()
    log.debug(f"argv_list={cli_variables}")
    flat_list = [str(item) for sublist in cli_variables for item in sublist]
    for item in flat_list:
        log.debug(f"variable item to parse={item}")
        key, value = item.split("=")
        if "." in key:
            parts = key.split(".")
            key_msg = (
                f"dict-value key {key} does not match the single level "
                "support provided"
            )
            assert len(parts) == 2, key_msg
            key, subkey = parts[0], parts[1]
            subdict = params.get(key, dict())
            assert isinstance(subdict, dict), (
                "dict-value key '%s' is also used for none-dict value" % key
            )
            subdict[subkey] = value
            params[key] = subdict
            log.debug(f"parsed param subdict {key} --> {subdict}")
        elif key.endswith("[]"):
            key = key[:-2]
            sublist = params.get(key, list())
            assert isinstance(sublist, list), (
                "list-value key '%s' is also used for none-list value" % key
            )
            values = value.split(",")
            sublist.extend(values)
            params[key] = sublist
            log.debug(f"parsed param sublist {key} --> {sublist}")
        else:
            assert key not in params, (
                "single-value key '%s' should not be set twice" % key
            )
            params[key] = value
            log.debug(f"parsed simple param {key} --> {value}")
    return params


def variables_check(variables_template, variables_given):
    """
    checks the possible mismatch between variable names given vs. recognised
    in the template
    Note that any mismatch will only result in some extra logging as
    no conclusion can be made about validity or processing effect
    """
    given_names = set(variables_given)
    expected_names = variables_template
    log.debug(f"checking given {given_names} vs expected {expected_names}")
    ignored_names = given_names - expected_names
    optional_names = expected_names - given_names
    if len(ignored_names):
        log.info(f"given names {ignored_names} are not in the template")
    if len(ignored_names):
        log.warning(f"some template variables {optional_names} not given")
    return


def getdelimiter(args: argparse.Namespace):
    if args.output_format is not None:
        if args.output_format == "csv":
            return ","
        if args.output_format == "tsv":
            return "\t"
    else:
        return ","


def main(sysargs=None):
    """
    The main entry point to this module.

    """
    args = (
        get_arg_parser().parse_args(sysargs)
        if sysargs is not None and len(sysargs) > 0
        else get_arg_parser().parse_args()
    )
    enable_logging(args)
    log.info("The args passed to %s are: %s." % (sys.argv[0], args))
    check_arguments(args)
    log.debug("Performing service")
    params = {}
    template_folder = args.template_folder or DEFAULT_TEMPLATES_FOLDER
    template_service = J2RDFSyntaxBuilder(template_folder)
    vars_template = template_service.variables_in_template(args.template_name)
    if args.variables is not None and len(vars_template) > 0:
        params = args_values_to_params(args.variables)
        variables_check(
            variables_template=vars_template, variables_given=params
        )
    query = template_service.build_syntax(name=args.template_name, **params)
    print("performing query")
    log.debug("making exec service")
    data_source = KGSource.build(*args.source)
    log.debug(f"data_source build = {data_source}")
    qry_result = data_source.query(query)
    log.debug(f"query_result = {qry_result}")
    output_location = Path().absolute() / args.output_location
    qry_result.as_csv(str(output_location), getdelimiter(args))
    log.info(f"output written to {output_location}")
    print(f"new file saved on location : {output_location}")


if __name__ == "__main__":
    main(sys.argv[1:])
