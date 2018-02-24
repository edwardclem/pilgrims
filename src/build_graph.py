#opening data and extracting information.

import pandas as pd
from geopy.distance import vincenty
import itertools as it
import networkx as nx
import matplotlib
matplotlib.use('tkAgg')
import matplotlib.pyplot as plt
from operator import itemgetter


#TODO: probably a better way to do this? Maybe you don't even want to?
#TODO: edge weight filtering 
def filter_graph(graph, num_closest = 5):
    '''
    Removing all but the num_closest lowest weight edges for each node.
    '''

    filtered = nx.Graph()

    #add all nodes from the graph.

    filtered.add_nodes_from(graph.nodes(data=True))

    for n, nbrs in graph.adj.items():
        adj_edges = [(n, nbr, eattr['weight']) for (nbr, eattr) in nbrs.items()]
        sorted_edges = sorted(adj_edges, key=itemgetter(2))
        top_five = sorted_edges[:num_closest]
        filtered.add_weighted_edges_from(top_five)

    return filtered

def save_graph_map(graph, outfile, offset=0.0002):
    '''
    Draws the graph map.
    '''

    pos=nx.get_node_attributes(filtered,'pos')
    names = nx.get_node_attributes(filtered,'name')
    indulgence = nx.get_node_attributes(filtered, 'weight')
    dists = nx.get_edge_attributes(filtered, 'weight')

    dists_trunc = dict([(edge, "{} km".format(round(weight, 3))) for edge, weight in dists.items()])
    indulgence_labeled = dict([(node, "{} days".format(days)) for node, days in indulgence.items()])

    #introducing offset
    name_pos = dict([(node, (pos[0], pos[1] + offset)) for node, pos in pos.items()])
    indulgence_pos = dict([(node, (pos[0], pos[1] - offset)) for node, pos in pos.items()])

    plt.figure(figsize=(30,30))
    plt.title("digital humanities af")
    nx.draw_networkx_nodes(filtered, pos, font_weight='bold')
    nx.draw_networkx_labels(filtered, name_pos, names)
    nx.draw_networkx_labels(filtered, indulgence_pos, indulgence_labeled)
    nx.draw_networkx_edges(filtered, pos)
    nx.draw_networkx_edge_labels(filtered, pos, dists_trunc)
    plt.savefig(outfile)

dataloc = "../data/pardouns_dacre_locales.csv"

dat = pd.read_csv(dataloc)

#extracting columns
dat_loc = dat[['placenamefrench','indulgenceamounttotal_indays', 'latitude', 'longitude']]

num_sites = dat_loc.shape[0]

#distance between every pair of sites
#NOTE: not using street ('manhattan distance') dist
distances = [] #list containing (site1, site2, weight) tuples

for site1, site2 in it.combinations(range(num_sites), 2):
    site1_latlong = (dat_loc['latitude'][site1], dat_loc['longitude'][site1])
    site2_latlong = (dat_loc['latitude'][site2], dat_loc['longitude'][site2])
    #using vincenty distance
    dist = vincenty(site1_latlong, site2_latlong).km
    #print("dist between {} and {}: {}".format(dat_loc['placenamefrench'][site1],dat_loc['placenamefrench'][site2], dist))
    distances.append((site1, site2, dist))

#build node- and edge- weighted graph.

graph_complete = nx.Graph()

for site in range(num_sites):
    #NOTE: using latitude and longitude coordinates for position.
    graph_complete.add_node(site, pos=(dat_loc['latitude'][site], dat_loc['longitude'][site]), name=dat_loc['placenamefrench'][site], weight=dat_loc['indulgenceamounttotal_indays'][site])

#adding all edges - need to filter edge set down to nearest adjacent sites
graph_complete.add_weighted_edges_from(distances)

filtered = filter_graph(graph_complete)

save_graph_map(filtered, '../processed/acre_edge_filtered_5.png')

#saving graph

nx.write_gpickle(filtered, '../processed/acre_edge_filtered_5.pkl')
