import folium
import os
import json
import csv
import math

from collections import defaultdict

MAX_WALK_RANGE = 0.08  # km
WALK_SPEED = 5.0  # km
BUS_SPEED = 30.0  # km
MRT_SPEED = 80.0  # km

# Code to be called by GUI
# 33
"""
nodes={}
with open('exportBuilding.geojson') as access_json:
    read_content = json.load(access_json)
    feature_access = read_content['features']

    for feature_data in feature_access:
        buildingName = feature_data['properties']
        if 'name' in buildingName:
            retrieveHDB = buildingName['name']
            nodes[retrieveHDB]= find_midpoint(feature_data['geometry']['coordinates'])
        elif 'addr:housename' in buildingName and 'addr:housenumber' in buildingName:
            retrieveName = buildingName['addr:housename'] + " " + buildingName['addr:housenumber']
            nodes[retrieveName]= find_midpoint(feature_data['geometry']['coordinates'])

pathfinder = Dijkstra(nodes) 
pathfinder.create_edges()
graph = pathfinder.build_graph()
path = pathfinder.find_shortest_path(graph,"The Meadows 641C","The Meadows 641A")

"""
# 33


class Dijkstra:

    # constructor to recieve a dictionary of nodes. (key = string name, value = [lat,long])
    def __init__(self, nodes):
        self.nodes = nodes
        self.edges = []

    # to be called by gui to create edges
    def create_edges(self):
        for k1, v1 in self.nodes.items():
            for k2, v2 in self.nodes.items():
                edge = add_neighbour(k1, v1, k2, v2)
                if edge is not None:
                    self.edges.append(edge)

    # to be called by gui
    def build_graph(self):
        graph = defaultdict(list)
        seen_edges = defaultdict(int)
        for src, dst, weight, mode in self.edges:
            seen_edges[(src, dst, weight)] += 1
            if seen_edges[(src, dst, weight)] > 1:  # checking for duplicated edge entries
                continue
            graph[src].append([dst, weight, mode])
            # remove this line of edge list is directed
            graph[dst].append([src, weight, mode])

        return graph

    # function to be called by gui to find path from src to dst, returns a list of coordinates for plotting lines
    def find_shortest_path(self, graph, src, dst):
        d, prev = dijkstra(graph, src, dst)
        path = find_path(prev, [dst, 'walk'])
        path = [swap(self.nodes[x[0]]) for x in path]
        return path

# checks if it is a neighbour then return an edge , [src, dest,weight,modeoftravel]. Else return none


def add_neighbour(k1, v1, k2, v2):
    # If it is within walking distance then there is an edge between the 2 points
    distance = calc_distance(v1, v2)
    if distance < MAX_WALK_RANGE:
        return [k1, k2, distance, 'walk']

# to be called by gui after calling build graph


def dijkstra(graph, src, dst=None):
    nodes = []
    for n in graph:
        nodes.append(n)
        nodes += [x[0] for x in graph[n]]
    q = set(nodes)
    nodes = list(q)

    dist = dict()
    prev = dict()
    for n in nodes:
        dist[n] = float('inf')
        prev[n] = None

    dist[src] = 0

    while q:
        u = min(q, key=dist.get)
        q.remove(u)

        if dst is not None and u == dst:
            return dist[dst], prev

        for v, w, mode in graph.get(u, []):

            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = [u, mode]

    return dist, prev


def find_path(pr, node):  # generate path list based on parent points 'prev'
    p = []

    while node is not None:
        p.append(node)
        node = pr[node[0]]
    return p[::-1]


def swap(coord):
    return [coord[1], coord[0]]

# returns the midpoint of the polygon coordinates


def find_midpoint(L):
    lat = []
    long = []
    for l in L[0]:
        lat.append(l[0])
        long.append(l[1])

    return [sum(lat)/len(lat), sum(long)/len(long)]


# Recieves 2 list/tuple of coordinates, (srclat,srclong)(destLat,destLong), returns the distance between 2 points
def calc_distance(src, dest):
    lat1, lon1 = src
    lat2, lon2 = dest
    radius = 6371  # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d
