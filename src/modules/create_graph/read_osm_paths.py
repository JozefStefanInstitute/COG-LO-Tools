#!/usr/bin/python3

from src.modules.create_graph.data_parser.data_handler import DataHandler
from src.modules.create_graph.neighbours_finder import NeighboursFinder
import networkx as nx
import matplotlib.pyplot as plt


def drawGraph(H, postalNodes, postalWays):
    G = nx.Graph()
    li = []
    labels = {}

    for posts in postalNodes:
        li.append(posts)
        G.add_node(posts, pos=(postalNodes[posts]["lat"], postalNodes[posts]["lon"]))
        labels[posts] = postalNodes[posts]["post_id"]


    for edge in postalWays:
        for edgeN in postalWays[edge]:
            G.add_edge(edge, edgeN, weight=postalWays[edge][edgeN]['weight'])


        # plt.figure(1)

    #pos = nx.spring_layout(G, k=0.25, iterations=40)
    pos = nx.get_node_attributes(H, 'pos', )
    nx.draw(H, pos=pos, node_size=0.1, node_color='g', edge_color='g',)
    nx.draw_networkx_nodes(G, pos, nodelist=li, node_color='g')
    col = nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g',edge_color='r')
    col.set_zorder(20)
    nx.draw_networkx_labels(G, pos, labels, font_size=16)

    plt.show()


def drawStaticGraph(nodes, ways, results):
    G = nx.Graph()
    li = []

    #    edge
    labels = {}
    i = 0
    color_map = []
    for posts in nodes:
        if nodes[posts].post_id != None:
            if nodes[posts].post_id in results:
                color_map.append('red')
            else:
                color_map.append('blue')
            labels[i] = nodes[posts].post_id + "(" + str(posts) + ")"
        else:
            labels[i] = posts
            color_map.append('green')

        li.append(posts)
        G.add_node(posts)

        i = i + 1

    for key, value in ways.items():
        for kc, vc in value.items():
            print(value)
            print(vc)

            G.add_edge(key, kc, weight=vc['weight'])

    import matplotlib.pyplot as plt

    # plt.figure(1)
    pos = nx.spring_layout(G, k=0.1, iterations=80)
    nx.draw_networkx_nodes(G, pos, node_color=color_map, nodelist=li)
    nx.draw_networkx_edges(G, pos, nodelist=li, node_color='g')

    nx.draw_networkx_labels(G, pos, labels, font_size=16)

    plt.show()


if __name__ == "__main__":

    # osmHandler = DataHandler("data/duplica_dob_test_export.osm",
    #                         'data/List of Postal Offices (geographical location).csv')

    osmHandler = DataHandler("modules/create_graph/data/slovenia-latest.osm.xml",
                             'modules/create_graph/data/List of Postal Offices (geographical location).csv')
    G = osmHandler.graph_viz()

    roadNodes = osmHandler.modified_nodes
    roadWays = osmHandler.modified_ways
    map_posts_to_nodes = {}
    for k,v in roadNodes.items():
        if v.is_post:
            map_posts_to_nodes[v.post_id] = k
            print("Post_id: "+str(v.post_id)+ " node_id"+ str(k))

    postNode = {}
    postEdge = {}
    tmpRes =[]

    finder = neighbourAlg.NeighboursFinder(G)
    for postId, nodeId in map_posts_to_nodes.items():
        #roadNodes, roadWays = syntic_graph2_constraction()
        #postId = 'A5'
        #nodeId = 601582324
        res = finder.search_near_posts(roadNodes, roadWays, nodeId, 1.5)
        print('PostID '+str(postId) +' Node: '+str(nodeId) + ' r: '+str(res))
        tmpRes.append((postId, nodeId, res))

        for res_id, res_dist in res:
                        if nodeId in postEdge:
                            tmp = postEdge[nodeId]
                            tmp[roadNodes[map_posts_to_nodes[res_id]].node_id] = {'weight': res_dist}
                            postEdge[nodeId] = tmp
                            print(res_id)
                        else:
                            postEdge[nodeId] = {roadNodes[map_posts_to_nodes[res_id]].node_id:{'weight': res_dist}}


    for k, v in roadNodes.items():
        if v.post_id != None:
            postNode[k] = v.__dict__

    for postId, nodeId, res in tmpRes:
        print('PostID ' + str(postId) + ' Node: ' + str(nodeId) + ' r: ' + str(res))
    if len(postEdge) != 0:
        drawGraph(G, postNode, postEdge)

    postNode = {}
    postEdge = {}


    import json
    json_str = json.dumps(postNode)
    f = open("post_nodes.json", "w")
    f.write(json_str)
    f.close()

    json_str = json.dumps(postEdge)
    f = open("post_edge.json", "w")
    f.write(json_str)
    f.close()
    #w = csv.writer(open("edge.csv", "w"))
    #for key, val in postNode.items():
    #    w.writerow([key, val])
    #drawStaticGraph(roadNodes, roadWays, res)

