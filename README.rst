pykg2tbl
===================================

Py Project to extra table data from knowledge-graphs using sparql templates

Started on 2022-01-04

Setup
-----
Start using this project with poetry


.. code-block:: bash

    $ make init       # install dependencies
    $ make init-dev   # includes the previous + adds dependencies for developers

Build Docs

.. code-block:: bash

    $ make docs



Developers
----------

Run Tests

.. code-block:: bash

    $ make test                                                   # to run all tests
    $ PYTEST_LOGCONF=debug-logconf.yml python tests/test_demo.py  # to run a specific test with specific logging


Check the code-style and syntax (flake8)

.. code-block:: bash

    $ make check
