# -*- coding: utf-8 -*-

DESCRIPTION = """Output json graph with papers and references for test data"""

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

from paper_collection import PaperCollection, Paper

import pandas as pd
import numpy as np

def get_authors_by_paper(df_authors):
    """Get a dictionary mapping paper_id to author data

    """
    author_data = {}
    for paper_id, group in df_authors.groupby('PaperId'):
        group = group.sort_values('AuthorSequenceNumber')
        this_authors = []
        for _, row in group.iterrows():
            this_authors.append({'name': row.OriginalAuthor, 'author_id': row.AuthorId})
        author_data[paper_id] = this_authors
    return author_data

def load_paper(prow, author_data=None):
    paper_id = prow.PaperId
    p = Paper(dataset='mag',
            dataset_version='mag-2019-11-22',
            paper_id=paper_id,
            title=prow.PaperTitle,
            display_title=prow.OriginalTitle,
            doi=prow.Doi,
            pub_date=prow.Date,
            year=prow.Year,
            venue=prow.OriginalVenue,
            node_rank=prow.flow)
    if author_data is not None:
        p.load_authors(author_data[paper_id])
    return p

def main(args):
    df_papers = pd.read_csv(args.papers, sep='\t')
    df_papers.drop_duplicates(subset=['PaperId'], inplace=True)
    df_citations = pd.read_csv(args.citations, sep='\t')
    if args.authors:
        df_authors = pd.read_csv(args.authors, sep='\t')
        author_data = get_authors_by_paper(df_authors)
    else:
        author_data = None
    coll = PaperCollection(description="Paper Collection")
    for _, prow in df_papers.iterrows():
        p = load_paper(prow, author_data=author_data)
        coll.papers.append(p)
    for _, row in df_citations.iterrows():
        coll.citations.append((row.PaperId, row.PaperReferenceId))
    logger.debug("constructing graph")
    G = coll.construct_graph()
    logger.debug("writing graph with {} nodes and {} edges to {}".format(G.number_of_nodes(), G.number_of_edges(), args.output))
    coll.write_graph(args.output)

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
    parser.add_argument("papers", help="path to input file with papers (TSV)")
    parser.add_argument("citations", help="path to input file with citations (TSV)")
    parser.add_argument("output", help="path to output file (JSON)")
    parser.add_argument("--authors", help="path to input file with paper/author data (TSV)")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        root_logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
