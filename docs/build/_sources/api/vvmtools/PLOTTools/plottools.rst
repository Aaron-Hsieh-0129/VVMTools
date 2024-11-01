PLOTTools Module
====================

.. autoclass:: vvmtools.PLOTTools.dataPlotters

Attributes
----------

.. autosummary:: 
   :toctree: attribute
   :nosignatures:

- **VARTYPE**: Dictionary of variable types. 
- **DIM**: Dictionary of spatial dimensions. There will be `xc`, `yc` `zc` (grid center), `zz` (grid upper) inside the dictionary
- **INIT**: Dictionary of initial profile data. There will be `RHO`, `THBAR`, `PBAR`, `PIBAR`, and `QVBAR` inside the dictionary
- **time_array_str**: Array of time values. The array is generated from 05:00 to 05:00 the next day at 2-minute intervals. (721 elements)


Methods
-------

.. autosummary::
   :toctree: generated

   vvmtools.PLOTTools.dataPlotters.draw_xt