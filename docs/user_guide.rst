User Guide
==========

This is a step-by-step guide on how to use the ZXQEP package.

Constructing the Initial PyZX Graph
--------------------------------------

First, create your base circuit using PyZX's ``Graph`` class. To ensure compatibility with ZXQEP's functions, your graph must adhere to the following structural rules:

* **Circuit Layout:** The graph must contain the rectangular structure found in standard circuit diagrams. 
* **No Hadamard Edges:** You must use explicit Hadamard *nodes* (spiders) rather than Hadamard *edges*.
* **Boundary Strictness:** All inputs must be placed at the very beginning of the circuit (in the 0th column, on the far left), and all outputs must be placed at the very end (the final column, on the far right).
* **State Initialization & Measurement:** You may begin rows with a spider for state initialization, and you may also end rows with a spider to represent a measurement, so long as all your input and output points are nodes.

Initializing the ZXQEPGraph Object
-------------------------------------

Once you have your base graph, you can pass it into the package by creating a ``ZXQEPGraph`` object.

.. code-block:: python

    import zxqep
    import pyzx as zx

    # Create your ZXQEPGraph object
    qep_graph = zxqep.ZXQEPGraph(base_graph)

Injecting Errors
-------------------

With your ``ZXQEPGraph`` object initialized, you can inject errors into the circuit using the ``inject_error`` method. 

Currently, the ``inject_error`` method only has functionality under the following conditions:

* **Error Types:** The type of error must be an `X`, `Z`, or `Y`, corresponding to the type of phase error
* **Clifford Only:** Non-Clifford errors are not supported. The phase of the X or Z errors must be exact multiples of Pi/2 (the input is in units of Pi, thus it must be in multiples of 1/2)
* **Placement Boundaries:** Errors must be injected strictly *after* the 0th column (inputs) and *before* the final column (outputs). They can be injected into any row.
* **Quantity limits:** While the function allows you to inject multiple errors into the graph, it currently only guarantees the successful and accurate propagation of a *single* Clifford error at a time.

.. code-block:: python

    # Example: Inject a Pauli X error on row 1, column 2
    qep_graph.inject_error(row=1, col=2, err_type='X')

Propagating the Error
------------------------

To see how the injected error propagates to the end of the circuit, use the  ``propagate_to_end()`` method. 

You can pass a boolean value to this function to print out the resulting propagated errors and the specific qubits they land on.

.. code-block:: python

    # Propagate the error and print the resulting error states and locations
    qep_graph.propagate_to_end(print_results=True)

Visualization and Conversion
-------------------------------

To visualize the current state of the error in your circuit can use the ``draw()`` method directly on your ``ZXQEPGraph`` object. This can be done both before and after propgating the error.

If you wish to convert your graph back to a PyZX graph, that can be done by using the ``to_pyzx_graph()`` method.

.. code-block:: python

    # Visualize the ZXQEPGraph natively
    qep_graph.draw()

    # Convert back to a standard PyZX graph
    resolved_pyzx_graph = qep_graph.to_pyzx_graph()