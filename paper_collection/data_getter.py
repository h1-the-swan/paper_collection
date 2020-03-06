# -*- coding: utf-8 -*-

DESCRIPTION = """Given a set of paper IDs, get a PaperCollection.

Provide common methods in a base class, and methods specific to 
certain data sets in individual classes for those data sets.

"""

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

from . import PaperCollection, Paper

class DataGetterBase:

    """Base class for getting data"""

    def __init__(self, config, paper_ids, description=None, method='spark'):
        self.config = config
        if method == 'spark':
            self.spark = config.spark
        self.paper_ids = paper_ids
        self.collection = PaperCollection(description=description)

    def load_paper(self):
        raise NotImplementedError


class DataGetterMAG2019(DataGetterBase):

    """DataGetter class for the MAG 2019 data set"""

    def __init__(self, config, paper_ids, description=None, method='spark', papers=None, citations=None, paper_authors=None):
        """TODO: to be defined1. """
        super().__init__(config, paper_ids, description, method)

        self.dataset = 'mag'
        self.dataset_version = 'mag-2019-11-22'
        self.paper_id_colname = 'PaperId'
        self.author_id_colname = 'AuthorId'
        self.citing_paper_colname = self.paper_id_colname
        self.cited_paper_colname = 'PaperReferenceId'
        self.author_seq_colname = 'AuthorSequenceNumber'
        self.author_name_colname = 'OriginalAuthor'
        self.doi_colname = 'Doi'
        self.pub_date_colname = 'Date'
        self.title_colname = 'Title'

        if method == 'spark':
            self.sdf_papers = self.spark.read.parquet(str(papers))
            self.sdf_citations = self.spark.read.parquet(str(citations))
            self.sdf_paper_authors = self.spark.read.parquet(str(paper_authors))

            self.df_papers = self.get_papers_spark()
            self.df_citations = self.get_citations_spark()
            self.df_paper_authors = self.get_paper_authors_spark()

            self.author_data = self.get_authors_by_paper(self.df_paper_authors)
            self.load_collection()

    def get_papers_spark(self):
        """TODO: Docstring for get_papers_spark.
        :returns: TODO

        """
        logger.debug('getting papers from spark')
        r = self.sdf_papers.filter(self.sdf_papers[self.paper_id_colname].isin(self.paper_ids))
        return r.toPandas()

    def get_citations_spark(self):
        """TODO: Docstring for get_citations_spark.
        :returns: TODO

        """
        logger.debug('getting citations from spark')
        r = self.sdf_citations.filter(self.sdf_citations[self.citing_paper_colname].isin(self.paper_ids))
        r = r.filter(r[self.cited_paper_colname].isin(self.paper_ids))
        return r.toPandas()

    def get_paper_authors_spark(self):
        """TODO: Docstring for get_paper_authors_spark.
        :returns: TODO

        """
        logger.debug('getting paper_authors from spark')
        r = self.sdf_paper_authors.filter(self.sdf_paper_authors[self.paper_id_colname].isin(self.paper_ids))
        return r.toPandas()

    def get_authors_by_paper(self, df_authors):
        """Get a dictionary mapping paper_id to author data

        """
        author_data = {}
        for paper_id, group in df_authors.groupby(self.paper_id_colname):
            group = group.sort_values(self.author_seq_colname)
            this_authors = []
            for _, row in group.iterrows():
                this_authors.append({'name': row[self.author_name_colname], 'author_id': row[self.author_id_colname]})
            author_data[paper_id] = this_authors
        return author_data

    def load_paper(self, prow, author_data=None):
        paper_id = prow[self.paper_id_colname]
        p = Paper(dataset=self.dataset,
                dataset_version=self.dataset_version,
                paper_id=paper_id,
                title=prow.PaperTitle,
                display_title=prow.OriginalTitle,
                doi=prow[self.doi_colname],
                pub_date=prow[self.pub_date_colname],
                year=prow.Year,
                venue=prow.OriginalVenue,
                node_rank=prow.flow)
        if author_data is not None:
            p.load_authors(author_data[paper_id])
        return p

    def load_collection(self):
        """TODO: Docstring for load_collection.
        :returns: TODO

        """
        logger.debug("loading collection")
        for _, prow in self.df_papers.iterrows():
            p = self.load_paper(prow, author_data=self.author_data)
            self.collection.papers.append(p)
        for _, row in self.df_citations.iterrows():
            self.collection.citations.append((row[self.citing_paper_colname], row[self.cited_paper_colname]))

        

def main(args):
    pass

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
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        root_logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
