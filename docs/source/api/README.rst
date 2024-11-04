VVMTools
========

VVMTools is a Python class designed to extract and process variables from simulation output files, especially NetCDF files. It includes functions to handle spatial dimensions, time intervals, topographic variables, and supports parallel processing to optimize data handling. The class also provides logging for debugging.

Features
--------

- **Variable Extraction**: Extract variable data from NetCDF files using specified time steps and domain ranges.
- **Topographic Variable Handling**: Load topographic variables from ``TOPO.nc`` files.
- **Parallel Processing**: Efficiently extract data across multiple time steps using multiprocessing.
- **Time Array Generation**: Create a time array from 05:00 to 05:00 the next day at 2-minute intervals.
- **Initial Profile Parsing**: Parse and store atmospheric profiles (e.g., RHO, THBAR, PBAR) from ``fort.98``.
- **Debugging**: Enable debug mode for logging and troubleshooting.

Requirements
------------

- Python 3.x
- Required libraries:
  - ``xarray``
  - ``numpy``
  - ``multiprocessing``
  - ``logging``

Installation
------------

Install the package from PyPI:

.. code-block:: bash

    pip install git+https://github.com/Aaron-Hsieh-0129/VVMTools.git


You can also clone this repository and install the required dependencies:

.. code-block:: bash

    pip install xarray numpy



Usage
------

Initialization
--------------

To initialize the ``VVMTools`` class, provide the path to the directory containing the case files. Optionally, enable ``debug_mode`` to log more detailed information:

.. code-block:: python

    import vvmtools

    case_path = "/path/to/case/files"
    mytools = vvmtools.analyze.DataRetriever(case_path, debug_mode=True)

Example Operations
------------------

1. **Extract a Variable**

   To retrieve a variable at a specific time step, use the ``get_var`` method:

   .. code-block:: python

       var_data = mytools.get_var("th", time=0, numpy=True)

2. **Parallel Data Extraction**

   For faster processing of data over multiple time steps, use ``get_var_parallel``:

   .. code-block:: python

       time_steps = range(0, 10)
       domain_range = (0, 10, None, None, 10, 20) # (k1, k2, j1, j2, i1, i2)
       var_data_parallel = mytools.get_var_parallel("th", time_steps, domain_range=domain_range, cores=4)

3. **Parallelize Function in Time**

   For faster processing of data over multiple time steps, use ``get_var_parallel``:

   .. code-block:: python

       def user_define_function(t):
           # some complex analysis
           return # some results

       time_steps = range(0, 10)
       var_data_parallel = mytools.func_time_parallel(user_define_function, time_steps=time_steps, cores=4)



Debugging
---------

Enable debugging by setting ``debug_mode=True`` when initializing ``VVMTools``. This will provide detailed logging to help trace errors and issues.

.. code-block:: python

    import vvmtools
    vvm_tools = vvmtools.analyze.DataRetriever(case_path, debug_mode=True)

This will display warnings, errors, and status information during execution.
