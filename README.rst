pvxmlgen
========

.. image:: https://travis-ci.org/lhofmann/pvxmlgen.png?branch=master
    :target: https://travis-ci.org/lhofmann/pvxmlgen

.. image:: https://coveralls.io/repos/github/lhofmann/pvxmlgen/badge.svg?branch=master
    :target: https://coveralls.io/github/lhofmann/pvxmlgen?branch=master

Automatically generate and update ParaView ServerManager XML from C++ headers using custom doxygen commands.


Requirements
------------

* Python 3
* Doxygen 1.8


Usage
-----

Not usable yet.


Contributing
------------

Clone this repository and install with pip (optionally inside a virtualenv)::

   $ git clone https://github.com/lhofmann/pvxmlgen.git
   $ cd pvxmlgen
   $ pip install --user -e .

Tests need additional requirements and ``tox`` (optional)::

   $ pip install -r test-requirements.txt
   $ pip install tox

Tests can be run by simply invoking ``tox`` or manually::

   $ py.test tests
   $ flake8 pvxmlgen


Doxygen Commands
----------------

* ``@pv_plugin{proxygroup}``
    
    Expose class and set proxygroup

    .. code-block:: cpp

       /** @pv_plugin{filters} */
       class vtkMyFilter : public vtkAlgorithm {

    .. code-block:: cpp

       /** @pv_plugin{sources} */
       class vtkMySource : public vtkAlgorithm {

* ``@pv_member``

    Expose member variable

    .. code-block:: cpp

       /** @pv_member */
       int MyMember {2};

* ``@pv_member{label}``

    Expose member variable and set label

    .. code-block:: cpp

       /** @pv_member{Label for this member} */
       int MyMember {2};

* ``@pv_attr{name,value}``

    Set attribute of current XML tag

    .. code-block:: cpp

       /** @pv_plugin{filters} 
        *  @pv_attr{label, Label for this filter} 
        */
       class vtkMyFilter : public vtkAlgorithm {

* ``@pv_begin_insert``, ``@pv_begin_append``, ``@pv_end`` 

    Insert or append arbitrary XML

    .. code-block:: cpp

       /** @pv_plugin{filters} 
        *  @pv_begin_insert
                <Hints>
                    <ShowInMenu category="My Category" />
                </Hints>
           @pv_end 
        */
       class vtkMyFilter : public vtkAlgorithm {

    .. code-block:: cpp

       /** @pv_begin_insert 
                <EnumerationDomain name="enum">
                    <Entry value="0" text="Option A"/>
                    <Entry value="1" text="Option B"/>
                </EnumerationDomain>       
           @pv_end 
        */
       int MyMember {1};

