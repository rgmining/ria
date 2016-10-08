#
# bipartite_sum.py
#
# Copyright (c) 2016 Junpei Kawamoto
#
# This file is part of rgmining-ria.
#
# rgmining-ria is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rgmining-ria is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
"""Provide a bipartite graph which implements OneSum algorithm.

The bipartite graph implemented in this module uses normalized summations for
updated anomalous scores.
"""
from __future__ import absolute_import
from ria import bipartite


class Reviewer(bipartite.Reviewer):
    """Reviewer which uses normalized summations for updated anomalous scores.

    This reviewer will update its anomalous score by computing summation of
    partial anomalous scores instead of using a weighted average.
    """
    __slots__ = ()

    def update_anomalous_score(self):
        """Update anomalous score.

        New anomalous score is the summation of weighted differences
        between current summary and reviews. The weights come from credibilities.

        Therefore, the new anomalous score is defined as

        .. math::

            {\\rm anomalous}(r)
            = \\sum_{p \\in P} \\mbox{review}(p) \\times \\mbox{credibility}(p) - 0.5

        where :math:`P` is a set of products reviewed by this reviewer,
        review(:math:`p`) and credibility(:math:`p`) are
        review and credibility of product :math:`p`, respectively.

        Returns:
          absolute difference between old anomalous score and updated one.
        """
        old = self.anomalous_score

        products = self._graph.retrieve_products(self)
        self.anomalous_score = sum(
            p.summary.difference(
                self._graph.retrieve_review(self, p)) * self._credibility(p) - 0.5
            for p in products
        )

        return abs(self.anomalous_score - old)


class BipartiteGraph(bipartite.BipartiteGraph):
    """Bipartite Graph implementing OneSum algorithm.

    This graph employs a normalized summation of deviation times credibility
    as the undated anomalous scores for each reviewer.

    Constructor receives as same arguments as
    :class:`ria.bipartite.BipartiteGraph` but `reviewer` argument is ignored
    since this graph uses :class:`ria.bipartite_sum.Reviewer` instead.
    """

    def __init__(self, **kwargs):
        kwargs["reviewer"] = Reviewer
        super(BipartiteGraph, self).__init__(**kwargs)

    def update(self):
        """ Update reviewers' anomalous scores and products' summaries.

        The update consists of 2 steps;

        Step1 (updating summaries):
            Update summaries of products with anomalous scores of reviewers
            and weight function. The weight is calculated by the manner in
            :class:`ria.bipartite.BipartiteGraph`.

        Step2 (updating anomalous scores):
            Update its anomalous score of each reviewer by computing the summation
            of deviation times credibility.
            See :meth:`Reviewer.update_anomalous_score` for more details.
            After that those updated anomalous scores are normalized so that
            every value is in :math:`[0, 1]`.

        Returns:
          maximum absolute difference between old summary and new one, and
            old anomalous score and new one. This value is not normalized and
            thus it may be grater than actual normalized difference.
        """
        res = super(BipartiteGraph, self).update()

        max_v = None
        min_v = float("inf")
        for r in self.reviewers:
            max_v = max(max_v, r.anomalous_score)
            min_v = min(min_v, r.anomalous_score)

        width = max_v - min_v
        if width:
            for r in self.reviewers:
                r.anomalous_score = (r.anomalous_score - min_v) / width

        return res
