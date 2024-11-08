analyze module
====================

Module Functions
----------------

.. autosummary::
   :toctree: generated

   vvmtools.analyze.create_nc_output


Module Class
----------------

.. autoclass:: vvmtools.analyze.DataRetriever
   :members:
   :exclude-members: get_var, get_var_parallel, func_time_parallel
   :show-inheritance:

   **Attributes:**

      VARTYPE
         Dictionary of variable types.

      DIM
         Dictionary of spatial dimensions, containing keys such as `xc`, `yc`, `zc` (grid center), and `zz` (grid upper).

      INIT
         Dictionary of initial profile data with entries for `RHO`, `THBAR`, `PBAR`, `PIBAR`, and `QVBAR`.

      time_array_str
         Array of time values generated from 05:00 to 05:00 the next day at 2-minute intervals (721 elements).


   **Methods:**

   .. autosummary::
      :toctree: generated
      :nosignatures:

      vvmtools.analyze.DataRetriever.get_var
      vvmtools.analyze.DataRetriever.get_var_parallel
      vvmtools.analyze.DataRetriever.func_time_parallel