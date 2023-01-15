import networkx as nx
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import math
from cdlib import algorithms, readwrite
from collections import Counter
from tqdm import tqdm


def read_graph(file, attributes):
    """Read a Pickle Graph file and assign attributes

    Args:
        file: the pickle file that contains the graph
        attributes: the attributes file

    Returns:
        A NetworkX graph 
    """
    # Read Graph pickle
    G = pickle.load(open(file, 'rb'))

    # Set Node Attributes
    nx.set_node_attributes(G, attributes)

    return G


def produce_csv(G, graph_num):
    """Produces the CSV output for our model

    Args:
        G : The NetworkX Graph we will process
        graph_num: The day of the Graph (0-62)
    """
    # Output DataFrmae init
    graph_data = pd.DataFrame(columns=['Node', 'Party', 'Modularity Class', 'Degree',
                              'Left Percentage', 'Right Percentage', 'Middle Percentage', 'Neutral Percentage'])

    # Loop the Combined Graph nodes to calculate the percentages of the neighbors' parties
    for n in G.nodes():

        neighbor_parties = []

        neighbors = G.neighbors(n)

        for ne in neighbors:
            try:
                neighbor_parties.append(G.nodes[ne]['party'])
            except KeyError:
                continue

        # This function produces a dictinary with all the unique objects and their count
        count = Counter(neighbor_parties)

        # Calculate the percentage of every party
        if 'left' in count:
            left_perc = count['left']/len(neighbor_parties)
        else:
            left_perc = 0
        if 'right' in count:
            right_perc = count['right']/len(neighbor_parties)
        else:
            right_perc = 0
        if 'middle' in count:
            middle_perc = count['middle']/len(neighbor_parties)
        else:
            middle_perc = 0
        if 'neutral' in count:
            neutral_perc = count['neutral']/len(neighbor_parties)
        else:
            neutral_perc = 0

        graph_data.loc[len(graph_data)] = [n, party, G.nodes[n]['Community'],
                                           G.degree[n], left_perc, right_perc, middle_perc, neutral_perc]

    graph_data.to_csv(f'CSV outputs/graph_{graph_num}.csv', index=False)


dir = 'day_graphs/'

# Read Attributes pickle
attributes = pickle.load(open('node_attributes', 'rb'))

# Loop the days and read the corrresponding Graph
for i in tqdm(range(1, 63)):

    Graph_Num = str(i)
    graph_name = 'Graph_'+Graph_Num
    file = dir+graph_name
    output = 'Gexf Files/' + graph_name + '.gexf'

    G = read_graph(file, attributes)

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
    readwrite.write_community_csv(coms, f"Communities/communities{i}.csv", ",")
    # TODO: Find a way to skip the file creation
    coms_df = pd.read_csv(f"Communities/communities{i}.csv", header=None)

    # Create a dictionary to in order to set it as an attribute with the name "Community"
    communities = {}

    for index, row in coms_df.iterrows():
        for i in range(0, len(row)):
            try:
                if not math.isnan(row[i]):
                    communities[int(row[i])] = index
            except TypeError:
                print(row[i])
    nx.set_node_attributes(G, communities, name="Community")

    # Call function produce_csv to export the data file for the model
    produce_csv(G, Graph_Num)
    # Export to .GEXF for visualization purposes
    nx.write_gexf(G, output)
