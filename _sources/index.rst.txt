:description: This package provides 4 algorithms for review graph mining project.
    Mutually Reinforcing Analysis (MRA) algorithm is an algorithm we've
    introduced in DEXA 2011, Repeated Improvement Analysis (RIA) algorithm
    is an algorithm we've introduced in DEIM 2015.

.. _top:

Repeated Improvement Analysis
===============================
.. raw:: html

   <div class="addthis_inline_share_toolbox"></div>

This package provides 4 algorithms for review graph mining project.
**Mutually Reinforcing Analysis (MRA)** algorithm is an algorithm we've introduced
in DEXA 2011 [#DEXA2011]_, **Repeated Improvement Analysis (RIA)** algorithm
is an algorithm we've introduced in DEIM 2015 [#DEIM2015]_.

Algorithm **One** has been proposed by Ee-Peng Lim *ea al.* in CIKM 2010 [#CIKM2010]_.
Algorithm **OneSum** is an variation of it made by us.

This package is a part of `Review Graph Mining Project </>`_
which provides other algorithms, datasets, and helper libraries.


Installation
--------------
Use `pip` to install this package.

.. code-block:: bash

   pip install --upgrade rgmining-ria


Graph model
-------------
This package assumes review data are represented in a bipartite graph.
This bipartite graph has two kinds of nodes; reviewers and products.
One reviewer node and one product node are connected if the reviewer posts
a review to the product.
In other words, an edge in the graph represents a review.
Each review has a rating score.
We assume the score is normalized in 0 to 1.

Here is a sample of the bipartite graph.

.. graphviz::

  digraph bipartite {
     graph [label="Sample bipartite graph.", rankdir = LR];
     "reviewer-0";
     "reviewer-1";
     "product-0";
     "product-1";
     "product-2";
     "reviewer-0" -> "product-0" [label="0.2"];
     "reviewer-0" -> "product-1" [label="0.9"];
     "reviewer-0" -> "product-2" [label="0.6"];
     "reviewer-1" -> "product-1" [label="0.1"];
     "reviewer-1" -> "product-2" [label="0.7"];
  }


Usage
------

Construct a graph
^^^^^^^^^^^^^^^^^^
This package provides four functions to construct graph objects.

* :meth:`ria.mra_graph` creates a review graph running MRA algorithm.
* :meth:`ria.ria_graph` creates a review graph running RIA algorithm.
  It takes one parameter :math:`\\alpha`.
* :meth:`ria.one_graph` and :meth:`ria.one_sum_graph` create a review graph
  running One and OneSum algorithm, respectively.

For example, to create a review graph running RIA algorithm,

.. code-block:: python

   import ria
   graph = ria.ria_graph(1.0)

Then, you need to add reviewer nodes, product nodes, and review edges.
:meth:`new_reviewer()<ria.bipartite.BipartiteGraph.new_reviewer>` and
:meth:`new_product()<ria.bipartite.BipartiteGraph.new_product>` methods
of the graph create a reviewer node and a product node, respectively,
and add them to the graph. Both methods take one argument `name`, i.e. ID of
the node.
Note that, the names must be unique in a graph.

:meth:`add_review()<ria.bipartite.BipartiteGraph.add_review>` method add a
review to the graph. It takes a `reviewer`, a `product`, and a normalized
rating score which the reviewer posted to the product.
The normalized rating scores mean they must be in 0 to 1.

For example, let us assume there are two reviewers and three products
like the below.

.. graphviz::

  digraph bipartite {
     graph [label="Sample bipartite graph.", rankdir = LR];
     "reviewer-0";
     "reviewer-1";
     "product-0";
     "product-1";
     "product-2";
     "reviewer-0" -> "product-0" [label="0.2"];
     "reviewer-0" -> "product-1" [label="0.9"];
     "reviewer-0" -> "product-2" [label="0.6"];
     "reviewer-1" -> "product-1" [label="0.1"];
     "reviewer-1" -> "product-2" [label="0.7"];
  }

The graph can be constructed by the following code.

.. code-block:: python

  # Create reviewers and products.
  reviewers = [graph.new_reviewer("reviewer-{0}".format(i)) for i in range(2)]
  products = [graph.new_product("product-{0}".format(i)) for i in range(3)]
  graph.add_review(reviewers[0], products[0], 0.2)
  graph.add_review(reviewers[0], products[1], 0.9)
  graph.add_review(reviewers[0], products[2], 0.6)
  graph.add_review(reviewers[1], products[0], 0.1)
  graph.add_review(reviewers[1], products[1], 0.7)


Analysis
^^^^^^^^^^^
:meth:`update()<fraud_eagle.graph.ReviewGraph.update>` runs one iteration of
`loopy belief propagation algorithm <https://arxiv.org/pdf/1206.0976.pdf>`_.
This method returns the amount of update in the iteration.
You need to run iterations until the amount of update becomes enough small.
It's depended to the review data and the parameter epsilon that how many
iterations are required to the amount of update becomes small.
Moreover, sometimes it won't be converged.
Thus, you should set some limitation to the iterations.

.. code-block:: python

  print("Start iterations.")
  max_iteration = 10000
  for i in range(max_iteration):

     # Run one iteration.
     diff = graph.update()
     print("Iteration %d ends. (diff=%s)", i + 1, diff)

     if diff < 10**-5: # Set 10^-5 as an acceptable small number.
         break


Result
^^^^^^^^
Each reviewer has an anomalous score which representing how the reviewer is
anomalous. The score is normalized in 0 to 1. To obtain that score,
use :meth:`anomalous_score<fraud_eagle.graph.Reviewer.anomalous_score>`
property.

The :class:`ReviewGraph<fraud_eagle.graph.ReviewGraph>` has
:meth:`reviewers<fraud_eagle.graph.ReviewGraph.reviewers>` property,
which returns a collection of reviewers the graph has.
Thus, the following code outputs all reviewers' anomalous score.

.. code-block:: python

  for r in graph.reviewers:
      print(r.name, r.anomalous_score)

On the other hand, each product has a summarized ratings computed from all
reviews posted to the product according to each reviewers' anomalous score.
The summarized ratings are also normalized in 0 to 1.
:meth:`summary<fraud_eagle.graph.Product.summary>` property returns such
summarized rating.

The :class:`ReviewGraph<fraud_eagle.graph.ReviewGraph>` also has
:meth:`products<fraud_eagle.graph.ReviewGraph.products>` property,
which returns a collection of products.
Thus, the following code outputs all products' summarized ratings.

.. code-block:: python

  for p in graph.products:
      print(p.name, p.summary)


API Reference
---------------
.. toctree::
  :glob:
  :maxdepth: 2

  modules/*


License
---------
This software is released under The GNU General Public License Version 3,
see `COPYING <https://github.com/rgmining/ria/blob/master/COPYING>`_ for more detail.


References
------------

.. [#DEXA2011] Kazuki Tawaramoto, `Junpei Kawamoto`_, `Yasuhito Asano`_, and `Masatoshi Yoshikawa`_,
  "|springer| `A Bipartite Graph Model and Mutually Reinforcing Analysis for Review Sites
  <http://www.anrdoezrs.net/links/8186671/type/dlg/http://link.springer.com/chapter/10.1007%2F978-3-642-23088-2_25>`_,"
  Proc. of `the 22nd International Conference on Database and Expert Systems Applications <http://www.dexa.org/>`_ (DEXA 2011),
  pp.341-348, Toulouse, France, August 31, 2011.
.. [#DEIM2015] `川本 淳平`_, 俵本 一輝, `浅野 泰仁`_, `吉川 正俊`_,
  "|pdf| `初期レビューを用いた長期間評価推定 <http://db-event.jpn.org/deim2015/paper/253.pdf>`_,"
  `第7回データ工学と情報マネジメントに関するフォーラム <http://db-event.jpn.org/deim2015>`_,
  D3-6, 福島, 2015年3月2日～4日. |deim2015-slide|
.. [#CIKM2010] `Ee-Peng Lim <https://sites.google.com/site/aseplim/>`_,
  `Viet-An Nguyen <http://www.cs.umd.edu/~vietan/>`_,
  Nitin Jindal,
  `Bing Liu <https://www.cs.uic.edu/~liub/>`_,
  `Hady Wirawan Lauw <http://www.smu.edu.sg/faculty/profile/9621/Hady-W-LAUW>`_,
  "`Detecting Product Review Spammers Using Rating Behaviors
  <http://dl.acm.org/citation.cfm?id=1871557>`_,"
  Proc. of the 19th ACM International Conference on Information and Knowledge Management,
  pp.939-948, 2010.

.. _Junpei Kawamoto: https://www.jkawamoto.info
.. _Yasuhito Asano: http://www.iedu.i.kyoto-u.ac.jp/intro/member/asano
.. _Masatoshi Yoshikawa: http://www.db.soc.i.kyoto-u.ac.jp/~yoshikawa/
.. _川本 淳平: https://www.jkawamoto.info
.. _浅野 泰仁: http://www.iedu.i.kyoto-u.ac.jp/intro/member/asano
.. _吉川 正俊: http://www.db.soc.i.kyoto-u.ac.jp/~yoshikawa/

.. |springer| image:: img/springer.png

.. |pdf| raw:: html

   <i class="fa fa-file-pdf-o" aria-hidden="true"></i>

.. |deim2016-slide| raw:: html

   <a href="http://www.slideshare.net/jkawamoto/ss-59672505">
    <i class="fa fa-slideshare" aria-hidden="true"></i>
   </a>

.. |deim2015-slide| raw:: html

  <a href="http://www.slideshare.net/jkawamoto/deim2015-45470497">
   <i class="fa fa-slideshare" aria-hidden="true"></i>
  </a>
