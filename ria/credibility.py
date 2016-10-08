#
# credibility.py
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
"""Defines functor classes computing credibility.

Credibility is a function-like class which has __call__ method.
This method receives only one argument, an instance of
:class:`ria.bipartite.Product`, and return a value of credibility.

This module has a helper base class :class:`GraphBasedCredibility`
which provides two helper functions traversing a bipartite graph.

The credibilities defined in this module are;

- :class:`UniformCredibility`
- :class:`WeightedCredibility`

"""
from __future__ import absolute_import
import numpy as np
from common import memoized


class UniformCredibility(object):
    """Uniform credibility assigns 1 for every product.

    Formally, this credibility is defined by

    .. math::

        {\\rm cred}(p) = 1,

    where *p* is a product.

    Uniform credibility does not use any arguments to construct.
    """
    __slots__ = ()

    def __init__(self, *unused_args):
        pass

    def __call__(self, product):
        """ Compute credibility of a given product.

        Args:
          product: An instance of :class:`bipartite.Product`.

        Returns:
          Always 1.
        """
        return 1.


class GraphBasedCredibility(object):
    """Abstract class of credibility using a Bipartite graph.

    Args:
      g: A bipartite graph instance.

    This class provides two helper methods; :meth:`reviewers` and
    :meth:`review_score`.
    """
    __slots__ = ("_g")

    def __init__(self, g):
        """Construct a GraphBasedCredibility with a given graph instance g.

        Args:
          g: A bipartite graph instance.
        """
        self._g = g

    def __call__(self, product):
        """Compute credibility of a given product.

        Args:
          product: An instance of :class:`ria.bipartite.Product`.
        """
        raise NotImplementedError

    def reviewers(self, product):
        """Find reviewers who have reviewed a given product.

        Args:
          product: An instance of :class:`ria.bipartite.Product`.

        Returns:
          A list of reviewers who have reviewed the product.
        """
        return self._g.retrieve_reviewers(product)

    def review_score(self, reviewer, product):
        """Find a review score from a given reviewer to a product.

        Args:
          reviewer: Reviewer i.e. an instance of :class:`ria.bipartite.Reviewer`.
          product: Product i.e. an instance of :class:`ria.bipartite.Product`.

        Returns:
          A review object representing the review from the reviewer to the product.
        """
        return self._g.retrieve_review(reviewer, product).score


class WeightedCredibility(GraphBasedCredibility):
    """Credibility using unbiased variance of review scores.

    Args:
      g: an instance of bipartite graph.

    The credibility computed by this class is defined by

    .. math::

        {\\rm cred}(p) = \\begin{cases}
            0.5 \\quad \\mbox{if} \\; N_{p} = 1, \\\\
            \\frac{\\log N_{p}}{\\sigma^{2} + 1} \\quad \\mbox{otherwise},
        \\end{cases}

    where :math:`N_{p}` is the number of reviews for the product *p*
    and :math:`\\sigma^{2}` is the unbiased variance of review scores.
    The unbiased variance is defined by

    .. math::

        \\sigma^{2} = \\frac{1}{N_{p} - 1} \\sum_{r \\in R} \\left(
            {\\rm review}(r, p)
            - \\frac{1}{N_{p}}\\sum_{r' \\in r} {\\rm review}(r', p)
        \\right)^{2},

    where :math:`{\\rm review}(r, p)` is a review from reviewer *r* to
    product *p*.
    """
    @memoized
    def __call__(self, product):
        """ Compute credibility of a given product.

        Args:
          product: An instance of :class:`bipartite.Product`.

        Returns:
          The credibility of the product. It is >= 0.5.
        """
        reviewers = self.reviewers(product)
        Nq = len(reviewers)

        if Nq == 1:
            return 0.5

        else:
            # Computing the unbiased variance of scores.
            var = np.var([self.review_score(r, product)
                          for r in reviewers], ddof=1)
            return np.log(Nq) / (var + 1)
