#
# bipartite_sum_test.py
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
"""Unit test for ria.bipartite_sum module.
"""
# pylint: disable=protected-access
from collections import defaultdict
import unittest
from ria import bipartite_sum


class TestReviewer(unittest.TestCase):
    """Test case for reviewer class in bipartite_sum module.

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
        self.graph = bipartite_sum.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        self.reviews = defaultdict(dict)
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.reviews[i][j] = self.graph.add_review(
                    r, self.products[j], 0.1 if i == 0 else 0.8)

    def test_update_anomalous_score(self):
        """Test updating anomalous scores.

        A new anomalous score is the weighted average of differences
        between current summary and reviews. The weights come from credibilities.

        Therefore, the new anomalous score is defined as

        .. math::

            {\\rm anomalous}(r)
            = \\sum_{p \\in P} \\mbox{review}(p) \\times \\mbox{credibility}(p)
              - 0.5

        where :math:`P` is a set of products reviewed by this reviewer,
        review(:math:`p`) and credibility(:math:`p`) are
        review and credibility of product :math:`p`, respectively.
        """
        res = 0
        for i, r in enumerate(self.reviews[0].values()):
            p = self.products[i]
            c = self.reviewers[0]._credibility(p)
            res += p.summary.difference(r) * c - 0.5

        old = self.reviewers[0].anomalous_score
        self.assertAlmostEqual(self.reviewers[0].update_anomalous_score(),
                               abs(old - res))
        self.assertAlmostEqual(self.reviewers[0].anomalous_score, res)


if __name__ == "__main__":
    unittest.main()
