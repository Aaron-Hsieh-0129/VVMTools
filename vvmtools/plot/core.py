import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import os, sys
import logging

class DataPlotter:
    """
    The DataPlotter class provides methods for creating and saving visualizations of scientific data
    across spatial and temporal dimensions.

    This class enables users to configure plotting attributes, including axis data, units, and custom tick
    locations, while offering utilities for automatically setting up figure paths and managing plot layouts.
    Custom color maps, label formatting, and title settings can be applied to generated plots for clear 
    and detailed data presentation.

    :param exp: Experiment name or identifier for labeling the plots.
    :type exp: str
    :param figpath: Directory path where generated figures will be saved. If the directory does not exist, 
                    it is created automatically.
    :type figpath: str
    :param domain: Dictionary containing data arrays for plotting dimensions, with keys `'x'`, `'y'`, `'z'`, and `'t'`.
                   `np.array` values are expected for spatial axes and `np.datetime64` for time (`'t'`).
    :type domain: dict
    :param units: Dictionary defining the units of each axis, with keys `'x'`, `'y'`, `'z'`, and `'t'`. 
                  The values are strings specifying the units displayed on axis labels.
    :type units: dict
    :param ticks: Custom tick locations for each axis, with keys `'x'`, `'y'`, `'z'`, and `'t'`. If not provided,
                  default tick settings are used.
    :type ticks: dict, optional
    :param time_fmt: Format for displaying labels on the time axis. Default is `'%H'`, for displaying hours 
                     in 24-hour format.
    :type time_fmt: str, optional

    Examples
    --------
    ::

        import numpy as np
        from vvmtools.plot import DataPlotter
        
        # prepare expname and data coordinate
        expname  = 'pbl_control'
        nx = 128; x = np.arange(nx)*0.2
        ny = 128; y = np.arange(ny)*0.2
        nz = 50;  z = np.arange(nz)*0.04
        nt = 721; t = np.arange(nt)*np.timedelta64(2,'m')+np.datetime64('2024-01-01 05:00:00')
        
        # create dataPlotter class
        figpath           = './fig/'
        data_domain       = {'x':x, 'y':y, 'z':z, 't':t}
        data_domain_units = {'x':'km', 'y':'km', 'z':'km', 't':'LocalTime'}
        dplot = DataPlotter(expname, figpath, data_domain, data_domain_units)

    """
    def __init__(self, exp, figpath, domain, units, ticks=None, time_fmt='%H'):
        self.EXP              = exp
        self.FIGPATH          = figpath
        self.DOMAIN           = domain
        self.DOMAIN_UNITS     = units
        self.CUSTOM_TIME_FMT  = time_fmt
        self.DOMAIN_TICKS = self._default_dim_ticks(ticks)

        self._check_create_figpath()

    def _default_dim_ticks(self, ticks_in):
        ticks = ticks_in or {'x':None, 'y':None, 'z':None, 't':None}
        dim_ticks = {}
        for key, value in ticks.items():
            dim_ticks[key] = value or self._get_clear_ticks( ax_name = key )
        return dim_ticks

    def _check_create_figpath(self):
        if not os.path.isdir(self.FIGPATH):
            print(f'create fig folder ... {self.FIGPATH}')
            os.system(f'mkdir -p {self.FIGPATH}')

    def _default_setting(self):
        plt.rcParams.update({'font.size':17,
                             'axes.linewidth':2,
                             'lines.linewidth':2})

    def _create_figure(self, figsize):
        self._default_setting()
        fig     = plt.figure(figsize=figsize)
        if figsize[0] / figsize[1] >= 1:
            ax      = fig.add_axes([0.1,0.1,0.77,0.8])
            cax     = fig.add_axes([0.9,0.1,0.02,0.8])
        else:
            ax      = fig.add_axes([0.15,  0.1, 0.7, 0.8])
            cax     = fig.add_axes([0.88, 0.1, 0.03, 0.8])
        return fig, ax, cax

    def _get_cmap(self, cmap_name='jet'):
        if cmap_name=='':
            # define custom colormap
            pass
        else:
           cmap = mpl.pyplot.get_cmap(cmap_name)
        return cmap

    def _get_clear_ticks(self, ax_name, ax_lim=None):
        # subdomain default ticks
        lim = ax_lim or (self.DOMAIN[ax_name].min(), self.DOMAIN[ax_name].max())
        if ax_name=='t':
            #align with hourly location
            length=(lim[1] - lim[0])

            if length  // np.timedelta64(1,'D') > 1:
              self.TIME_FMT = '%D'
              delta = np.timedelta64(1,'D') 
              left = (lim[0]-np.timedelta64(1,'s')).astype('datetime64[D]')
            elif length  // np.timedelta64(1,'h') > 12:
              self.TIME_FMT = '%H'
              delta = np.timedelta64(3,'h') 
              left = (lim[0]-np.timedelta64(0,'s')).astype('datetime64[h]')
            elif length  // np.timedelta64(1,'h') > 1:
              self.TIME_FMT = '%H'
              delta = np.timedelta64(1,'h') 
              left = (lim[0]-np.timedelta64(1,'s')).astype('datetime64[h]')
            else :
              self.TIME_FMT = '%H:%M'
              delta = np.timedelta64(10,'m')
              mn = int(lim[0].astype(str)[11:19].split(':')[-1])
              left = (lim[0] - np.timedelta64(mn%10,'m'))
            
            ticks=np.arange(left,left+length+delta*2, delta)
        elif ax_name=='z':
            nticks = 11
            length = (lim[1]-lim[0])
            interval = length / (nticks - 1)
            if interval >= 1e-3:
              interval = np.round(interval,2)
            ticks = np.arange(lim[0],lim[1]+interval,interval)
        else:
            nticks = 5
            ticks = np.linspace(lim[0], lim[1], nticks)
        return ticks
 

    def _determine_ticks_and_lim(self, ax_name, ax_lim):
        if type(ax_lim) == type(None):
            # use the ticks and limit in class setting
            self.TIME_FMT = self.CUSTOM_TIME_FMT
            lim   = (self.DOMAIN[ax_name].min(), self.DOMAIN[ax_name].max())
            ticks = self.DOMAIN_TICKS[ax_name]
        else:
            lim   = ax_lim
            ticks = self._get_clear_ticks(ax_name, ax_lim)

        return  lim, ticks

    def draw_xt(self, data, \
                      levels, \
                      extend, \
                      x_axis_dim = 'x',\
                      cmap_name='bwr', \
                      title_left = '', \
                      title_right = '', \
                      xlim = None, \
                      ylim = None,\
                      figname='',\
               ):

        """
        This function creates a x-t plot for a 2D data over spatial (x or y) and temporal (t) dimensions. 

        :param data: 2D array (t,x) of data values to be plotted, with dimensions corresponding to the time and 
                     `x_axis_dim` axes in `DOMAIN`.
        :type data: numpy.ndarray
        :param levels: Discrete boundaries for color intervals, used for normalizing the color mapping of data values.
        :type levels: list or numpy.ndarray
        :param extend: Specifies color bar extension behavior at the boundaries; can be one of `'both'`, 
                       `'min'`, or `'max'`.
        :type extend: str
        :param x_axis_dim: The spatial dimension to plot on the x-axis, `'x'` or `'y'` (default is `'x'`).
        :type x_axis_dim: str, optional
        :param cmap_name: The name of the colormap to use (default is `'bwr'` for blue-white-red) same as matplotlib.
        :type cmap_name: str, optional
        :param title_left: Title text to display on the left side of the plot.
        :type title_left: str, optional
        :param title_right: Title text to display on the right side of the plot. The `'EXPNAME'` will add in second line.
        :type title_right: str, optional
        :param xlim: Tuple specifying the minimum and maximum limits for the x-axis. If None, the limits are derived 
                     from `DOMAIN`.
        :type xlim: tuple, optional
        :param ylim: Tuple specifying the minimum and maximum limits for the y-axis (time). If None, the limits are derived 
                     from `DOMAIN`.
        :type ylim: tuple, optional
        :param figname: Filename to save the plot. If not provided, the plot is not saved.
        :type figname: str, optional

        :return: The generated figure (`fig`), main axis (`ax`), and color bar axis (`cax`) objects.
        :rtype: tuple(matplotlib.figure.Figure, matplotlib.axes.Axes, matplotlib.axes.Axes)


        Examples
        --------
        Initialize the `DataPlotter` Classes
        ::

            import numpy as np
            from vvmtools.plot import DataPlotter
            import matplotlib.pyplot as plt
           
            # prepare expname and data coordinate
            expname  = 'pbl_control'
            nx = 128; x = np.arange(nx)*0.2
            ny = 128; y = np.arange(ny)*0.2
            nz = 50;  z = np.arange(nz)*0.04
            nt = 721; t = np.arange(nt)*np.timedelta64(2,'m')+np.datetime64('2024-01-01 05:00:00')
           
            # create dataPlotter class
            figpath           = './fig/'
            data_domain       = {'x':x, 'y':y, 'z':z, 't':t}
            data_domain_units = {'x':'km', 'y':'km', 'z':'km', 't':'LocalTime'}
            dplot = DataPlotter(expname, figpath, data_domain, data_domain_units)

        Create the 2d data.
        ::

            np.random.seed(0)
            data_xt2d  = np.random.normal(0, 0.1, size=(nt,nx))

        draw x-t diagram.
        ::

            fig, ax, cax = dplot.draw_xt(data = data_xt2d,
                                            levels = np.arange(-1,1.001,0.1),
                                            extend = 'both',
                                            title_left  = 'draw_xt hov example',
                                            title_right = f'right_land_type',
                                            figname     = 'test_hov.png',
                                           )
            plt.show()

        .. figure:: /api/vvmtools/plot/_images/dataPlotter_draw_xt.png
            :scale: 30%
            :class: with-border

        draw x-t diagram with optional configuration.
        ::

            fig, ax, cax = dplot.draw_xt(data = data_xt2d,
                                            levels = np.arange(-1,1.001,0.1), 
                                            extend = 'both',
                                            x_axis_dim  = 'y',
                                            cmap_name   = 'Spectral',
                                            xlim        = (6.4, 19.2),
                                            ylim        = (np.datetime64('2024-01-01 09:00:00'),
                                                           np.datetime64('2024-01-01 17:00:00')
                                                          ),
                                            title_left  = 'draw_xt (optional)',
                                            title_right = f'right_land_type',
                                            figname     = ''
                                           )
            plt.show()

        .. figure:: /api/vvmtools/plot/_images/dataPlotter_draw_xt_optional.png
            :scale: 30%
            :class: with-border

        """

        xlim, xticks = self._determine_ticks_and_lim(ax_name=x_axis_dim, ax_lim=xlim)
        ylim, yticks = self._determine_ticks_and_lim(ax_name='t', ax_lim=ylim)

        fig, ax, cax = self._create_figure(figsize=(8,10))
        plt.sca(ax)
        cmap = self._get_cmap(cmap_name)
        norm = mpl.colors.BoundaryNorm(boundaries=levels, \
                  ncolors=256, extend=extend)
        PO = plt.pcolormesh(self.DOMAIN[x_axis_dim], self.DOMAIN['t'], data, \
                       cmap=cmap, norm=norm, \
                      )
        CB = plt.colorbar(PO, cax=cax)
        plt.xticks(xticks)
        plt.yticks(yticks)
        ax.yaxis.set_major_formatter(mpl.dates.DateFormatter(self.TIME_FMT))
        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.ylabel(f'time [{self.DOMAIN_UNITS["t"]}]')
        plt.xlabel(f'{x_axis_dim} [{self.DOMAIN_UNITS[x_axis_dim]}]')
        plt.grid()
        plt.title(f'{title_right}\n{self.EXP}', loc='right', fontsize=15)
        plt.title(f'{title_left}', loc='left', fontsize=20, fontweight='bold')
        if len(figname)>0:
            plt.savefig(f'{self.FIGPATH}/{figname}', dpi=200)
        return fig, ax, cax

    def draw_zt(self, data, \
                      levels, \
                      extend, \
                      pblh_dicts={},\
                      cmap_name='bwr',\
                      title_left = '', \
                      title_right = '', \
                      xlim = None, \
                      ylim = None,\
                      figname='',\
               ):
        """
        This function creates a z-t plot for a specified variable over time and height dimensions. and draw a series pbl height 1-D datasets.

        :param data: 2D array (nz,nt) of data values to plot, with dimensions corresponding to time ('t') and height ('z') axes.
        :type data: np.ndarray
        :param levels: Sequence of boundaries to use for color normalization.
        :type levels: list or np.ndarray
        :param extend: Controls the color scaling at the boundaries. Accepts 'both', 'neither', 'min', or 'max' to adjust color mapping.
        :type extend: str
        :param pblh_dicts: Dictionary of planetary boundary layer height data with labels as keys and height values as arrays (nt). Optional.
        :type pblh_dicts: dict, optional
        :param cmap_name: Name of the colormap for the plot. Defaults to 'bwr'.
        :type cmap_name: str, optional
        :param title_left: Title text displayed at the left of the plot.
        :type title_left: str, optional
        :param title_right: Title text displayed at the right of the plot.
        :type title_right: str, optional
        :param xlim: Limits for the x-axis (time), specified as a tuple (start, end). Defaults to None, which uses the full domain range.
        :type xlim: tuple, optional
        :param ylim: Limits for the y-axis (height), specified as a tuple (start, end). Defaults to None, which uses the full domain range.
        :type ylim: tuple, optional
        :param figname: File name for saving the generated plot. If left empty, the plot will not be saved.
        :type figname: str, optional
    
        :return: The figure, main axis, and colorbar axis of the created plot.
        :rtype: tuple (matplotlib.figure.Figure, matplotlib.axes._axes.Axes, matplotlib.colorbar.Colorbar)

        Examples
        --------
        Initialize the `DataPlotter` Classes
        ::

            import numpy as np
            from vvmtools.plot import DataPlotter
            import matplotlib.pyplot as plt
            
            # prepare expname and data coordinate
            expname  = 'pbl_control'
            nx = 128; x = np.arange(nx)*0.2
            ny = 128; y = np.arange(ny)*0.2
            nz = 50;  z = np.arange(nz)*0.04
            nt = 721; t = np.arange(nt)*np.timedelta64(2,'m')+np.datetime64('2024-01-01 05:00:00')
            
            # create dataPlotter class
            figpath           = './fig/'
            data_domain       = {'x':x, 'y':y, 'z':z, 't':t}
            data_domain_units = {'x':'km', 'y':'km', 'z':'km', 't':'LocalTime'}
            dplot = DataPlotter(expname, figpath, data_domain, data_domain_units)

        Create the 2d data.
        ::

            np.random.seed(0)
            data_zt2d  = np.random.normal(0, 0.1, size=(nz,nt))
            line1_1d = np.sin( np.linspace(0, 2*np.pi, nt) ) +1
            line2_1d = np.cos( np.linspace(0, 2*np.pi, nt) ) +1

        draw z-t diagram.
        ::

            fig, ax, cax = dplot.draw_zt(data = data_zt2d, 
                                         levels = np.arange(-1,1.001,0.1), 
                                         extend = 'both', 
                                         pblh_dicts={'line1': line1_1d,
                                                     'line2': line2_1d,
                                                    },
                                         title_left  = 'draw_zt pblh example', 
                                         title_right = f'right_land_type', 
                                         figname     = 'test_pbl.png',
                                  )
           
            plt.show()

        .. figure:: /api/vvmtools/plot/_images/dataPlotter_draw_zt.png
            :scale: 30%
            :class: with-border

        draw z-t diagram with optional configuration.
        ::

            fig, ax, cax = dplot.draw_zt(data = data_zt2d, 
                                         levels = np.arange(-1,1.001,0.1), 
                                         extend = 'both', 
                                         pblh_dicts={'line1': line1_1d,
                                                     'line2': line2_1d,
                                                    },
                                         cmap_name   = 'Spectral',
                                         xlim        = (np.datetime64('2024-01-01 09:00:00'),
                                                        np.datetime64('2024-01-01 17:00:00')
                                                       ),
                                         ylim        = (0, 1),
                                         title_left  = 'draw_zt (optional)', 
                                         title_right = f'right_land_type', 
                                         figname     = '',
                                  )
           
            plt.show()

        .. figure:: /api/vvmtools/plot/_images/dataPlotter_draw_zt_optional.png
            :scale: 30%
            :class: with-border

        """

        xlim, xticks = self._determine_ticks_and_lim(ax_name='t', ax_lim=xlim)
        ylim, yticks = self._determine_ticks_and_lim(ax_name='z', ax_lim=ylim)

        fig, ax, cax = self._create_figure(figsize=(10,6))
        plt.sca(ax)
        cmap = self._get_cmap(cmap_name)
        norm = mpl.colors.BoundaryNorm(boundaries=levels, \
                  ncolors=256, extend=extend)
        PO = plt.pcolormesh(self.DOMAIN['t'], self.DOMAIN['z'], data, \
                       cmap=cmap, norm=norm, \
                      )
        CB = plt.colorbar(PO, cax=cax)
        if (len(pblh_dicts) > 0):
            for key, value in pblh_dicts.items():
                plt.scatter(self.DOMAIN['t'], value, s=10, label=key, zorder=10)
            LGD = plt.legend()
        plt.xticks(xticks)
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter(self.TIME_FMT))
        plt.yticks(yticks)
        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.xlabel(f'time [{self.DOMAIN_UNITS["t"]}]')
        plt.ylabel(f'z [{self.DOMAIN_UNITS["z"]}]')
        plt.grid()
        plt.title(f'{title_right}\n{self.EXP}', loc='right', fontsize=15)
        plt.title(f'{title_left}', loc='left', fontsize=20, fontweight='bold')
        if len(figname)>0:
            plt.savefig(f'{self.FIGPATH}/{figname}', dpi=200)
        return fig, ax, cax

