# -*- coding: utf-8 -*-

DESCRIPTION = """get data from MAG 2019 dataset using spark"""

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

from config import Config
from paper_collection.data_getter import DataGetterMAG2019

def get_paper_ids(fpath):
    fpath = Path(fpath)
    paper_ids = fpath.read_text().split('\n')
    return paper_ids

def main(args):
    logging.getLogger('py4j').setLevel(logging.WARNING)
    config = Config()
    spark = config.spark
    paper_ids = get_paper_ids(args.paper_ids)
    try:
        datagetter = DataGetterMAG2019(config, paper_ids, description="MSRC seed papers", method='spark',
                                        papers=args.papers,
                                        citations=args.citations,
                                        paper_authors=args.paper_authors)
        coll = datagetter.collection
        logger.debug("constructing graph")
        G = coll.construct_graph()
        logger.debug("writing graph with {} nodes and {} edges to {}".format(G.number_of_nodes(), G.number_of_edges(), args.output))
        coll.write_graph(args.output)

    finally:
        config.teardown()

if __name__ == "__main__":
    total_start = timer()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s", datefmt="%H:%M:%S"))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("paper_ids", help="path to file with newline separated paper ids")
    parser.add_argument("papers", help="path to MAG papers parquet data")
    parser.add_argument("citations", help="path to MAG citations parquet data")
    parser.add_argument("paper_authors", help="path to MAG paper_authors parquet data")
    parser.add_argument("output", help="path to output file (JSON)")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        root_logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
