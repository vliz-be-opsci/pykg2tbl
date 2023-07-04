pykg2tbl
===================================

Pykg2tbl is a Python library that facilitates the extraction of table data from knowledge graphs using sparql templates

Started on 2022-01-04

Features
-----

- Extract table data from knowledge graphs using SPARQL templates
- User-friendly interface for defining extraction requirements
- Customizable SPARQL templates to accommodate different data extraction scenarios
- Automation of the extraction process for time-saving and efficiency
- Seamless integration with data analysis tools, visualization libraries, and downstream applications

Installation
-----
To install Pykg2tbl, follow these steps:

    1. Clone the repository: ``git clone https://github.com/vliz-be-opsci/pykg2tbl.git``
    2. Navigate to the project directory: ``cd pykg2tbl``
    3. Install the required dependencies: ``make init``
    4. (Optional) Install additional dependencies for development: ``make init-dev``

Usage
-----
Pykg2tbl provides a straightforward process for extracting table data from knowledge graphs. Here's an example of how to use Pykg2tbl:

.. code-block:: python

    import pykg2tbl

    # Define the SPARQL template for table extraction
    template = """
        SELECT ?name ?age ?city
        WHERE {
            ?person rdf:type foaf:Person .
            ?person foaf:name ?name .
            ?person foaf:age ?age .
            ?person foaf:city ?city .
        }
    """

    # Execute the extraction process
    table_data = pykg2tbl.extract_table(template)

    # Process and analyze the extracted table data
    # ...

    # Visualize the extracted table data
    # ...

For more detailed information on the usage of Pykg2tbl, refer to the `official documentation <https://open-science.vliz.be/pykg2tbl/>`.

Contributing
-----

We welcome contributions from the community to enhance Pykg2tbl. If you'd like to contribute, please follow these guidelines:

    1. Fork the repository and create a new branch for your feature or bug fix.
    2. Make your changes and ensure that the code adheres to the project's coding style.
    3. Write unit tests to cover your changes and ensure they pass.
    4. Submit a pull request with a clear description of your changes and the problem they solve.

For more information on contributing to Pykg2tbl, please refer to the `contribution guidelines </CONTRIBUTING.rst>`.


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
    $ make test-coverage                                          # to run all tests and check the test coverage


Check the code-style and syntax (flake8, black, isort)

.. code-block:: bash

    $ make check


.. image:: https://github.com/vliz-be-opsci/pykg2tbl/blob/gh-pages/coverage.svg
   :align: center
   :target: https://github.com/JotaFan/pycoverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :align: center
   :alt: Code style: black
   :target: https://github.com/psf/black


