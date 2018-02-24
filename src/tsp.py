#planning with traveling salesman problem algorithm from OR-tools

import pandas as pd
from geopy.distance import vincenty
from ortools.constraint_solver import pywrapcp

DIST_FACTOR = 100 #needs to compute distances as integers

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

    # solve
    assignment = routing.SolveWithParameters(search_parameters)
    # Solution cost.
    if assignment:
        print("Total distance: " + str(assignment.ObjectiveValue()/DIST_FACTOR) + " km\n")

        route_number = 0
        index = routing.Start(route_number) # Index of the variable for the starting node.
        route = ''
        indulgence_val = 0
        while not routing.IsEnd(index):
            # Convert variable indices to node indices in the displayed route.
            route += str(dat_loc['placenamefrench'][routing.IndexToNode(index)]) + ' -> '
            indulgence_val += dat_loc['indulgenceamounttotal_indays'][routing.IndexToNode(index)]
            index = assignment.Value(routing.NextVar(index))
        route += str(dat_loc['placenamefrench'][routing.IndexToNode(index)])
        print("Route:\n\n" + route)
        print("Total indulgence: {} days ".format(indulgence_val))
    else:
        print("no solution found")

if __name__=="__main__":
    run()
