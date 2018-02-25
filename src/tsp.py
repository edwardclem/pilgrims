#planning with traveling salesman problem algorithm from OR-tools

import pandas as pd
from geopy.distance import vincenty
from ortools.constraint_solver import pywrapcp
import time

DIST_FACTOR = 100 #needs to compute distances as integers
MAX_PATH = 5 #in km

class CreateDistanceCallback(object):
    def __init__(self, data):
        self.data = data

    def Distance(self, site1, site2):
        site1_latlong = (self.data['latitude'][site1], self.data['longitude'][site1])
        site2_latlong = (self.data['latitude'][site2], self.data['longitude'][site2])
        dist = vincenty(site1_latlong, site2_latlong).km
        return int(dist*DIST_FACTOR)


def run():
    dataloc = "../data/pardouns_dacre_locales.csv"

    dat = pd.read_csv(dataloc)

    #extracting columns
    dat_loc = dat[['placenamefrench','indulgenceamounttotal_indays', 'latitude', 'longitude']]

    num_sites = dat_loc.shape[0]

    start = 0
    #create ORTools routing model
    routing = pywrapcp.RoutingModel(num_sites, 1, start)
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()

    dist_between_nodes = CreateDistanceCallback(dat_loc)
    dist_callback = dist_between_nodes.Distance
    routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)

    #create dimension/distance constraint\
    #TODO: scaling?
    #this is the easy way out - really want to maximize nodes collected with
    #path under a certain length
    #is that strictly a traveling salesman problem?

    routing.AddDimension(dist_callback, int(MAX_PATH*DIST_FACTOR), int(MAX_PATH*DIST_FACTOR), True, "distance")

    #add "prize", indulgence time
    #added to cost if not visited
    for node_ind in range(num_sites):
        routing.AddDisjunction([node_ind], int(dat_loc['indulgenceamounttotal_indays'][node_ind]))

    # solve
    assignment = routing.SolveWithParameters(search_parameters)
    # Solution cost.

    if assignment:
        print("Total cost (dist*SCALE_FACTOR + indulgence lost): " + str(assignment.ObjectiveValue()) + "\n")
        route_number = 0
        index = routing.Start(route_number) # Index of the variable for the starting node.
        route = ''
        indulgence_val = 0
        distance = 0
        while not routing.IsEnd(index):
            prev_node = routing.IndexToNode(index)
            # Convert variable indices to node indices in the displayed route.
            route += str(dat_loc['placenamefrench'][routing.IndexToNode(index)]) + ' -> '
            indulgence_val += dat_loc['indulgenceamounttotal_indays'][routing.IndexToNode(index)]
            index = assignment.Value(routing.NextVar(index))
            distance += dist_callback(routing.IndexToNode(index), prev_node)
        route += str(dat_loc['placenamefrench'][routing.IndexToNode(index)])
        print("Route:\n\n" + route)
        print("Total indulgence: {} days ".format(indulgence_val))
        #getting total distance
        # dist = routing.CumulVar(index, "distance")
        print("max distance allowed: {} km".format(MAX_PATH))
        print("total distance: {} km".format(distance/DIST_FACTOR))
    else:
        print("no solution found")

if __name__=="__main__":
    start = time.time()
    run()
    end = time.time()

    print("elapsed time: {}".format(end - start))
