#
# test_suite.py
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
"""Test suite.
"""
from __future__ import absolute_import, print_function
import importlib
import sys
import unittest


TESTS = (
    "tests.bipartite_test",
    "tests.bipartite_sum_test",
    "tests.credibility_test",
    "tests.one_test",
)
"""Collection of test modules."""


def suite():
    """Returns a test suite.
    """
    loader = unittest.TestLoader()
    res = unittest.TestSuite()

    for t in TESTS:
        mod = importlib.import_module(t)
        res.addTest(loader.loadTestsFromModule(mod))
    return res


def main():
    """The main function.

    Returns:
      Status code.
    """
    try:
        res = unittest.TextTestRunner(verbosity=2).run(suite())
    except KeyboardInterrupt:
        print("Test canceled.")
        return -1
    else:
        return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
