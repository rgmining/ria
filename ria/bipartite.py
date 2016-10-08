#
# bipartite.py
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
"""Provide classes for review mining algorithms based on a bipartite model.

Especially, the following three classes are the core of the algorithm.

:class:`BipartiteGraph`
    Representing the bipartite graph model.
    It provides basic methods to handle the graph and update method to compute
    new anomalous scores for reviewers and new summaries for products.
:class:`Reviewer`
    Representing a reviewer.
    It is modeled as a node in the bipartite graph.
    Each reviewer has an anomalous score.
:class:`Product`
    Representing a product.
    It is also modeled as a node in the bipartite graph.
    Each product has a summary score of the given review scores.

The bipartite model we use has two kinds of nodes; Reviewer and Product.
A reviewer and a product are tied when the reviewer has reviewed the product.
Each edge is a directed and has a label representing a score the reviewer has
given to the product.

In the bipartite graph model, both reviewers and products have scores.
Each reviewer has an anomalous score which represent how anomalous the reviewer is.
Each product has a summary of reviews the product has received.

Here is a sample of the bipartite graph.

.. graphviz::

  digraph bipartite {
    graph [label="Bipartite graph model.", rankdir = LR];
    "r1" [label="Reviewer 1 \n (anomalous: 0.1)"];
    "r2" [label="Reviewer 2 \n (anomalous: 0.9)"];
    "r3" [label="Reviewer 3 \n (anomalous: 0.5)"];
    "p1" [label="Product 1 \n (summary: 0.3)"];
    "p2" [label="Product 2 \n (summary: 0.8)"];
    "r1" -> "p1" [label="0.3"];
    "r1" -> "p2" [label="0.9"];
    "r2" -> "p2" [label="0.1"];
    "r3" -> "p2" [label="0.5"];
  }

This module defines the bipartite graph itself (:class:`bipartite.BipartiteGraph`)
and two kinds of nodes, :class:`bipartite.Reviewer` and :class:`bipartite.Products`.

There are also many variations of the bipartite graph.
"""
from __future__ import absolute_import, division
import json
from logging import getLogger
import math

import numpy as np
import networkx as nx

from common import memoized
from ria.credibility import WeightedCredibility
from review import AverageSummary


LOGGER = getLogger(__name__)


class _Node(object):
    """Abstract node of the bipartite model.

    Args:
      graph: parent graph instance.
      name: name of the new node.

    If the name is not given, object.__str__() will be used.

    This class implements __eq__, __ne__, and __hash__ for convenience.

    Attributes:
      name: Name of this node.
    """
    __slots__ = ("_graph", "name", "_hash")

    def __init__(self, graph, name=None):
        """Construct a new node.

        Args:
          name: Specifying the name of this node.
                If not given, use strings returned from __str__ method.
        """
        if not isinstance(graph, BipartiteGraph):
            raise ValueError(
                "Given graph is not instance of Bipartite:", graph)

        self._graph = graph
        if name:
            self.name = name
        else:
            self.name = super(_Node, self).__str__()
        self._hash = None

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.name == other.name

    def __hash__(self):
        if not self._hash:
            self._hash = 13 * hash(type(self)) + 17 * hash(self.name)
        return self._hash

    def __str__(self):
        return self.name


class Reviewer(_Node):
    """A node class representing Reviewer.

    Args:
      graph: an instance of BipartiteGraph representing the parent graph.
      credibility: an instance of credibility.Credibility to be used to update
        scores.
      name: name of this node. (default: None)
      anomalous: initial anomalous score. (default: None)
    """
    __slots__ = ("_anomalous", "_credibility")

    def __init__(self, graph, credibility, name=None, anomalous=None):
        super(Reviewer, self).__init__(graph, name)
        self._anomalous = anomalous
        self._credibility = credibility

    @property
    def anomalous_score(self):
        """Anomalous score of this reviewer.

        Initial anomalous score is :math:`1 / |R|`
        where :math:`R` is a set of reviewers.
        """
        return self._anomalous if self._anomalous else 1. / len(self._graph.reviewers)

    @anomalous_score.setter
    def anomalous_score(self, v):
        """Set an anomalous score.

        Args:
          v: the new anomalous score.
        """
        self._anomalous = float(v)

    def update_anomalous_score(self):
        """Update anomalous score.

        New anomalous score is a weighted average of differences
        between current summary and reviews. The weights come from credibilities.

        Therefore, the new anomalous score of reviewer :math:`p` is as

        .. math::

           {\\rm anomalous}(r) = \\frac{
             \\sum_{p \\in P} {\\rm credibility}(p)|
                {\\rm review}(r, p)-{\\rm summary}(p)|
           }{
             \\sum_{p \\in P} {\\rm credibility}(p)
           }

        where :math:`P` is a set of products reviewed by reviewer :math:`p`,
        review(:math:`r`, :math:`p`) is the rating reviewer :math:`r` posted
        to product :math:`p`, summary(:math:`p`) and credibility(:math:`p`) are
        summary and credibility of product :math:`p`, respectively.

        Returns:
          absolute difference between old anomalous score and updated one.
        """
        products = self._graph.retrieve_products(self)
        diffs = [
            p.summary.difference(self._graph.retrieve_review(self, p))
            for p in products
        ]

        old = self.anomalous_score
        try:
            self.anomalous_score = np.average(
                diffs, weights=map(self._credibility, products))
        except ZeroDivisionError:
            self.anomalous_score = np.average(diffs)

        return abs(self.anomalous_score - old)


class Product(_Node):
    """A node class representing Product.

    Args:
      graph: An instance of BipartiteGraph representing the parent graph.
      name: Name of this node. (default: None)
      summary_cls: Specify summary type. (default: AverageSummary)
    """
    __slots__ = ("_summary", "_summary_cls")

    def __init__(self, graph, name=None, summary_cls=AverageSummary):
        super(Product, self).__init__(graph, name)

        self._summary = None
        self._summary_cls = summary_cls

    @property
    def summary(self):
        """Summary of reviews for this product.

        Initial summary is computed by

        .. math::

            \\frac{1}{|R|} \\sum_{r \\in R} \\mbox{review}(r),

        where :math:`\\mbox{review}(r)` means review from reviewer :math:`r`.
        """
        if self._summary:
            return self._summary

        reviewers = self._graph.retrieve_reviewers(self)
        return self._summary_cls(
            [self._graph.retrieve_review(r, self) for r in reviewers])

    @summary.setter
    def summary(self, v):
        """Set summary.

        Args:
          v: A new summary. It could be a single number or lists.
        """
        if hasattr(v, "__iter__"):
            self._summary = self._summary_cls(v)
        else:
            self._summary = self._summary_cls(float(v))

    def update_summary(self, w):
        """Update summary.

        The new summary is a weighted average of reviews i.e.

        .. math::

            \\frac{\\sum_{r \\in R} \\mbox{weight}(r) \\times \\mbox{review}(r)}
                {\\sum_{r \\in R} \\mbox{weight}(r)},

        where :math:`R` is a set of reviewers reviewing this product,
        :math:`\\mbox{review}(r)` and :math:`\\mbox{weight}(r)` are
        the review and weight of the reviewer :math:`r`, respectively.

        Args:
          w: A weight function.

        Returns:
          absolute difference between old summary and updated one.
        """
        old = self.summary.v # pylint: disable=no-member

        reviewers = self._graph.retrieve_reviewers(self)
        reviews = [self._graph.retrieve_review(
            r, self).score for r in reviewers]
        weights = [w(r.anomalous_score) for r in reviewers]
        if sum(weights) == 0:
            self.summary = np.mean(reviews)
        else:
            self.summary = np.average(reviews, weights=weights)
        return abs(self.summary.v - old) # pylint: disable=no-member


class BipartiteGraph(object):
    """Bipartite graph model for review data mining.

    Args:
      summary_type: specify summary type class, default value is AverageSummary.
      alpha: used to compute weight of anomalous scores, default value is 1.
      credibility: credibility class to be used in this graph.
        (Default: :class:`ria.credibility.WeightedCredibility`)
      reviewer: Class of reviewers.
      product: Class of products.

    Attributes:
      alpha: Parameter.
      graph: Graph object of networkx.
      reviewers: Collection of reviewers.
      products: Collection of products.
      credibility: Credibility object.
    """

    def __init__(
            self, summary=AverageSummary, alpha=1,
            credibility=WeightedCredibility, reviewer=Reviewer, product=Product):
        """Construct bipartite graph.

        Args:
          summary_type: specify summary type class, default value is AverageSummary.
          alpha: used to compute weight of anomalous scores, default value is 1.
          credibility: credibility class to be used in this graph.
                        (Default: WeightedCredibility)
          reviewer: Class of reviewers.
          product: Class of products.
        """
        self.alpha = alpha
        self.graph = nx.DiGraph()
        self.reviewers = []
        self.products = []

        self._summary_cls = summary
        self._review_cls = summary.review_class()

        self.credibility = credibility(self)
        self._reviewer_cls = reviewer
        self._product_cls = product

    def new_reviewer(self, name, anomalous=None):
        """Create a new reviewer.

        Args:
          name: name of the new reviewer.
          anomalous: initial anomalous score. (default: None)

        Returns:
          A new reviewer instance.
        """
        n = self._reviewer_cls(
            self, name=name, credibility=self.credibility, anomalous=anomalous)
        self.graph.add_node(n)
        self.reviewers.append(n)
        return n

    def new_product(self, name):
        """Create a new product.

        Args:
          name: name of the new product.

        Returns:
          A new product instance.
        """
        n = self._product_cls(self, name, summary_cls=self._summary_cls)
        self.graph.add_node(n)
        self.products.append(n)
        return n

    def add_review(self, reviewer, product, review, date=None):
        """Add a new review from a given reviewer to a given product.

        Args:
          reviewer: an instance of Reviewer.
          product: an instance of Product.
          review: a float value.
          date: date the review issued.

        Returns:
          the added new review object.

        Raises:
          TypeError: when given reviewer and product aren't instance of
            specified reviewer and product class when this graph is constructed.
        """
        if not isinstance(reviewer, self._reviewer_cls):
            raise TypeError(
                "Type of given reviewer isn't acceptable:", reviewer,
                ", expected:", self._reviewer_cls)
        elif not isinstance(product, self._product_cls):
            raise TypeError(
                "Type of given product isn't acceptable:", product,
                ", expected:", self._product_cls)
        _ = date
        r = self._review_cls(review)
        self.graph.add_edge(reviewer, product, review=r)
        return r

    @memoized
    def retrieve_products(self, reviewer):
        """Retrieve products reviewed by a given reviewer.

        Args:
          reviewer: A reviewer.

        Returns:
          A list of products which the reviewer reviews.

        Raises:
          TypeError: when given reviewer isn't instance of specified reviewer
            class when this graph is constructed.
        """
        if not isinstance(reviewer, self._reviewer_cls):
            raise TypeError(
                "Type of given reviewer isn't acceptable:", reviewer,
                ", expected:", self._reviewer_cls)
        return self.graph.successors(reviewer)

    @memoized
    def retrieve_reviewers(self, product):
        """Retrieve reviewers who reviewed a given product.

        Args:
          product: A product specifying reviewers.

        Returns:
          A list of reviewers who review the product.

        Raises:
          TypeError: when given product isn't instance of specified product
            class when this graph is constructed.
        """
        if not isinstance(product, self._product_cls):
            raise TypeError(
                "Type of given product isn't acceptable:", product,
                ", expected:", self._product_cls)
        return self.graph.predecessors(product)

    @memoized
    def retrieve_review(self, reviewer, product):
        """Retrieve review that the given reviewer put the given product.

        Args:
          reviewer: An instance of Reviewer.
          product: An instance of Product.

        Returns:
          A review object.

        Raises:
          TypeError: when given reviewer and product aren't instance of
            specified reviewer and product class when this graph is constructed.
          KeyError: When the reviewer does not review the product.
        """
        if not isinstance(reviewer, self._reviewer_cls):
            raise TypeError(
                "Type of given reviewer isn't acceptable:", reviewer,
                ", expected:", self._reviewer_cls)
        elif not isinstance(product, self._product_cls):
            raise TypeError(
                "Type of given product isn't acceptable:", product,
                ", expected:", self._product_cls)

        try:
            return self.graph[reviewer][product]["review"]
        except TypeError:
            raise KeyError(
                "{0} does not review {1}.".format(reviewer, product))

    def update(self):
        """Update reviewers' anomalous scores and products' summaries.

        Returns:
          maximum absolute difference between old summary and new one, and
          old anomalous score and new one.
        """
        w = self._weight_generator(self.reviewers)
        diff_p = max(p.update_summary(w) for p in self.products)
        diff_a = max(r.update_anomalous_score() for r in self.reviewers)
        return max(diff_p, diff_a)

    def _weight_generator(self, reviewers):
        """Compute a weight function for the given reviewers.

        Args:
          reviewers: a set of reviewers to compute weight function.

        Returns:
          a function computing a weight for a reviewer.
        """
        scores = [r.anomalous_score for r in reviewers]
        mu = np.average(scores)
        sigma = np.std(scores)

        if sigma:
            def w(v):
                """Compute a weight for the given reviewer.

                Args:
                  v: anomalous score of a reviewer.
                Returns:
                  weight of the given anomalous score.
                """
                try:
                    exp = math.exp(self.alpha * (v - mu) / sigma)
                    return 1. / (1. + exp)
                except OverflowError:
                    return 0.

            return w

        else:
            # Sigma = 0 means all reviews have same anomalous scores.
            # In this case, all reviews should be treated as same.
            return lambda v: 1.

    def dump_credibilities(self, output):
        """Dump credibilities of all products.

        Args:
          output: a writable object.
        """
        for p in self.products:
            json.dump({
                "product_id": p.name,
                "credibility": self.credibility(p)
            }, output)
            output.write("\n")

    def to_pydot(self):
        """Convert this graph to PyDot object.

        Returns:
          PyDot object representing this graph.
        """
        return nx.nx_pydot.to_pydot(self.graph)
