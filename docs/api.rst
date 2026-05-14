API Reference
=============

This section contains the API documentation for the classes and functions in ``zxqep``. 

.. currentmodule:: zxqep

ZXQEPNode Object
-----------------
The primary class used to represent, inject, and propagate errors through a grid-based ZX-calculus graph.

.. autosummary::
   :toctree: _autosummary

   ZXQEPNode

ZXQEPGraph Object
-----------------
The primary class used to represent, inject, and propagate errors through a grid-based ZX-calculus graph.

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :recursive:

   ZXQEPGraph

ZXQEPGraph Methods
------------------
If you want to explicitly highlight the key methods available on the ``ZXQEPGraph`` object in your main API table, you can list them out here. 

.. autosummary::
   :toctree: _autosummary

   ZXQEPGraph.inject_error
   ZXQEPGraph.propagate_to_end
   ZXQEPGraph.to_pyzx_graph
   ZXQEPGraph.draw