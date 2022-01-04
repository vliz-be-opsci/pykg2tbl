# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import logging.config

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
