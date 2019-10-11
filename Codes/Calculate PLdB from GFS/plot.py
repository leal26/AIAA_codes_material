import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import pickle
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import copy
import random
from weather import makeFloats
from noaa import process

def contour(data, levels=None, label="Perceived Loudness, PLdB",
            index_altitude=None, cmap=cm.coolwarm, scatter = None):
    matplotlib.use('TkAgg')
    lon, lat, z = data.T

    numcols, numrows = len(set(lon)), len(set(lat))

    fig = plt.figure(figsize=(12, 6))

    # bounds = np.arange(0,110,10) - FIXME to match output
    m = Basemap(projection='merc', llcrnrlat=13, urcrnrlat=58,
                llcrnrlon=-144, urcrnrlon=-53, resolution='c')
    map_lon, map_lat = m(*(lon, lat))

    m.drawstates()
    m.drawcountries(linewidth=1.0)
    m.drawcoastlines()

    # target grid to interpolate to
    xi = np.linspace(map_lon.min(), map_lon.max(), numcols)
    yi = np.linspace(map_lat.min(), map_lat.max(), numrows)
    xi, yi = np.meshgrid(xi, yi)
    # interpolate
    try:
        if index_altitude is None:
            zi = griddata((map_lon, map_lat), z, (xi, yi), method='linear')
        else:
            # z = z.T[index_altitude, ]
            z_altitude = []
            for i in range(len(z)):
                z_altitude.append(z[i][index_altitude][1])
            z_altitude = np.array(z_altitude)
            zi = griddata((map_lon, map_lat), z_altitude, (xi, yi),
                          method='linear')
    except(ValueError):
        print('For weather z is a function of altitude. Choose index' +
              'for altitude (pressure) of interest.')

    # contour plot
    if levels is None:
        m.contourf(xi, yi, zi, cmap=cmap)
    else:
        m.contourf(xi, yi, zi, cmap=cmap, levels=levels)
    cbar = m.colorbar()
    if scatter is not None:
        map_lon, map_lat = m(*scatter)
        plt.scatter(map_lon[0], map_lat[0], marker='o',c='k')
        plt.scatter(map_lon[1], map_lat[1], marker='s',c='k')
    # colorbar

    degree_sign = '\N{DEGREE SIGN}'
    cbar.set_label(label)


day = '21'
month = '06'
year = '2018'
hour = '12'
altitude = '50000'

filename = "./" + year + month + day + '_' + '00' + '_'+ altitude + '.p'
data = pickle.load(open(filename, 'rb'))
data = np.array([data.lonlat[:,0], data.lonlat[:,1], data.noise]).T
contour(data)
plt.show()
