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

    """A single article, from a single data set."""

    def __init__(self,
                 dataset=None,
                 dataset_version=None,
                 paper_id=None,
                 title=None,
                 display_title=None,
                 doi=None,
                 url=None,
                 pub_date=None,
                 year=None):
        """TODO: to be defined1. """

        self.dataset = dataset
        self.dataset_version = dataset_version
        self.paper_id = paper_id
        self.title = title
        self.display_title = display_title
        self.doi = doi
        self.url = url
        self.pub_date = pub_date
        self.year = year

        self.authors = []
        self.venue = None

        if (not self.display_title) and (self.title):
            self.display_title = self.title.title()

        if (not self.url) and (self.doi):
            self.url = "https://doi.org/{}".format(self.doi)

    def __repr__(self):
        return "Paper(paper_id: {})".format(self.paper_id)

class PaperCollection:

    """A collection of Papers"""

    def __init__(self, 
                 papers=None, 
                 description=None,
                 citations=None):
        """
        papers: list of Paper objects
        description: (str) description of this collection
        citations: list of tuples (citing_id, cited_id)
        """

        self.papers = papers
        if self.papers is None:
            self.papers = list()
        self.description = description
        self.citations = citations
        if self.citations is None:
            self.citations = list()

    def __repr__(self):
        return "PaperCollection({})".format(self.description)

    def __len__(self):
        return len(self.papers)

        
        

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
