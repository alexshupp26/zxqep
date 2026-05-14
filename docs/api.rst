API Reference
=============

This section contains the API documentation for the classes and functions in ``zxqep``. 

.. currentmodule:: zxqep

ZXQEPNode Object
-----------------
The class used to represent the node objects present in ZXQEPGraph objects

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
The methods for ZXQEPGraph objects

.. autosummary::
   :toctree: _autosummary

   ZXQEPGraph.inject_error
   ZXQEPGraph.propagate_to_end
   ZXQEPGraph.to_pyzx_graph
   ZXQEPGraph.draw