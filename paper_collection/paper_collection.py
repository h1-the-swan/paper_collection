# -*- coding: utf-8 -*-

DESCRIPTION = """main module"""

import sys, os, time, json
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

import math

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
                 year=None,
                 venue=None,
                 authors=None,
                 node_rank=None):
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
        self.venue = venue
        self.node_rank = node_rank

        if (not self.display_title) and (self.title):
            self.display_title = self.title.title()

        if (not self.url) and (self.doi):
            self.url = "https://doi.org/{}".format(self.doi)

        self.load_authors(authors)

    def __repr__(self):
        return "Paper(paper_id: {})".format(self.paper_id)

    def to_dict(self):
        """return a dictionary of attributes suitable for JSON output
        :returns: dictionary

        """
        string_fields = [
            'dataset',
            'dataset_version',
            'title',
            'display_title',
            'doi',
            'url',
            'pub_date',
            'venue',
            'display_authors'
        ]

        num_fields = [
            'year',
            'node_rank'
        ]
        out = dict()
        for f in string_fields:
            attr = getattr(self, f)
            if not attr or (attr != attr):  # invalid value, probably NaN
                attr = None  # default for missing data
            out[f] = str(attr)
        for f in num_fields:
            attr = getattr(self, f)
            if (attr != attr):  # invalid value, probably NaN
                attr = None  # default for missing data
            out[f] = attr
        return out

    def load_authors(self, authors):
        """load author data

        :authors: list of dicts (with keys e.g., 'name', author_id')

        """
        self.authors = authors
        if not self.authors:
            self.authors = []
        self.display_authors = self.get_display_authors()

    def get_display_authors(self):
        """Get a string representation for the authors of this paper
        """
        if not self.authors:
            return None
        names = [a['name'] for a in self.authors]
        return ", ".join(names)

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

    def construct_graph(self):
        """Construct a graph with papers and citations
        """
        import networkx as nx
        G = nx.DiGraph()

        for paper in self.papers:
            # G.add_node(str(paper.paper_id),
            #            title=paper.title,
            #            display_title=paper.display_title,
            #            doi=paper.doi,
            #            url=paper.url,
            #            pub_date=str(paper.pub_date),
            #            year=str(paper.year),
            #            node_rank=paper.node_rank)
            G.add_node(str(paper.paper_id), **paper.to_dict())

        for citing, cited in self.citations:
            G.add_edge(str(citing), str(cited))

        self.G = G

        return G

    def write_graph(self, outfpath):
        """Write graph to json

        outfpath: output path (json)

        """
        from networkx.readwrite import json_graph
        if self.G is None:
            self.construct_graph()
        outfpath = Path(outfpath)
        logger.debug("writing to {}".format(outfpath))
        json_data = json_graph.node_link_data(self.G)
        with outfpath.open('w') as outf:
            json.dump(json_data, outf)

