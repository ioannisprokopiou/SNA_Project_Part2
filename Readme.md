# Instructions

### Create a Virtual Enviroment
python -m venv venv

### Activate the Virtual Enviroment
**Windows** 

venv\Scripts\activate

**MacOS**

source mypython/bin/activate

### Install Requirements

pip install -r requirements.txt

# Information about the data

## The Day Graphs folder
This folder contains 62 graphs, one for each day from 25-7-2022 to 25-9-2022. The name of the graph is set as Graph_0, Graph_1, etc. 
Apparently Graph_0 represents the graph for the first day, Graph_1 represents the graph for the second day, etc. 
All graphs are in pickle format. To load them you need to execute the following:

**G = pickle.load(open('day_graphs/_graph_name_','rb'))**

**G is a networkx Undirected Graph object**

Each graph represents a Twitter network that has been formulated by taking into account the mentions of each user. 
So let's say user A mentions user B, then an edge from user A to user B will be created. As we have already mentioned each graph 
contains ONLY the users that tweeted at that specific date. If you want to create a new graph that takes into account all the users(nodes) and mentions(edges) available 
you will need to sequentially merge all the graphs. This is feasible by using networkx.   

##The node_attributes file
This file is a pickle file, which when unpickled is in dict format. It contains information for all the nodes that are available in all the Graphs. 
An example is the following:

24602: {'followers': 20, 'following': 76, 'total_tweets': 552, 'lists': 0, 'twitter_age': 790, 'verified': False, 'party': 'right'}}

This means that the user (node) with id 24602 is a node with the following attributes:
1. followers: Number of followers
2. following: Number of following 
3. total_tweets: the total number of tweets the user has posted from the day he/she registered on Twitter
4. lists: the number of lists that the user is subscribed to
5. twitter_age: the number of days that passed since the registration of the user 
6. verified: if the user is verified or not
7. party: the political party the user "follows" (right,left,middle or neutral)

Of course there is a number of additional features that you can extract by yourselves. 

For any additional questions, don't hesitate to contact me. 
