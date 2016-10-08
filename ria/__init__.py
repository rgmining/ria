#
# __init__.py
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
"""Implement the Repeated Improvement Analysis (RIA) and
Mutually Reinforcing Analysis (MRA).

We introduce RIA in the 7th Forum on Data Engineering and Information Management
(DEIM 2015) and MRA in the 22nd International Conference on Database and Expert
Systems Applications (DEXA 2011).

This package also provides another analysis algorithm, One, which employs
one anomalous index proposed by Ee-Peng Lim *ea al.* in the 19th International
Conference on Information and Knowledge Management (CIKM 2010), and its
extended version OneSum.

The top level module of this package provides four constructor functions, which
create review graph providing above four algorithms.
"""
from __future__ import absolute_import
from ria.bipartite import BipartiteGraph
from ria.credibility import UniformCredibility
import ria.one as one
import ria.bipartite_sum as bipartite_sum


def ria_graph(alpha):
    """Create a review graph providing RIA algorithm with a parameter alpha.

    Args:
      alpha: Parameter.

    Returns:
      A review graph.
    """
    return BipartiteGraph(alpha=alpha)


def mra_graph():
    """Create a review graph providing MRA algorithm.

    Returns:
      A review graph.
    """
    return BipartiteGraph(credibility=UniformCredibility, alpha=1)


def one_graph():
    """Create a review graph providing One algorithm.

    Returns:
      A review graph.
    """
    return one.BipartiteGraph(credibility=UniformCredibility, alpha=1)


def one_sum_graph():
    """Create a review graph providing OneSum algorithm.

    Returns:
      A review graph.
    """
    return bipartite_sum.BipartiteGraph(credibility=UniformCredibility, alpha=1)
