Getting Started
===============

This is a guide to help you install ZXQEP.

Prerequisites
-------------

ZXQEP requires **Python 3.10 or higher**. 

.. note::
   ZXQEP is built upon the PyZX python package for visualizing and simplifying ZX-Calculus circuits, which requires **Python 3.10 or higher**

Installation
------------

To install the package from the source repository, navigate to the root directory of the project and run:

.. code-block:: bash

    pip install .


You can verify the installation by running the test suite from the root directory:

.. code-block:: bash

    pytest

Example
-----------

Here is a short example demonstrating how to initialize a graph, inject a Pauli error, propagate it using ZX-calculus, and visualize that graph.

.. jupyter-execute::

    import zxqep as ep
    import pyzx as zx

    ## Initialize the graph
    graph = zx.Graph()

    # Add inputs
    v00 = graph.add_vertex(0,0,0)
    v10 = graph.add_vertex(1,1,0)

    # Hadamard on the first qubit
    v01 = graph.add_vertex(3,0,1)

    # CNOT with the control on the first qubit, and the target on the second qubit
    v02 = graph.add_vertex(1,0,2)
    v12 = graph.add_vertex(2,1,2)
    graph.add_edge((v02,v12))

    # Add outputs
    v03 = graph.add_vertex(0,0,3)
    v13 = graph.add_vertex(0,1,3)

    # Add horizontal connections
    graph.add_edges([(v00,v01),(v01,v02),(v02,v03)])
    graph.add_edges([(v10,v12),(v12,v13)])

    # Convert the graph into a ZXQEPGraph object
    error_graph = ep.ZXQEPGraph(graph)

    ## Inject an error 
    error_graph.inject_error(row=0, col=1, err_type='Z', fraction_val=1)

    ## Visualize the error
    error_graph.draw()

    ## Propagate the error
    error_graph.propagate_to_end()

    ## Visualize the propagated error
    error_graph.draw()
