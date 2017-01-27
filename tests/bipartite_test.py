#
# bipartite_test.py
#
# Copyright (c) 2016-2017 Junpei Kawamoto
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
# along with rgmining-ria. If not, see <http://www.gnu.org/licenses/>.
#
"""Unit test for ria.bipartite module.
"""
# pylint: disable=protected-access
from __future__ import division
from collections import defaultdict
import numpy as np
import random
import unittest
from ria import bipartite
from review import AverageReview, AverageSummary


class TestReviewer(unittest.TestCase):
    """Test case for Reviewer class.


    This test case uses the following sample graph.

    .. graphviz::

       digraph bipartite {
          graph [rankdir = LR];
          "reviewer-0";
          "reviewer-1";
          "product-0";
          "product-1";
          "product-2";
          "reviewer-0" -> "product-0" [label="0.1"];
          "reviewer-0" -> "product-1" [label="0.1"];
          "reviewer-0" -> "product-2" [label="0.1"];
          "reviewer-1" -> "product-1" [label="0.8"];
          "reviewer-1" -> "product-2" [label="0.8"];
       }

    """

    def setUp(self):
        """Set up for tests.
        """
        self.graph = bipartite.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        self.reviews = defaultdict(dict)
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.reviews[i][j] = self.graph.add_review(
                    r, self.products[j], 0.1 if i == 0 else 0.8)

    def test_anomalous_score(self):
        """Test anomalous_score property.
        """
        # At first, anomalous scores are initialized 1 / |reviewers|.
        for r in self.reviewers:
            self.assertAlmostEqual(r.anomalous_score, 1 / len(self.reviewers))

        # After setting some value, it will be used.
        for r in self.reviewers:
            new = random.random()
            r.anomalous_score = new
            self.assertAlmostEqual(r.anomalous_score, new)

    def test_update_anomalous_score(self):
        """Test updating anomalous scores.

        A new anomalous score is the weighted average of differences
        between current summary and reviews. The weights come from credibilities.

        Therefore, the new anomalous score is defined as

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
        """
        res = 0
        weight = 0
        for i, r in enumerate(self.reviews[0].values()):
            p = self.products[i]
            c = self.reviewers[0]._credibility(p)
            res += p.summary.difference(r) * c
            weight += c

        expected = res / weight
        old = self.reviewers[0].anomalous_score
        self.assertAlmostEqual(self.reviewers[0].update_anomalous_score(),
                               abs(old - expected))
        self.assertAlmostEqual(self.reviewers[0].anomalous_score, expected)


class TestProduct(unittest.TestCase):
    """Test case for Product class.


    This test case uses the following sample graph.

    .. graphviz::

       digraph bipartite {
          graph [rankdir = LR];
          "reviewer-0";
          "reviewer-1";
          "product-0";
          "product-1";
          "product-2";
          "reviewer-0" -> "product-0" [label="0.1"];
          "reviewer-0" -> "product-1" [label="0.1"];
          "reviewer-0" -> "product-2" [label="0.1"];
          "reviewer-1" -> "product-1" [label="0.8"];
          "reviewer-1" -> "product-2" [label="0.8"];
       }

    """

    def setUp(self):
        """Set up for tests.
        """
        self.graph = bipartite.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        self.reviews = defaultdict(dict)
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.reviews[i][j] = self.graph.add_review(
                    r, self.products[j], 0.1 if i == 0 else 0.8)

    def test_summary(self):
        """Test summary property.
        """
        # Initial summary is an average of given review scores
        self.assertAlmostEqual(self.products[0].summary.score, 0.1)
        self.assertAlmostEqual(
            self.products[1].summary.score, np.mean([0.1, 0.8]))
        self.assertAlmostEqual(
            self.products[2].summary.score, np.mean([0.1, 0.8]))

        # After setting some value, it will be used.
        for p in self.products:
            new = random.random()
            p.summary = new
            self.assertAlmostEqual(p.summary.score, new)

    def test_update_summary(self):
        """Test updating summary.

        The updated summary of a product :math:`p` is a weighted average of
        reviews. The weights are computed by a given weight function.

        .. math::

           {\\rm summary}(p) = \\frac{
              \\sum_{r \\in R} \\mbox{weight}(r) \\times \\mbox{review}(r, p)
           }{
              \\sum_{r \\in R} \\mbox{weight}(r)
           },

        where :math:`R` is a set of reviewers reviewing this product,
        review(:math:`r, p`) and weight(:math:`r`) are
        the review and weight of the reviewer :math:`r`, respectively.
        """
        w = self.graph._weight_generator(self.reviewers)
        res = 0
        weights = 0
        for i, r in enumerate(self.reviewers):
            res += self.reviews[i][2].score * w(r.anomalous_score)
            weights += w(r.anomalous_score)
        old = self.products[2].summary.score
        expected = res / weights
        self.products[2].update_summary(w)
        self.assertAlmostEqual(
            self.products[2].update_summary(w), abs(old - expected))
        self.assertAlmostEqual(self.products[2].summary.score, expected)


class TestBipartiteGraphConstruction(unittest.TestCase):
    """Test case for constructing a bipartite graph.
    """

    def setUp(self):
        """Set up for tests.
        """
        self.graph = bipartite.BipartiteGraph()

    def test_constructor(self):
        """Test creating a graph object.
        """
        self.assertEqual(self.graph._summary_cls, AverageSummary)
        self.assertEqual(self.graph._review_cls, AverageReview)
        self.assertEqual(self.graph._reviewer_cls, bipartite.Reviewer)
        self.assertEqual(self.graph._product_cls, bipartite.Product)

    def test_new_reviewer(self):
        """Test for creating reviewers.
        """
        name1 = "test-reviewer1"
        r1 = self.graph.new_reviewer(name1, 0.1)
        self.assertEqual(r1.name, name1)
        self.assertIsInstance(r1, self.graph._reviewer_cls)
        self.assertAlmostEqual(r1.anomalous_score, 0.1)

        name2 = "test-reviewer2"
        r2 = self.graph.new_reviewer(name2)
        self.assertEqual(r2.name, name2)
        self.assertAlmostEqual(r2.anomalous_score, 0.5)

        self.assertEqual(len(self.graph.reviewers), 2)
        self.assertIn(r1, self.graph.reviewers)
        self.assertIn(r2, self.graph.reviewers)

    def test_new_product(self):
        """Test for creating products.
        """
        name = "test-product"
        p = self.graph.new_product(name)
        self.assertEqual(p.name, name)
        self.assertIsInstance(p, self.graph._product_cls)
        self.assertEqual(len(self.graph.products), 1)
        self.assertIn(p, self.graph.products)

    def test_add_review(self):
        """Test for adding reviews.

        This test uses the following sample graph.

        .. graphviz::

           digraph bipartite {
              graph [rankdir = LR];
              "reviewer-0";
              "reviewer-1";
              "product-0";
              "product-1";
              "product-2";
              "reviewer-0" -> "product-0" [label="0.1"];
              "reviewer-0" -> "product-1" [label="0.1"];
              "reviewer-0" -> "product-2" [label="0.1"];
              "reviewer-1" -> "product-1" [label="0.8"];
              "reviewer-1" -> "product-2" [label="0.8"];
           }

        """
        reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        for i, r in enumerate(reviewers):
            for j in range(i, len(products)):
                rating = 0.1 if i == 0 else 0.8
                review = self.graph.add_review(r, products[j], rating)
                self.assertEqual(review.score, rating)

        with self.assertRaises(TypeError):
            self.graph.add_review(reviewers[0], reviewers[0], 0.1)
        with self.assertRaises(TypeError):
            self.graph.add_review(products[0], products[0], 0.1)


class TestRetrievNodes(unittest.TestCase):
    """Test case for retrieving nodes.

    This test case uses the following sample graph.

    .. graphviz::

       digraph bipartite {
          graph [rankdir = LR];
          "reviewer-0";
          "reviewer-1";
          "product-0";
          "product-1";
          "product-2";
          "reviewer-0" -> "product-0" [label="0.1"];
          "reviewer-0" -> "product-1" [label="0.1"];
          "reviewer-0" -> "product-2" [label="0.1"];
          "reviewer-1" -> "product-1" [label="0.8"];
          "reviewer-1" -> "product-2" [label="0.8"];
       }

    """

    def setUp(self):
        """Set up for tests.
        """
        self.graph = bipartite.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        self.reviews = defaultdict(dict)
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.reviews[i][j] = self.graph.add_review(
                    r, self.products[j], 0.1 if i == 0 else 0.8)

    def test_retrieve_reviewers(self):
        """Test retriving reviewers from a product.
        """
        self.assertEqual(
            set(self.graph.retrieve_reviewers(self.products[0])),
            set(self.reviewers[:1]))
        self.assertEqual(
            set(self.graph.retrieve_reviewers(self.products[1])),
            set(self.reviewers))
        self.assertEqual(
            set(self.graph.retrieve_reviewers(self.products[2])),
            set(self.reviewers))
        with self.assertRaises(TypeError):
            self.graph.retrieve_reviewers(self.reviewers[0])

    def test_retrieve_products(self):
        """Test retriving proucts from a reviewer

        Sample graph used in this test is as same as
        :meth:`test_retrieve_reviewers`.
        """
        self.assertEqual(
            set(self.graph.retrieve_products(self.reviewers[0])),
            set(self.products))
        self.assertEqual(
            set(self.graph.retrieve_products(self.reviewers[1])),
            set(self.products[1:]))
        with self.assertRaises(TypeError):
            self.graph.retrieve_products(self.products[0])

    def test_retrieve_review(self):
        """Test retriving reviews from a reviewer and a product.

        Sample graph used in this test is as same as
        :meth:`test_retrieve_reviewers`.
        """
        for i, r in enumerate(self.reviewers):
            for j, p in enumerate(self.products):
                if j in self.reviews[i]:
                    self.assertEqual(
                        self.graph.retrieve_review(r, p), self.reviews[i][j])
        with self.assertRaises(TypeError):
            self.graph.retrieve_review(self.reviewers[0], self.reviewers[1])
        with self.assertRaises(TypeError):
            self.graph.retrieve_review(self.products[0], self.products[1])


class TestWeightGenerator(unittest.TestCase):
    """Test case for _weight_generator function.
    """

    def setUp(self):
        """Set up a bipartite graph.
        """
        self.alpha = 2
        self.graph = bipartite.BipartiteGraph(alpha=self.alpha)

    def test_with_same_anomalous_scores(self):
        """Test with reviewers who have same anomalous scores.
        """
        reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(10)
        ]
        w = self.graph._weight_generator(reviewers)

        for r in reviewers:
            self.assertEqual(w(r.anomalous_score), 1)

    def test_with_random_reviewers(self):
        """Test with random reviewers.
        """
        reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i), random.random())
            for i in range(10)
        ]
        w = self.graph._weight_generator(reviewers)

        scores = [r.anomalous_score for r in reviewers]
        mu = np.average(scores)
        sigma = np.std(scores)

        for r in reviewers:
            exp = np.exp(self.alpha * (r.anomalous_score - mu) / sigma)
            self.assertAlmostEqual(w(r.anomalous_score), 1. / (1. + exp))


if __name__ == "__main__":
    unittest.main()
