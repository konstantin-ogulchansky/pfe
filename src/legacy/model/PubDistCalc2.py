import os
import sys
import json
import time
import traceback
import networkx as nx
import community_louvain as cm
import collections
import math
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from matplotlib import rcParams
import random
import pandas as pd
from pyvis.network import Network
import numpy as np
import networkx.algorithms.community as cmm
import matplotlib
from collections import Counter
col=allcolors = range(0xFFFFFF+1)
k=2
numpubdist = {}
authdist = []
nbnc1=0
moddict={}
edgc1dict={}
ndc1dict={}
ndc2dict={}
edgc2dict={}
nbebl={}
nbnc2=0
nbec1=0
nbec2=0
modc1=0
modc2=0
nbeb=0
fixdate=2015
lastpubsum=0
largest_cc={}
# trackauth=[23392711700,8905960300,6603178468,7003638977,24765908100,53880298500,7003954863,55884599100,57200498082,6603550679,6602188705,55888328400,7006015230,6603827744,7006945745,55885318000,57203999691,7004269287,12545018500,56211628500,55887022200,55902164500,56343725100,6603671578,11339046600]

trackauth = [24328821200,57194761095,57201557606,7004305656,6507577569,57199220111,23986650400,6602229923,56732733900,23135704400,24781143200,57191328845,24576636300,6507749243,57189376990,6603769649,12139968700,55557400700,56533775500,55907685600,14034000100,10142984200,57195581679,6602864827,7003438151,6602189293,16244613900,6506368184,55885318000,55887022200,12545018500,7006015230,55902164500,15061529900 ,55883979600,54581372000,35588784300,35877201000,57204802364,25929341100, 8976201700, 57205481547, 57195638233, 15061529900, 6701836992, 56516772600, 6602211855,
             35583036400, 14021020300, 55888328400, 23977126600, 57190576899, 57189034692, 55557927000, 7006929810,
             11339046600, 23392711700, 8905960300, 6603178468, 7003638977, 24765908100, 7003954863, 55884599100,
             57200498082, 6603550679, 55546759400, 56613081700, 57191622205, 56826065900, 57190883130, 57043755900,
             57191505920]
authtk = [23392711700, 6603178468, 8905960300]
labexstudent=[55546759400,56613081700,56826065900,57190883130,57043755900,57191505920,55557927000,57189376990,57189034692,57194446159,57191328845,56732733900,56516772600,57199220111,57190576899,57195638233,57194761095,57205481547]
pubcount={}
te = [(7003638977, 55546759400), (6603178468, 55546759400), (55546759400, 7003638977), (55546759400, 6603178468)]
te2 = [(56613081700, 11339046600), (7006929810, 11339046600), (56613081700, 11339046600), (7006929810, 11339046600)]
clustersdic = str(datetime.datetime.today()).replace("-", "").replace(".", "").replace(":", "")
oldpart={}
G = nx.Graph()
affiliation_city = {}
auth_city = {}
city = {}
cities = set()
auth_name = {}
auth_pub = {}
todelete = set()
comodularity = {}
nintraedges={}
nintrapublications={}
colabcount={}

doc=57189034692
enc2=6603178468
enc1=23392711700
docname="nicolas huin"

df = pd.read_csv("./citiesoff.csv", encoding="latin-1")
city = df.to_dict()


def debug(x, end='\n'):
    sys.stderr.write(x)
    sys.stderr.write(end)


def export_heatmap(filename, auth_cluster, city_of_auth):
    all_cities = set()
    city_id = {}

    for auth in auth_cluster:
        if (city_of_auth.get(auth)):
            all_cities.add(city_of_auth[auth])

    cnt = 0
    for c in all_cities:
        city_id[c] = cnt
        cnt += 1

    nbr_clusters = auth_cluster[max(auth_cluster, key=auth_cluster.get)] + 1
    # heatmap = [[0] for i in range(len(cities))] * nbr_clusters
    heatmap = [[0] * (len(all_cities)) for i in range(nbr_clusters)]

    cluster_authors = [set() for i in range(nbr_clusters + 1)]

    for auth, cluster in auth_cluster.dict():
        if (city_of_auth.get(auth)):
            cluster_authors[cluster].add(auth)

    for auth, clust in auth_cluster.dict():
        if (city_of_auth.get(auth)):
            heatmap[clust][city_id[city_of_auth[auth]]] += 1 / len(cluster_authors[clust])

    # for line in heatmap:
    #     debug(str(line))

    domain = filename[:4]

    dir = 'fig\\' + domain

    if not os.path.exists(dir):
        os.makedirs(dir)

    xlabels = [a[0] for a in cities]
    ylabels = [c for c in range(nbr_clusters)]

    plt.figure(figsize=(16, 9))

    sns.heatmap(heatmap, cmap='Blues')
    # plt.tight_layout()

    plt.title("Heatmap of Degree Distribution : " + filename[0:9], fontsize=22)
    plt.xlabel("City", fontsize=12)
    plt.ylabel("Cluster", fontsize=12)

    plt.savefig(dir + '\\HT_' + filename + '.png')
    plt.clf()
    plt.close()


def extract_data_from_json(filename, domain):
    debug("extract_data_from_json('%s')" % (filename))
    # open input json file
    filepath = 'D:\\ourPFEstatistics\\json' + '\\' + domain + '\\' + filename
    f = open(filepath)

    data = None
    # parse json file
    try:
        data = json.loads(f.read())
    except Exception as e:
        print(filepath + " didn't work !")
        traceback.print_exc()
        f.close()

    f.close()
    return data


def extract_edges(papers):
    debug("extract_edges()")
    global bothenc
    for paper in papers:

        if (not paper.get('affiliation')):
            continue
        aff = paper['affiliation']


        # if that entry doesn't have an author ==> it's not a paper
        if (not paper.get('author')):
            continue

        authors = paper['author']

        # if there is only 1 author, ignore this paper

        if (not type(authors) is list):
            continue
        else:
            comp = set()
            authdist.append(len(authors))
            for i in range(len(authors)):

                z = int(authors[i]['authid'])


                auth_name[z] = authors[i].get('authname', 'x')
                comp.add(int(authors[i]['authid']))


            for i in range(len(comp)):
                u = int(list(comp)[i])

                for j in range(i):
                    v = int(list(comp)[j])


                    # since we are looping over the same array, we should skip this case

                    # if ((v,u) not in pairs and (u,v) not in pairs):

                    # undirected graph ==> (u,v) == (v, u)
                    # to store only 1/2 of the memory
                    # we will always use key (u,v) such as u is smaller than v
                    # u, v = min(u, v), max(u, v)

                    # checking if edge already exists
                    if G.has_edge(u, v):
                        # update the edge weight
                        G[u][v]['weight'] += 1
                    else:
                        G.add_edge(u, v, weight=1)
            comp.clear()


    return G.number_of_nodes(), len(papers)


def export_degree_hist(filename, domain):
    deg = [d for n, d in G.degree()]
    dir = 'fig\\' + domain

    if not os.path.exists(dir):
        os.makedirs(dir)

    slope = export_log_pl(deg, dir + '\\' + filename + '.png')
    degmax = max([d for n, d in G.degree()])
    mean = sum([d for n, d in G.degree()]) / len([d for n, d in G.degree()])

    return slope, degmax, mean


def export_evolution(data, filename, domain, metric):
    y = [x for x in range(1990, 2019)]
    plt.title(metric + "  : " + domain)
    plt.xlabel("Year")
    plt.ylabel(metric)

    # if(metric == 'Slope'):
    #     print(data)

    plt.plot(y, data, 'k-', lw=0.5)
    plt.plot(y, data, 'k+')
    plt.tight_layout()
    plt.grid()
    plt.savefig(filename + "_" + metric)
    plt.clf()
    plt.close()


def export_graphml(filename, domain):
    debug("export_graphml('%s')" % filename)

    # create a file .graphml to output the graph coded in graphml
    dir = 'graphml\\' + domain

    if not os.path.exists(dir):
        os.makedirs(dir)

    output_file = open(dir + '\\' + filename, "w+")

    debug("---- file created : %s" % filename)
    sys.stdout = output_file

    # graphml format is structured as follows :
    #     - xml_header
    #     - nodes declarations
    #     - edges declarations
    #     - xml_footer

    xml_header = "<?xml version='1.0' encoding='utf-8'?>"
    xml_header += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">'
    xml_header += '<graph edgedefault="undirected">\n'  # undirected graph

    sys.stdout.write(xml_header)

    debug("---- xml_header : done.")

    # res += xml_header

    sys.stdout.write('<key id="d1" for="edge" attr.name="weight" attr.type="int"/>')

    # node ids declaration as graphml format : <node id="#node" />
    nodes = G.nodes
    for node in nodes:
        sys.stdout.write('<node id="%d"/>\n' % (node))

    debug("%d nodes added." % len(nodes))
    # edges declaration as graphml format : <edge source="src" target="tgt" />

    cnt = 1
    for e in G.edges.data(data='weight', default=1):
        sys.stdout.write('<edge id="e%d" source="%d" target="%d">' % (cnt, e[0], e[1]))
        sys.stdout.write('<data key="d1">%d</data>' % e[2])
        sys.stdout.write('</edge>')
        cnt += 1

    # xml_footerx
    sys.stdout.write('</graph></graphml>\n')

    debug("---- xml_footer : done.")
    debug("---- file exported successfully : %s\n" % filename)

    # close file now that we are done
    output_file.close()


def extract_all(domain):
    folder = 'D:\\ourPFEstatistics\\json' + '\\' + domain

    slopes = []
    degmaxs = []
    means = []
    mods = []
    execs = []
    nbr_partitions = []
    nbr_authors = []
    nbr_papers = []

    nbr_author = 0
    nbr_paper = 0

    for filename in os.listdir(folder):

        if filename.endswith('.json'):

            domain = filename[:4]
            year = filename[5:9]

            data = extract_data_from_json(filename, domain)
            if (data == None):
                debug(filename + " : data = None")
                continue
            papers = data['search-results']['entry']


            ############################################################################################
            nbr_author, nbr_paper_cur = extract_edges(papers)
            #
            # nbr_paper = nbr_paper_cur
            #
            # nbr_authors.append(nbr_author)
            # nbr_papers.append(nbr_paper)

            ############################################################################################
            # s, d, m = export_degree_hist(filename[:9], domain)
            # slopes.append(s)
            # degmaxs.append(d)
            # means.append(m)

            ############################################################################################
            partition, p, mod, exe = export_stats(filename[:9], domain)
            # nbr_partitions.append(p)
            # mods.append(mod)
            # execs.append(exe)
            # ############################################################################################
            print(filename[5:-5])
            if (filename[5:-5] == "2018"):
                print("stooooooooooooooooop "+str(len(G.nodes())))
            ############################################################################################
            # export_heatmap(filename[:9], partition, city)
            # export_graphml("tranche " + filename[:9] + '.graphml', domain)

    # folder = os.getcwd() + '\\distributions'
    #
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
    #
    # folder = os.getcwd() + '\\distributions\\' + domain
    #
    # if not os.path.exists(folder):
    #     os.makedirs(folder)

    # export_evolution(slopes, folder + '\\' + domain,domain,'Slope')
    # export_evolution(nbr_authors, folder + '\\' + domain, domain, 'Number of Authors')
    # export_evolution(nbr_papers, folder + '\\' + domain, domain, 'Number of Publications per year')
    # export_evolution(degmaxs, folder + '\\' + domain,domain,'Degree Max')
    # export_evolution(means, folder + '\\' + domain,domain,'Degree Mean')
    # export_evolution(mods, folder + '\\' + domain, domain, 'Modularity')
    # export_evolution(execs, folder + '\\' + domain, domain, 'Execution Time')
    # export_evolution(nbr_partitions, folder + '\\' + domain, domain, 'Number of Partitions')
    distpub = list(auth_pub.values())
    plt.hist(distpub);
    # ax.set_title('Distribution of number of publications:COMP')
    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("number of publications")
    plt.xlim(left=0, right=100)
    plt.savefig('Distribution of number of publicationsCOMP.png')
    plt.clf()
    plt.close()

    # export_graphml("whole_graph_" + domain + ".graphml", '')


def export_stats(filename, domain):
    # dictionary = {1: 27, 34: 1, 3: 72, 4: 62, 5: 33, 6: 36, 7: 20, 8: 12, 9: 9, 10: 6, 11: 5,
    #               12: 8, 2: 74, 14: 4, 15: 3, 16: 1, 17: 1, 18: 1, 19: 1, 21: 1, 27: 2}
    # plt.bar(list(auth_pub.keys()), auth_pub.values(), color='g')
    # plt.show()

    ######################### Calculating Data ########################################################

    debug("Calculating data")
    nbr_nodes = G.number_of_nodes()
    nbr_edges = G.number_of_edges()

    debug("Connected Componnents")
    Gc = []
    percentage = 0
    nbr = 0
    # sortedcc=sorted(nx.connected_components(G),key=len,reverse=True)
    sortedcc = nx.connected_components(G)
    for cc in sortedcc:

        if (len(set(cc).intersection(trackauth)) != 0):
            Gc += cc
    #####################################################""pubdist############################################
    l=0
    for n in G.nodes:
        for k in G.neighbors(n):
            l+=G[n][k]["weight"]
        numpubdist[int(filename[-4:])][n]=l
        l=0
        ##########################"############Delet##########################
    #
    # global todelete
    # global partition
    # global fixdate
    # for n in G.nodes:
    #     if (not city.get(n) and n not in trackauth):
    #
    #         todelete.add(n)
    #
    #
    #
    #     else:
    #         if (not n in city):
    #             city[n] = " ";
    #         if (city[n] != 'nice' and city[n] != 'sophia antipolis' and city[n] != 'valbonne' and n not in trackauth):
    #             todelete.add(n)
    # for n in todelete:
    #     test = True
    #     if (n in Gc):
    #         for n2 in trackauth:
    #             if (G.has_edge(n, n2) or G.has_edge(n2, n)):
    #                 test = False
    #         if (test):
    #             Gc.remove(n)

    ########################################################################

    # Gc = max(nx.connected_components(G), key=len)
    # global largest_cc
    # largest_cc = G.subgraph(Gc.copy())
    #
    # debug("Partitions")
    #
    # start = time.perf_counter()
    #
    # # global k
    # # partlabel=cmm.label_propagation.label_propagation_communities(largest_cc)
    # # k+=2
    # # partition={}
    # # counti=0
    # # for s in partlabel:
    # #     partition.update(dict.fromkeys(s, counti))
    # #     counti+=1
    # global oldpart
    # if(not oldpart):
    #     partition = cm.best_partition(largest_cc,random_state=1)
    #     oldpart=partition.copy()
    # else:
    #     maximum = max(oldpart.values())
    #     alln=list(largest_cc.nodes)
    #     allclust=list(oldpart.keys())
    #     for i in alln:
    #         if(i not in allclust):
    #             oldpart[i]=maximum+1
    #             maximum+=1
    #
    #     partition = cm.best_partition(largest_cc,partition=oldpart,random_state=1)
    #     oldpart = partition.copy()
    #     # if (int(filename[-4:]) == 2018):
    #     #     sys.stderr.write("Done")
    #     #     json.dump(partition, open("politakibetterpartition2018.json", 'w'))

#################################collect number of nodes evolution#######################################################
    #
    # for i in range(0,18):
    #     it=[k for k, v in partition2018.items() if v == i]
    #     for k1 in it:
    #         sb=1
    #         for k2 in it[sb:]:
    #             sb+=1
    #             if(k1!=k2 and G.has_edge(int(k1),int(k2))):
    #
    #                 nintraedges[i][int(filename[-4:])]+=1
    #
    #                 nintrapublications[i][int(filename[-4:])]+=G[int(k1)][int(k2)]['weight']







    # print(partition)
    ########################################################################
    # doclist = set()
    # partition2  ={}
    # if (enc1 in partition.keys()):
    #     doclist.add(enc1)
    #     partition2[enc1] = '#00A4CCFF'
    #     # sys.stderr.write("\n yes \n")
    #     for k, v in partition.items():
    #
    #         if (partition[k] == partition[enc1]):
    #             doclist.add(k)
    #             partition2[k] = '#00A4CCFF'
    #
    # if (enc2 in partition.keys()):
    #     doclist.add(enc2)
    #     partition2[enc2] = '#F95700FF'
    #     # sys.stderr.write("\n yes \n")
    #     for k, v in partition.items():
    #
    #         if (partition[k] == partition[enc2]):
    #             doclist.add(k)
    #             partition2[k] = '#F95700FF'



###################################################################################################
    execution_time = 0
    # values = [partition.get(node) for node in largest_cc.nodes]
    # print(values)
    # # print("%d == %d" % (largest_cc.number_of_nodes(), len(auth_name.keys())), file =
    # # here we draw
    # plt.figure(figsize=(28, 28))
    # auth_name2={}
    # for x in largest_cc.nodes:
    #     if((x not in trackauth) ):
    #         auth_name[x]=auth_name[x]
    #     auth_name2[x]=auth_name[x]
    # #
    # ps=nx.spring_layout(largest_cc,k=0.1,iterations=30)
    #
    #
    # # pos=nx.draw_networkx(largest_cc, pos=None, arrows=True, with_labels=True, **kwds)
    # # nx.draw(largest_cc,pos=pos,labels=auth_name2 ,cmap=plt.get_cmap('rainbow'), node_color=values, node_size=30, with_labels=True,font_size=8)
      # image is 8 x 8 inches
    # plt.axis('off')
    # sizenode=[]
    # for n in largest_cc :
    #     if(n in authtk):
    #         sizenode.append(50)
    #     else:
    #         sizenode.append(25)
    # pos_attrs = {}
    # nx.draw_networkx_nodes(largest_cc, pos, node_size=[v * 200 for v in sizenode], cmap=plt.cm.RdYlBu, node_color=values)
    # for node, coords in pos.items():
    #     pos_attrs[node] = (coords[0], coords[1])
    #
    # node_attrs = nx.get_node_attributes(G, 'type')
    # custom_node_attrs = {}
    # for node, attr in node_attrs.items():
    #     custom_node_attrs[node] = "{'type': '" + attr + "'}"
    #
    # # nx.draw_networkx_labels(G, pos_attrs, labels=custom_node_attrs)
    # #
    #
    #
    # nx.draw_networkx_labels(largest_cc, pos_attrs, auth_name2, font_size=16)
    # if (len(set(largest_cc.edges([55546759400])).intersection(te)) ):
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=te,edge_color='r', alpha=0.3,width=14)
    # if (len(set(largest_cc.edges([57190576899])))!=0 ):
    #         ed=set(largest_cc.edges([57190576899]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="fuchsia", alpha=0.8,width=14)
    # if (len(set(largest_cc.edges([55557927000])))!=0 ):
    #         ed=set(largest_cc.edges([55557927000]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color='y', alpha=0.8,width=14)
    #
    # if (len(set(largest_cc.edges([57189034692])))!=0 ):
    #         ed=set(largest_cc.edges([57189034692]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="lime", alpha=0.8,width=14)
    #
    # if (len(set(largest_cc.edges([57043755900])))!=0 ):
    #         ed=set(largest_cc.edges([57043755900]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="aquamarine", alpha=0.8,width=14)
    # if (len(set(largest_cc.edges([14021020300])))!=0 ):
    #         ed=set(largest_cc.edges([14021020300]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="greenyellow", alpha=0.8,width=14)
    # if (len(set(largest_cc.edges([56516772600])))!=0 ):
    #         ed=set(largest_cc.edges([56516772600]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="deepskyblue", alpha=0.8,width=14)
    #
    # if (len(set(largest_cc.edges([57195638233])))!=0 ):
    #         ed=set(largest_cc.edges([57195638233]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="teal", alpha=0.8,width=14)
    # if (len(set(largest_cc.edges([57205481547])))!=0 ):
    #         ed=set(largest_cc.edges([57205481547]))
    #         nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    #         nx.draw_networkx_edges(largest_cc, pos,edgelist=ed,edge_color="deeppink", alpha=0.8,width=14)
    #
    # else:
    #     nx.draw_networkx_edges(largest_cc, pos, alpha=0.3, weight=8)
    # # if(filename[5:9]=='2015'):
    # #     plt.show()
    #
    # docgraph = largest_cc.subgraph(list(doclist).copy())
    # # # nx.draw_networkx_labels(docgraph, pos_attrs, labels=custom_node_attrs)
    # # plt.figure(figsize=(26, 26))  # image is 8 x 8 inches
    # # plt.axis('off')
    # sizenode = []
    # for n in docgraph:
    #     if (n==enc1 or n==enc2):
    #         sizenode.append(50)
    #     else:
    #         sizenode.append(25)
    # pos_attrs = {}
    #
    # pos = nx.spring_layout(docgraph, dim=2, k=4 / math.sqrt(G.number_of_nodes()))
    # for node, coords in pos.items():
    #     pos_attrs[node] = (coords[0], coords[1])
    #
    # auth_name2 = {}
    # for x in docgraph.nodes:
    #     if ((x not in trackauth)):
    #         nm = (auth_name[x] + " 0 0").split()
    #         f = nm[0][0]
    #         s = nm[1][0]
    #         # auth_name[x] = f + "." + s
    #
    #     auth_name2[x] = auth_name[x]
    # values = [partition2.get(node) for node in docgraph.nodes]
    #
    #
    # nx.draw_networkx_nodes(docgraph, pos, node_size=[v * 200 for v in sizenode], cmap=plt.cm.RdYlBu, node_color=values)
    # nx.draw_networkx_labels(docgraph, pos_attrs, auth_name2, font_size=16)
    # if (len(set(docgraph.edges([doc]))) != 0):
    #     ed = set(docgraph.edges([doc]))
    #     nx.draw_networkx_edges(docgraph, pos, alpha=0.3, weight=8)
    #     nx.draw_networkx_edges(docgraph, pos, edgelist=ed, edge_color="yellow", alpha=0.8, width=14)
    #
    # else:
    #     nx.draw_networkx_edges(docgraph, pos, alpha=0.3, weight=8)

    # if not os.path.exists('D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\'):
    #     os.makedirs('D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\')
    # plotIn(largest_cc,partition2,auth_name,'D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\'+ filename[:9],sizenode)
    # plt.clf()
    # plt.close()
    # plt.clf()
    # plt.close()
    # nbr_partitions = max([v for u, v in partition.items()]) + 1
    nbr_partitions = 2
    #

    # debug("Modularity")
    # mod = cm.modularity(partition, largest_cc)
    mod = 2

    ######################### Statistics Printing ########################################################

    # if not os.path.exists('stats'):
    #     os.makedirs('stats')
    #
    # dir = 'stats\\' + domain
    #
    # if not os.path.exists(dir):
    #     os.makedirs(dir)
    #
    # sys.stdout = open(dir + '\\' + "statsFile_" + filename + ".log", "w+")
    #
    # print("Number of nodes in cluster 1: %d" % (nbnc1))
    # print("Number of nodes in cluster 2 : %d" % (nbnc2))
    # print("Number of edges in cluster 1 : %d" % (nbec1))
    # print("Number of edges in cluster 2 : %d" % (nbec2))
    # print("Number of edges between the 2 clusters: %d" % (nbeb))
    # print("Number of clusters: %d" % (nbr_partitions))
    # print("modularity:", modc1)


    ######################### End of Statistics Priting ##################################################

    # if not os.path.exists('csv'):
    #     os.makedirs('csv')
    #
    # dir = 'csv\\' + domain
    #
    # if not os.path.exists(dir):
    #     os.makedirs(dir)
    #
    # with open(dir + '\\' + 'outputpartitionsFile_' + filename + '.csv', 'w+') as output:
    #     for key in partition.keys():
    #         output.write("%s,%s\n" % (key, partition[key]))
    partition={}
    return partition, nbr_partitions, mod, execution_time


def Union(lst1, lst2):
    final_list = list(set(lst1) | set(lst2))
    return final_list

def plotIn(lc,p,names,filen,sz):

    l=[k  for  k in  p.keys()]
    gin=lc.subgraph(l.copy())


    got_net = Network(height="100%", width="100%")

    # set the physics layout of the network
    # got_net.barnes_hut()

    got_net.from_nx(gin)

    for n in got_net.nodes:

        n["color"] = p[n["id"]]
        n["title"] = names[n["id"]]

        if(n["id"]in trackauth):
            n["label"] = names[n["id"]]
        else:
            n["label"] = ' '



        if (n["id"]==enc1 or n["id"]==enc2):
            n["size"]=15
            n["shape"] = "box"

        else:
            n["size"]=6

    for e in got_net.edges:
        b = list(e.values())
        e1 = b[0]
        e2 = b[1]
        e["title"] = G[e1][e2]["weight"]
    got_net.save_graph(filen+".html")
def drawdict(D,title,x,y,c,m):
    plt.figure(figsize=(20,10))
    plt.plot(*zip(*sorted(D.dict())), linestyle='--', marker='o', color=c, label=m)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.yticks(np.arange(min(D.values()), max(D.values()) + 1, 1.0))
    if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain"  ):
        os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain")
    plt.savefig("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain\\"+title)
def drawdict2(D,D1,title,x,y,c1,c2,m1,m2):
    plt.figure(figsize=(20,10))
    plt.plot(*zip(*sorted(D.dict())), linestyle='--', marker='o', color=c1, label=m1)
    plt.plot(*zip(*sorted(D1.dict())), linestyle='--', marker='o', color=c2, label=m2)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)

    if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain"  ):
        os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain")
    plt.savefig("D:\\Internship\\Codes\\stats\\Plots\\Plots Modified Louvain\\"+title)



def main():
    # domain = input()
    #####################################Initiate number of nodes dict########################################
    for i in range(1990,2019):
        numpubdist[i]={}


    ###########################################################################################################

    for file in os.scandir('D:\\ourPFEstatistics\\json'):
        if (file.is_dir() and len(file.name) == 4 and (file.name == 'COMP')):
            domain = file.name


            extract_all(domain)


    # print(cities)
    # print(cities)
    # print(len(cities))
    # with open('cities.csv', 'w') as f:
    #     for key in city.keys():
    #         f.write("%s,%s\n" % (key, city[key]))
    # drawdict(moddict,"Modularity Evolution ","Years","Modularity","red","Modularity")
    # drawdict2(edgc1dict,edgc2dict,"Evolution of the number of edges","years","Number of edges","green","pink","Number of edges in the first cluster","Number of edges in the second cluster")
    # drawdict2(ndc1dict,ndc2dict,"Evolution of the number of nodes","years","Number of nodes","green","pink","Number of nodes in the first cluster","Number of nodes in the second cluster")
    # drawdict(nbebl, "Number of publications between clusters ", "Years", "Number of edges", "red", "Number of edges")
    # json.dump(nintrapublications, open("intrapub.json", 'w'))
    # json.dump(nintraedges, open("intraefges.json", 'w'))
    # json.dump(authdist, open("Authdist.json", 'w'))
if __name__ == '__main__':
    main()