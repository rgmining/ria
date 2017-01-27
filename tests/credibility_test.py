#
# credibility_test.py
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
"""Unit tests for ria.credibility module.
"""
import numpy as np
import random
import unittest
from ria import credibility
from ria import bipartite


class TestUniformCredibility(unittest.TestCase):
    """Test case for UniformCredibility class.
    """

    def setUp(self):
        """Set up a bipartite graph.
        """
        self.graph = bipartite.BipartiteGraph()

    def test(self):
        """Test with some products.
        """
        c = credibility.UniformCredibility()
        for i in range(100):
            p = self.graph.new_product("product-{0}".format(i))
            self.assertEqual(c(p), 1)


class TestGraphBasedCredibility(unittest.TestCase):
    """Test case for GraphBasedCredibility.

    This test case uses the following bipartite graph.

    .. graphviz::

       digraph bipartite {
          graph [rankdir = LR];
          "reviewer-0";
          "reviewer-1";
          "product-0";
          "product-1";
          "product-2";
          "reviewer-0" -> "product-0";
          "reviewer-0" -> "product-1";
          "reviewer-0" -> "product-2";
          "reviewer-1" -> "product-1";
          "reviewer-1" -> "product-2";
       }

    """

    def setUp(self):
        """Set up a sample graph.
        """
        self.graph = bipartite.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)
        ]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)
        ]
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.graph.add_review(r, self.products[j], 0.3)

        self.credibility = credibility.GraphBasedCredibility(self.graph)

    def test_call(self):
        """Test calling credibility.
        """
        with self.assertRaises(NotImplementedError):
            self.credibility(self.products[0])

    def test_reviewers(self):
        """Test reviewers.
        """
        self.assertEqual(
            set(self.credibility.reviewers(self.products[2])),
            set(self.reviewers))

    def test_review_score(self):
        """Test review_score.
        """
        self.assertEqual(
            self.credibility.review_score(self.reviewers[0], self.products[1]),
            0.3)


class WeightedCredibility(unittest.TestCase):
    """Test case for WeightedCredibility.

    This test case uses the following bipartite graph.

    .. graphviz::

       digraph bipartite {
          graph [rankdir = LR];
          "reviewer-0";
          "reviewer-1";
          "product-0";
          "product-1";
          "product-2";
          "reviewer-0" -> "product-0";
          "reviewer-0" -> "product-1";
          "reviewer-0" -> "product-2";
          "reviewer-1" -> "product-1";
          "reviewer-1" -> "product-2";
       }

    """

    def setUp(self):
        """Set up a sample graph.
        """
        self.graph = bipartite.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)
        ]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)
        ]
        self.reviews = []
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.reviews.append(
                    self.graph.add_review(r, self.products[j], random.random()))

        self.credibility = credibility.WeightedCredibility(self.graph)

    def test_np_1(self):
        """Test credibility with a product which has only one review.
        """
        self.assertEqual(self.credibility(self.products[0]), 0.5)

    def test(self):
        """Test credibility.
        """
        target = self.products[2]
        average = np.mean([self.reviews[i].score for i in (2, 4)])
        sigma2 = sum((self.reviews[i].score - average)**2 for i in (2, 4))
        self.assertAlmostEqual(
            self.credibility(target), np.log(2) / (sigma2 + 1))


if __name__ == "__main__":
    unittest.main()
