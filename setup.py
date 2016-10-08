#
# setup.py
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
# pylint: skip-file
"""Package information of repeated improvement analysis algorithm.
"""
from setuptools import setup, find_packages


def _load_requires_from_file(filepath):
    """Read a package list from a given file path.

    Args:
      filepath: file path of the package list.

    Returns:
      a list of package names.
    """
    with open(filepath) as fp:
        return [pkg_name.strip() for pkg_name in fp.readlines()]


setup(
    name='rgmining-ria',
    version='0.9.0',
    author="Junpei Kawamoto",
    author_email="kawamoto.junpei@gmail.com",
    description="Repeated Improvement Analysis Algorithm for Review graph mining project",
    url="https://github.com/rgmining/common",
    packages=find_packages(exclude=["tests"]),
    install_requires=_load_requires_from_file("requirements.txt"),
    test_suite='tests.suite',
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ]
)
