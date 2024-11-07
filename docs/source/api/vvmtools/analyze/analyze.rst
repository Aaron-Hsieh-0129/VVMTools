analyze module
====================

.. autoclass:: vvmtools.analyze.DataRetriever
   :exclude-members: get_var, get_var_parallel, func_time_parallel


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

   vvmtools.analyze.create_nc_output
   vvmtools.analyze.DataRetriever.get_var
   vvmtools.analyze.DataRetriever.get_var_parallel
   vvmtools.analyze.DataRetriever.func_time_parallel