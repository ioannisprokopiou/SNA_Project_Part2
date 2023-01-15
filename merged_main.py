import networkx as nx
import pickle
import pandas as pd
import math
from cdlib import algorithms, readwrite
from tqdm import tqdm

# Read the first Graph and start looping from the 2nd day (Graph_01)
first_file = 'day_graphs/'+'Graph_0'
prev_G = pickle.load(open(first_file, 'rb'))

# Assign 1 to every edge weight
# This will be used to count how many times an edge had appeared
for e in prev_G.edges():
    prev_G[e[0]][e[1]]['weight'] = 1

# Loop all the Graphs to combine them to 1
for i in tqdm(range(1, 63)):
    file = 'day_graphs/'+'Graph_'+str(i)

    G = pickle.load(open(file, 'rb'))

    for e in G.edges():
        G[e[0]][e[1]]['weight'] = 1

    # Every time we combine the new Graph we read with the output of the previous loop
    # Meaning all the eprevious Graphs that have been combined (except the first loop when the previous Graph is Graph_0)
    G = nx.compose(G, prev_G)

    # Add the weights and assign them to the new combined Graph
    edge_data = {e: G.edges[e]['weight'] + prev_G.edges[e]
                 ['weight'] for e in G.edges & prev_G.edges}
    nx.set_edge_attributes(G, edge_data, 'weight')

    # Assign the newly combined Graph to the Previous graph for the next iteration
    # G variable will be overwritten in the next loop
    prev_G = G

# Add the attributes to the final combined Graph
attributes = pickle.load(open('node_attributes', 'rb'))
nx.set_node_attributes(G, attributes)

# Export to .GEXF for visualization purposes
nx.write_gexf(G, 'composed_graph.gexf')

# Remove nodes without the 'party' attribute
# If a node doesn't have the party attribute, it doesn't have any other
# attribute choice doesn't affect the result
nodes_with_no_attrs = []

for n in G.nodes:
    try:
        party = G.nodes[n]['party']
    except KeyError:
        nodes_with_no_attrs.append(n)

for n in nodes_with_no_attrs:
    G.remove_node(n)

# Find communities and export the to a .csv file
coms = algorithms.louvain(G, resolution=1.0)
readwrite.write_community_csv(
    coms, "Communities/communities_composed_graph.csv", ",")
# TODO: Find a way to skip the file creation
coms_df = pd.read_csv(
    "Communities/communities_composed_graph.csv", header=None)

# Create a dictionary to in order to set it as an attribute with the name "Community"
communities = {}

for index, row in coms_df.iterrows():
    for i in range(0, len(row)):
        if not math.isnan(row[i]):
            communities[int(row[i])] = index

nx.set_node_attributes(G, communities, name="Community")

# Init output dataframe
graph_data = pd.DataFrame(columns=['Node', 'Party', 'Modularity Class', 'Degree',
                                   'Left Percentage', 'Right Percentage', 'Middle Percentage', 'Neutral Percentage'])

# Loop the Combined Graph nodes to calculate the weighted percentages of the neighbors' parties
for n in tqdm(G.nodes()):

    left_neighbors = 0
    right_neighbors = 0
    middle_neighbors = 0
    neutral_neighbors = 0

    neighbors = G.neighbors(n)

    for ne in neighbors:

        ne_party = G.nodes[ne]['party']

        # Add all the weights per party
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

        # Calculate the percentage of the weights and not the percentage of nodes
        if total_parties != 0:
            left_perc = left_neighbors/total_parties
            right_perc = right_neighbors/total_parties
            middle_perc = middle_neighbors/total_parties
            neutral_perc = neutral_neighbors/total_parties

    graph_data.loc[len(graph_data)] = [n, G.nodes[n]['party'], G.nodes[n]['Community'],
                                       G.degree[n], left_perc, right_perc, middle_perc, neutral_perc]

graph_data.to_csv(f'CSV outputs/composed_graph.csv', index=False)
