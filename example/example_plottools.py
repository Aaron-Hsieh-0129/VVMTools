import numpy as np
from vvmtools.plot import DataPlotter
import matplotlib.pyplot as plt


# prepare expname and data coordinate
expname  = 'pbl_control'
nx = 128; x = np.arange(nx)*0.2
ny = 128; y = np.arange(ny)*0.2
nz = 50;  z = np.arange(nz)*0.04
nt = 721; t = np.arange(nt)*np.timedelta64(2,'m')+np.datetime64('2024-01-01 05:00:00')

# read or create data
data_zt2d  = np.random.normal(0, 0.1, size=(nz,nt))
data_xt2d  = np.random.normal(0, 0.1, size=(nt,nx))
line1_1d = np.sin( np.linspace(0, 2*np.pi, nt) ) +1
line2_1d = np.cos( np.linspace(0, 2*np.pi, nt) ) +1

# create dataPlotter class
figpath           = './fig/'
data_domain       = {'x':x, 'y':y, 'z':z, 't':t}
data_domain_units = {'x':'km', 'y':'km', 'z':'km', 't':'LocalTime'}
dplot = DataPlotter(expname, figpath, data_domain, data_domain_units)

# draw z-t diagram
# input data dimension is (nz, nt)
# [output] figure, axis, colorbar axis
fig, ax, cax = dplot.draw_zt(data = data_zt2d, \
                             levels = np.arange(-1,1.001,0.1), \
                             extend = 'both', \
                             pblh_dicts={'line1': line1_1d,\
                                         'line2': line2_1d,\
                                        },\
                             title_left  = 'draw_zt pblh example', \
                             title_right = f'right_land_type', \
                             figname     = 'test_pbl.png',\
                      )

# draw x-t diagram
# input data dimension is (nt, nx)
# [output] figure, axis, colorbar axis
fig2, ax2, cax2 = dplot.draw_xt(data = data_xt2d,\
                                levels = np.arange(-1,1.001,0.1), \
                                extend = 'both', \
                                title_left  = 'draw_xt hov example', \
                                title_right = f'right_land_type', \
                                figname     = 'test_hov.png',\
                               )
plt.show()

