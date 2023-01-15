import networkx as nx
import matplotlib.pyplot as plt
import pickle
import pandas as pd
import math
from cdlib import algorithms, readwrite
from collections import Counter

def read_graph(file):
  #Read Graph pickle
  G = pickle.load(open(file,'rb'))

  #Read Attributes pickle
  attributes = pickle.load(open('node_attributes','rb'))

  #Set Node Attributes
  nx.set_node_attributes(G, attributes)

  return G, attributes


def produce_csv(G, graph_num):

  graph_data = pd.DataFrame(columns=['Node','Party','Modularity Class','Degree','Left Percentage','Right Percentage','Middle Percentage','Neutral Percentage'])

  for n in G.nodes():
    #print(G.nodes[n])
    neighbor_parties = []

    neighbors = G.neighbors(n)

    for ne in neighbors:
      try:
        neighbor_parties.append(G.nodes[ne]['party'])
      except KeyError:
        continue

    count = Counter(neighbor_parties)

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

    try:
      party = G.nodes[n]['party']
    except KeyError:
      party = ''

    graph_data.loc[len(graph_data)] = [n,party,G.nodes[n]['Community'],G.degree[n],left_perc,right_perc,middle_perc,neutral_perc]

  graph_data.to_csv(f'CSV outputs/graph_{graph_num}.csv',index=False)

dir = 'day_graphs/'
graph_data = pd.DataFrame(columns=['Graph', 'Nodes', 'Edges','Transitivity','Avg Degree Centrality','Avg Clustering Coefficients'])

# Set Graph numbers to process here
for i in range (1,5):
  print(i)
  Graph_Num = str(i)
  graph_name = 'Graph_'+Graph_Num
  file = dir+graph_name
  image = file + '.png'
  output = 'Gexf Files/' + graph_name + '.gexf'

  G, attributes = read_graph(file)

  coms = algorithms.louvain(G, resolution=1.0)
  readwrite.write_community_csv(coms, f"Communities/communities{i}.csv", ",")
  coms_df = pd.read_csv(f"Communities/communities{i}.csv", header=None)

  communities = {}

  for index,row in coms_df.iterrows():
    for i in range(0,len(row)):
      if not math.isnan(row[i]):
        communities[int(row[i])] = index

  nx.set_node_attributes(G, communities, name="Community")

  produce_csv(G,Graph_Num)
  nx.write_gexf(G, output)


