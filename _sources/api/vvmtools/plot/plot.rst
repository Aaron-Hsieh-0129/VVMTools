plot module
====================

.. autoclass:: vvmtools.plot.DataPlotter
    :exclude-members: draw_xt, draw_zt

Attributes
----------

.. autosummary:: 
   :toctree: attribute
   :nosignatures:

- **EXP**: Experiment name or identifier, used to label plots.
- **FIGPATH**: Path for saving generated figures.
- **DOMAIN**: Dictionary with data arrays for plotting dimensions (`'x'`, `'y'`, `'z'`, and `'t'`).
- **DOMAIN_UNITS**: Dictionary defining units for each axis.
- **CUSTOM_TIME_FMT**: Custom time format for labels on the time axis.
- **DOMAIN_TICKS**: Dictionary with default or user-specified tick locations for each axis.



Methods
-------

.. autosummary::
   :toctree: generated

   vvmtools.plot.DataPlotter.draw_xt
   vvmtools.plot.DataPlotter.draw_zt
