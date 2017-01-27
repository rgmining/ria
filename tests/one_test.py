#
# one_test.py
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
"""Unit test for ria.one module.
"""
import unittest
from ria import one


class TestBipartiteGraph(unittest.TestCase):
    """Test case for one.BipartiteGraph.

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
        self.graph = one.BipartiteGraph()
        self.reviewers = [
            self.graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
        self.products = [
            self.graph.new_product("product-{0}".format(i)) for i in range(3)]
        for i, r in enumerate(self.reviewers):
            for j in range(i, len(self.products)):
                self.graph.add_review(
                    r, self.products[j], 0.1 if i == 0 else 0.8)

    def test_update(self):
        """Test update only works once.
        """
        self.graph.update()
        self.assertEqual(self.graph.update(), 0)


if __name__ == "__main__":
    unittest.main()
