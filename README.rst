pvxmlgen
========

.. image:: https://travis-ci.org/lhofmann/pvxmlgen.png?branch=master
    :target: https://travis-ci.org/lhofmann/pvxmlgen

.. image:: https://coveralls.io/repos/github/lhofmann/pvxmlgen/badge.svg?branch=master
    :target: https://coveralls.io/github/lhofmann/pvxmlgen?branch=master

Generates ParaView ServerManager XML from C++ headers with specially crafted comments.


Requirements
------------

* Python 3

Usage
-----

.. code-block:: bash

   $ python pvxmlgen.py [input.h] [output.xml]

or

.. code-block:: bash

   $ python pvxmlgen.py [input.h] -

for printing to standard output


Contributing
------------

Run tests with pytest and linter with flake8

.. code-block:: bash

   $ pip install pytest flake8
   $ py.test tests
   $ flake8
