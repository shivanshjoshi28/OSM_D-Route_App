# importing the required libraries
import plotly.express as px
from skimage import io
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
from collections import defaultdict


# Architecture of Graph- Djikstra Algorithm

class Node_Distance:

    def __init__(self, name, dist):
        self.name = name
        self.dist = dist


class Graph:

    def __init__(self, node_count):
        # Store the adjacency list as a dictionary
        # The default dictionary would create an empty list as a default (value)
        # for the nonexistent keys.
        self.adjlist = defaultdict(list)
        self.node_count = node_count

    def Add_Into_Adjlist(self, src, node_dist):
        self.adjlist[src].append(node_dist)

    def Dijkstras_Shortest_Path(self, source, dst, v):

        # Initialize the distance of all the nodes from the source node to infinity
        distance = [999999999999] * self.node_count
        # Distance of source node to itself is 0
        distance[source] = 0
        parent = []
        parent.clear()
        for i in range(v):
            parent.append(i)

        # Create a dictionary of { node, distance_from_source }
        dict_node_length = {source: 0}

        while dict_node_length:

            # Get the key for the smallest value in the dictionary
            # i.e Get the node with the shortest distance from the source
            current_source_node = min(
                dict_node_length, key=lambda k: dict_node_length[k])
            del dict_node_length[current_source_node]
            if(current_source_node == dst):
                break

            for node_dist in self.adjlist[current_source_node]:
                adjnode = node_dist.name
                length_to_adjnode = node_dist.dist

                # Edge relaxation
                if distance[adjnode] > distance[current_source_node] + length_to_adjnode:
                    parent[adjnode] = current_source_node
                    distance[adjnode] = distance[current_source_node] + \
                        length_to_adjnode
                    dict_node_length[adjnode] = distance[adjnode]
        return distance[dst], parent


def ImageGet():   # to get the graph in the image format that we have save
    img = io.imread('WebAppCurrImage.jpg')
    fig = px.imshow(img)
    return fig


def Setup(a1, a2, a3, a4):
    north, east, south, west = a1, a2, a3, a4    # input the graph detail
    # Downloading the map as a graph object
    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    # Plotting the map graph

    # As We have to apply dijkstra's Algorithm and we know that the input nodes in djikstra algorithm is 0 index for the node , so first we given the number to all the nodes
    v = len(G.nodes)
    di = {}
    index = 0
    for node in G.nodes(data=True):
        # each value of dictionary correspond to the index
        di[node[0]] = [index]
        di[index] = [node[0]]
        index += 1

    li = []
    li.clear()
    for edge in G.edges(data=True):
        src_id = edge[0]
        dst_id = edge[1]
        new_src = di[src_id][0]
        new_dst = di[dst_id][0]
        weight = edge[2]['length']
        li.append([new_src, new_dst, weight])
    ox.plot_graph(G, edge_color="y", save=True, filepath="WebAppCurrImage.jpg")
    e = len(li)

    return G, v, e, li, di


def node_list_to_path(G, node_list):
    edge_nodes = list(zip(node_list[:-1], node_list[1:]))
    # print(edge_nodes)
    lines = []
    for u, v in edge_nodes:
        # if there are parallel edges, select the shortest in length
        data = min(G.get_edge_data(u, v).values(), key=lambda x: x['length'])

        # if it has a geometry attribute (ie, a list of line segments)
        if 'geometry' in data:
            # add them to the list of lines to plot
            xs, ys = data['geometry'].xy
            lines.append(list(zip(xs, ys)))
        else:
            # if it doesn't have a geometry attribute, the edge is a straight
            # line from node to node
            x1 = G.nodes[u]['x']
            y1 = G.nodes[u]['y']
            x2 = G.nodes[v]['x']
            y2 = G.nodes[v]['y']
            line = [(x1, y1), (x2, y2)]
            lines.append(line)
    return lines


def calc_lat_long(G, path):
    lines = node_list_to_path(G, path)
#     print(lines)
    long2 = []
    lat2 = []
    long2.clear()
    lat2.clear()
    for each_line_detail in lines:
        for coordinate in each_line_detail:
            long2.append(coordinate[0])
            lat2.append(coordinate[1])
    return lat2, long2


def plot_path(lat, long, origin_point, destination_point):
    # adding the lines joining the nodes
    fig = go.Figure(go.Scattermapbox(
        name="Path",
        mode="lines",
        lon=long,
        lat=lat,
        marker={'size': 10},
        line=dict(width=4.5, color='blue')))

    # adding source marker
    fig.add_trace(go.Scattermapbox(
        name="Source",
        mode="markers",
        lon=[origin_point[1]],
        lat=[origin_point[0]],
        marker={'size': 12, 'color': "red"}))

    # adding destination marker
    fig.add_trace(go.Scattermapbox(
        name="Destination",
        mode="markers",
        lon=[destination_point[1]],
        lat=[destination_point[0]],
        marker={'size': 12, 'color': 'green'}))

    # getting center for plots:
    lat_center = np.mean(lat)
    long_center = np.mean(long)

    # defining the layout using mapbox_style
    fig.update_layout(mapbox_style="open-street-map",
                      mapbox_center_lat=30, mapbox_center_lon=-80)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      mapbox={
        'center': {'lat': lat_center, 'lon': long_center},
        'zoom': 13})

#     fig.show()
    return fig


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server

app.layout = html.Div([
    html.H1("ORM Route Finder - Djikstra's Algorithm Implementation"),
    dcc.Link("All the latitude and longitude can be found from here :  ",
             href="https://www.openstreetmap.org/#map=16/30.3207/78.0549", target="_blank"),
    html.Br(),
    html.Div(["Map North: ",
              dcc.Input(id='input-1-state', value='30.2943', type='text')]),
    html.Br(),
    html.Div(["Map East: ",
              dcc.Input(id='input-2-state', value='78.1079', type='text')]),
    html.Br(),
    html.Div(["Map South: ",
              dcc.Input(id='input-3-state', value='30.2652', type='text')]),
    html.Br(),
    html.Div(["Map West: ",
              dcc.Input(id='input-4-state', value='78.0593', type='text')]),
    html.Br(),
    html.Div(["Source Longitude: ",
              dcc.Input(id='source-long', value='30.27968', type='text')]),
    html.Br(),
    html.Div(["Source Latitude: ",
              dcc.Input(id='source-lat', value='78.07736', type='text')]),
    html.Br(),
    html.Div(["Destination Longitude: ",
              dcc.Input(id='destination-long', value='30.275218', type='text')]),
    html.Br(),
    html.Div(["Destination Latitude: ",
              dcc.Input(id='destination-lat', value='78.081006', type='text')]),
    html.Br(),
    html.Button(id='submit-button-state', n_clicks=0,
                children='Find the Shortest Route'),
    html.Br(),
    html.Div(id='output-state'),
    html.Br(),
    html.Div(id='container'),
    html.Br(),
    html.Div([html.Span("Github repo "), dcc.Link("https://github.com/shivanshjoshi28/OSM_Route_Finder",
                                                  href="https://github.com/shivanshjoshi28/OSM_Route_Finder", target="_blank"), ]),
    html.H3("©️ Created by Shivansh Joshi")

])


def getPath(parent, output_node_id_zero_indexed, input_node_id_zero_index, di):
    route = []
    route.clear()
    curr = output_node_id_zero_indexed
    while(curr != input_node_id_zero_index):
        route.append(curr)
        curr = parent[curr]
    route.append(input_node_id_zero_index)
    route.reverse()
    path = []
    path.clear()
    for pa in route:
        path.append(di[pa][0])
    return path

# As it seems to be nice,i.e path with the minimum distance



@app.callback(Output('container', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'),
              State('input-3-state', 'value'),
              State('input-4-state', 'value'),
              State('source-long', 'value'),
              State('source-lat', 'value'),
              State('destination-long', 'value'),
              State('destination-lat', 'value'))
def update_output(n_clicks, input1, input2, input3, input4, src_long, src_lat, dst_long, dst_lat):
    src_long = float(src_long)
    src_lat = float(src_lat)
    dst_long = float(dst_long)
    dst_lat = float(dst_lat)
    origin_point = (src_long, src_lat)
    destination_point = (dst_long, dst_lat)
    G, v, e, li, di = Setup(float(input1), float(
        input2), float(input3), float(input4))

    g = Graph(v)   # graph with v number of vertex
    for i in range(e):  # graph with e number of edges
        g.Add_Into_Adjlist(li[i][0], Node_Distance(li[i][1], li[i][2]))

    # get the nearest nodes to the locations
    origin_node = ox.get_nearest_node(G, origin_point)
    destination_node = ox.get_nearest_node(G, destination_point)
    input_node_id_zero_index = di[origin_node][0]
    output_node_id_zero_indexed = di[destination_node][0]

    ShortestDist, parent = g.Dijkstras_Shortest_Path(
        input_node_id_zero_index, output_node_id_zero_indexed, v)
    path = getPath(parent, output_node_id_zero_indexed,
                   input_node_id_zero_index, di)
    lat2, long2 = calc_lat_long(G, path)
    fig1 = plot_path(lat2, long2, origin_point, destination_point)
    return html.Div([dcc.Graph(figure=ImageGet()), html.Br(), html.H6("Shortest Path length = {} meters".format(ShortestDist), style={'color': 'Red', 'text-align': 'center'}), html.Br(), dcc.Graph(figure=fig1)])


if __name__ == '__main__':
    app.run_server(debug=False)
