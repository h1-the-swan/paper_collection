#!/usr/bin/env python

"""Tests for `paper_collection` package."""


import unittest

from paper_collection import paper_collection

import pandas as pd
import numpy as np


class TestPaper_collection(unittest.TestCase):
    """Tests for `paper_collection` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.df_papers = pd.read_csv('tests/jw_papers_mag2019.tsv', sep='\t')
        self.df_papers.drop_duplicates(subset=['PaperId'], inplace=True)
        self.num_papers = len(self.df_papers)
        self.df_citations = pd.read_csv('tests/jw_citations_mag2019.tsv', sep='\t')
        self.num_citations = len(self.df_citations)
        self.df_authors = pd.read_csv('tests/jw_PaperAuthorAffiliations_mag2019.tsv', sep='\t')
        self.authors_by_paper = self.get_authors_by_paper(self.df_authors)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def get_authors_by_paper(self, df_authors):
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

    def load_paper(self, prow):
        paper_id = prow.PaperId
        authors = self.authors_by_paper[paper_id]
        return paper_collection.Paper(dataset='mag',
                                      dataset_version='mag-2019-11-22',
                                      paper_id=paper_id,
                                      title=prow.PaperTitle,
                                      display_title=prow.OriginalTitle,
                                      doi=prow.Doi,
                                      pub_date=prow.Date,
                                      year=prow.Year,
                                      venue=prow.OriginalVenue,
                                      authors=authors,
                                      node_rank=prow.flow)

    def test_000_single_paper(self):
        """Load a single paper"""
        prow = self.df_papers.iloc[0]
        p = self.load_paper(prow)
        assert p.display_title is not None
        assert len(p.display_title)

    def test_001_collection(self):
        """Load a collection"""
        coll = paper_collection.PaperCollection(description="Paper Collection")
        for _, prow in self.df_papers.iterrows():
            p = self.load_paper(prow)
            coll.papers.append(p)
        assert len(coll) == self.num_papers

    def test_002_graph(self):
        """Construct graph"""
        coll = paper_collection.PaperCollection(description="Paper Collection")
        for _, prow in self.df_papers.iterrows():
            p = self.load_paper(prow)
            coll.papers.append(p)
        for _, row in self.df_citations.iterrows():
            coll.citations.append((row.PaperId, row.PaperReferenceId))
        G = coll.construct_graph()
        assert G.number_of_nodes() == self.num_papers
        assert G.number_of_edges() == self.num_citations

