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

   $ python pvxmlgen.py [input.h] [output.xml]

   or

   $ python pvxmlgen.py [input.h] -

   for printing to standard output


Contributing
------------

   $ pip install pytest
   $ py.test tests
