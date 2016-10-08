#
# one.py
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
"""Provide a review graph which implement One algorithm.

In One algorithm, only one updating scores is allowed. Thus, the review graph
defined in this module overwrites :meth:`ria.bipartite.BipartiteGraph.update`
so that it works only one time.
"""
from __future__ import absolute_import
from ria import bipartite


class BipartiteGraph(bipartite.BipartiteGraph):
    """Bipartite graph implementing One algorithm.

    Attributes:
      updated: Whether :meth:`update` has been called. If True, that method does
        nothing.
    """

    def __init__(self, **kwargs):
        super(BipartiteGraph, self).__init__(**kwargs)
        self.updated = False

    def update(self):
        """Update reviewers' anomalous scores and products' summaries.

        Returns:
          maximum absolute difference between old summary and new one, and
          old anomalous score and new one.
        """
        if self.updated:
            return 0

        res = super(BipartiteGraph, self).update()
        self.updated = True
        return res
