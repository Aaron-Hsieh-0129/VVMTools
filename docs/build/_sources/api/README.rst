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

Clone this repository and install the required dependencies:

.. code-block:: bash

    pip install xarray numpy

Usage
-----

Initialization
--------------

To initialize the ``VVMTools`` class, provide the path to the directory containing the case files. Optionally, enable ``debug_mode`` to log more detailed information:

.. code-block:: python

    from vvm_tools import VVMTools

    case_path = "/path/to/case/files"
    vvm_tools = VVMTools(case_path, debug_mode=True)

Example Operations
------------------

1. **Extract a Variable**

   To retrieve a variable at a specific time step, use the ``get_var`` method:

   .. code-block:: python

       var_data = vvm_tools.get_var("temperature", time=0, numpy=True)

2. **Parallel Data Extraction**

   For faster processing of data over multiple time steps, use ``get_var_parallel``:

   .. code-block:: python

       time_steps = range(0, 10)
       var_data_parallel = vvm_tools.get_var_parallel("temperature", time_steps, cores=4)


Debugging
---------

Enable debugging by setting ``debug_mode=True`` when initializing ``VVMTools``. This will provide detailed logging to help trace errors and issues.

.. code-block:: python

    vvm_tools = VVMTools(case_path, debug_mode=True)

This will display warnings, errors, and status information during execution.
