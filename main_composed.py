import networkx as nx
import pickle
import pandas as pd
import math
from cdlib import algorithms, readwrite


attributes = pickle.load(open('node_attributes', 'rb'))

G = nx.read_gexf('composed_graph.gexf')

nodes_with_no_attrs = []

for n in G.nodes:
    try:
        party = G.nodes[n]['party']
    except KeyError:
        nodes_with_no_attrs.append(n)

for n in nodes_with_no_attrs:
    G.remove_node(n)

coms = algorithms.louvain(G, resolution=1.0)
readwrite.write_community_csv(
    coms, "Communities/communities_composed_graph.csv", ",")
coms_df = pd.read_csv(
    "Communities/communities_composed_graph.csv", header=None)

communities = {}

for index, row in coms_df.iterrows():
    for i in range(0, len(row)):
        if not math.isnan(row[i]):
            communities[str(int(row[i]))] = index

nx.set_node_attributes(G, communities, name="Community")


graph_data = pd.DataFrame(columns=['Node', 'Party', 'Modularity Class', 'Degree',
                                   'Left Percentage', 'Right Percentage', 'Middle Percentage', 'Neutral Percentage'])

for n in G.nodes():

    left_neighbors = 0
    right_neighbors = 0
    middle_neighbors = 0
    neutral_neighbors = 0

    neighbors = G.neighbors(n)

    for ne in neighbors:

        ne_party = G.nodes[ne]['party']

        if ne_party == 'left':
            try:
                left_neighbors += G[n][ne]['weight']
            except KeyError:
                left_neighbors += G[ne][n]['weight']
        elif ne_party == 'right':
            try:
                right_neighbors += G[n][ne]['weight']
            except KeyError:
                right_neighbors += G[ne][n]['weight']
        elif ne_party == 'middle':
            try:
                middle_neighbors += G[n][ne]['weight']
            except KeyError:
                middle_neighbors += G[ne][n]['weight']
        elif ne_party == 'neutral':
            try:
                neutral_neighbors += G[n][ne]['weight']
            except KeyError:
                neutral_neighbors += G[ne][n]['weight']

        total_parties = left_neighbors+right_neighbors+middle_neighbors+neutral_neighbors

        if total_parties != 0:
            left_perc = left_neighbors/total_parties
            right_perc = right_neighbors/total_parties
            middle_perc = middle_neighbors/total_parties
            neutral_perc = neutral_neighbors/total_parties
            # print(n)
        else:
            print(n, left_neighbors, right_neighbors,
                  middle_neighbors, neutral_neighbors)

    graph_data.loc[len(graph_data)] = [n, party, G.nodes[n]['Community'],
                                       G.degree[n], left_perc, right_perc, middle_perc, neutral_perc]

graph_data.to_csv(f'CSV outputs/composed_graph.csv', index=False)
