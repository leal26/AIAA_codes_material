import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.basemap import Basemap
def process(filename):
    data = loadmat(filename, struct_as_record=False)['s'][0][0]
    data.height = data.height[0] * 0.3048  # Convert to meters
    data.temperature = data.temperature[0]
    data.wind_x = data.wind_x[0]
    data.wind_y = data.wind_y[0]
    data.humidity = data.humidity[0]
    data.pressure = data.pressure[0, 0]
    data.lon = data.lon[0]
    data.lat = data.lat[0]
    data.elevation = 10.**5/2.5577*(1-(data.pressure[:, :]/101325)**(1/5.2558)) / 0.3048
    return data

year = '2018'
month = '06'
day = '18'
hour = '12'
filename = year + month + day + '_' + hour + '.mat'

index_altitude = 0
data = process(filename)
pickle.dump(open(filename = year + month + day + '_' + hour + '.p'), 'wb')
pickle.close()
print(data.lon.shape, data.lat.shape, data.humidity.shape)

# Plotting
from mpl_toolkits.basemap import Basemap
fig = plt.figure(figsize=(12, 6))
m = Basemap(projection='merc', llcrnrlat=13, urcrnrlat=58,
            llcrnrlon=-144, urcrnrlon=-53, resolution='c')
map_lon, map_lat = m(*(data.lon, data.lat))
m.drawstates()
m.drawcountries(linewidth=1.0)
m.drawcoastlines()
print(min(data.humidity[index_altitude, :, :].ravel()),
      max(data.humidity[index_altitude, :, :].ravel()))
plt.contourf(map_lon, map_lat, data.humidity[index_altitude, :, :],
             cmap=cm.coolwarm)

cbar = m.colorbar()
degree_sign = '\N{DEGREE SIGN}'
label = "Relative Humidity"
cbar.set_label(label)
plt.show()
