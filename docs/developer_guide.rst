Developer Guide
===============

This is a guide for how to contribute to the ZXQEP package.

Installation
------------

To perform a developmental install of the package from the source repository, navigate to the root directory of the project and run:

.. code-block:: bash

    pip install -e .

Testing
-------

The ``zxqep`` package utilizes ``pytest`` for function testing. 

Right now, there are 15 tests, all checking that the class propagates injected errors accurately.

To run these tests, navigate to the root directory of the repository and run:

.. code-block:: bash

    pytest
