#opening data and extracting information.

import pandas as pd
from geopy.distance import vincenty
import itertools as it
import networkx as nx
import matplotlib
matplotlib.use('tkAgg')
import matplotlib.pyplot as plt

dataloc = "../data/pardouns_dacre_locales.csv"

dat = pd.read_csv(dataloc)

#extracting columns
dat_loc = dat[['placenamefrench','indulgenceamounttotal_indays', 'latitude', 'longitude']]

num_sites = dat_loc.shape[0]

#distance between every pair of sites
#NOTE: not using street ('manhattan distance') dist
distances = {} #dictionary containing pairs

for site1, site2 in it.combinations(range(num_sites), 2):
    site1_latlong = (dat_loc['latitude'][site1], dat_loc['longitude'][site1])
    site2_latlong = (dat_loc['latitude'][site2], dat_loc['longitude'][site2])
    #using vincenty distance
    dist = vincenty(site1_latlong, site2_latlong).km
    print("dist between {} and {}: {}".format(dat_loc['placenamefrench'][site1],dat_loc['placenamefrench'][site2], dist))
    distances[(site1, site2)] = dist

#build node- and edge- weighted graph.

graph = nx.Graph()

for site in range(num_sites):
    graph.add_node(site, name=dat_loc['placenamefrench'][site], weight=dat_loc['indulgenceamounttotal_indays'][site])

#adding all edges - need to filter edge set down to nearest adjacent sites

for pair, dist in distances.items():
    graph.add_edge(*pair, weight=dist)

#drawing
plt.figure()
nx.draw(graph, with_labels=True, font_weight='bold')
plt.show()
