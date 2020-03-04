# -*- coding: utf-8 -*-

DESCRIPTION = """main module"""

import sys, os, time
from pathlib import Path
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
root_logger = logging.getLogger()
logger = root_logger.getChild(__name__)

class Paper:

    """Docstring for Paper. """

    def __init__(self):
        """TODO: to be defined1. """

class PaperCollection:

    """Docstring for PaperCollection. """

    def __init__(self):
        """TODO: to be defined1. """

        
        

# def main(args):
#     pass
#
# if __name__ == "__main__":
#     total_start = timer()
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s", datefmt="%H:%M:%S"))
#     root_logger.addHandler(handler)
#     root_logger.setLevel(logging.INFO)
#     logger.info(" ".join(sys.argv))
#     logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
#     import argparse
#     parser = argparse.ArgumentParser(description=DESCRIPTION)
#     parser.add_argument("--debug", action='store_true', help="output debugging info")
#     global args
#     args = parser.parse_args()
#     if args.debug:
#         root_logger.setLevel(logging.DEBUG)
#         logger.debug('debug mode is on')
#     main(args)
#     total_end = timer()
#     logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
