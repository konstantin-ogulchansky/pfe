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

'''this code was made to build the graph from json files, and also for parsing it (clustering, looking for specific informations...).
It also contains some other useful functions '''

col=allcolors = range(0xFFFFFF+1)
k=2
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
# trackauth=[23392711700,8905960300,6603178468,7003638977,24765908100,53880298500,7003954863,55884599100,57200498082,6603550679,6602188705,55888328400,7006015230,6603827744,7006945745,55885318000,57203999691,7004269287,12545018500,56211628500,55887022200,55902164500,56343725100,6603671578,11339046600]

trackauth = [24328821200,57194761095,57201557606,7004305656,6507577569,57199220111,23986650400,6602229923,56732733900,23135704400,24781143200,57191328845,24576636300,6507749243,57189376990,6603769649,12139968700,55557400700,56533775500,55907685600,14034000100,10142984200,57195581679,6602864827,7003438151,6602189293,16244613900,6506368184,55885318000,55887022200,12545018500,7006015230,55902164500,15061529900 ,55883979600,54581372000,35588784300,35877201000,57204802364,25929341100, 8976201700, 57205481547, 57195638233, 15061529900, 6701836992, 56516772600, 6602211855,
             35583036400, 14021020300, 55888328400, 23977126600, 57190576899, 57189034692, 55557927000, 7006929810,
             11339046600, 23392711700, 8905960300, 6603178468, 7003638977, 24765908100, 7003954863, 55884599100,
             57200498082, 6603550679, 55546759400, 56613081700, 57191622205, 56826065900, 57190883130, 57043755900,
             57191505920] #this were the authids of some authors that we were tracking
authtk = [23392711700, 6603178468, 8905960300]
te = [(7003638977, 55546759400), (6603178468, 55546759400), (55546759400, 7003638977), (55546759400, 6603178468)]
te2 = [(56613081700, 11339046600), (7006929810, 11339046600), (56613081700, 11339046600), (7006929810, 11339046600)]
clustersdic = str(datetime.datetime.today()).replace("-", "").replace(".", "").replace(":", "")
oldpart={}
G = nx.Graph() # G will store ou graph
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

doc=57189034692
enc2=6603178468
enc1=23392711700
docname="nicolas huin"

df = pd.read_csv("./citiesoff.csv", encoding="latin-1")  #citiesoff.csv is a file that contains the city of each author
city = df.to_dict()


def debug(x, end='\n'):
    ''' Function used for debuging, it only prints the inputs in the err-output '''
    sys.stderr.write(x)
    sys.stderr.write(end)


def extract_edges(papers):
    ''' This function takes as parameters all the papers of a certain year and extract from them new nodes/edges, that are added to or graph.
     The graph is stored in the global variable G'''

    debug("extract_edges()")
    global bothenc
    for paper in papers:

        if (not paper.get('affiliation')): # papers with no affiliation are not considered
            continue
        aff = paper['affiliation']


        # if that entry doesn't have an author ==> it's not a paper
        if (not paper.get('author')): # papers with no author are not considered
            continue

        authors = paper['author']

        # if there is only 1 author, ignore this paper

        if (not type(authors) is list):
            continue
        else:
            comp = set()

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
    ''' this paper is for drawing the degree distribution, and it takes  2 paramas :
     filename : the name of the file where data will be plotted
     domain : the discipline (computer science, physics...) '''

    deg = [d for n, d in G.degree()]
    dir = 'fig\\' + domain

    if not os.path.exists(dir):
        os.makedirs(dir)

    slope = export_log_pl(deg, dir + '\\' + filename + '.png')
    degmax = max([d for n, d in G.degree()])
    mean = sum([d for n, d in G.degree()]) / len([d for n, d in G.degree()])

    return slope, degmax, mean


def export_evolution(data, filename, domain, metric):
    ''' Function used to draw the evolution over time of a certain metric like modularity for example, it takes 3 params:
     data : the data of the metric that we want to plot
     filename : the name of the file where this data will be plotted
     domain : the discipline
     metric : the name of the metric'''

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


def extract_all(domain):
    ''' This function is responsible of parsing the json files and send them to extract_edges to build the graph
    To use it u have only to change the local variable folder
      it takes as params the name of the discipline
      you can also use it to export some metrics, depends on what you want, I put what we used to export in comments'''

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
    ''' This function wes used to export statistics on our graph and also draw the graph, clustering, detecting the connected components '''

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

        ##########################"############Delet##########################
    ''' This part was used to delete from the graph all authors outside sophia antipolis, nice and valbonne '''

    global todelete
    global partition
    global fixdate
    for n in G.nodes:
        if (not city.get(n) and n not in trackauth):

            todelete.add(n)



        else:
            if (not n in city):
                city[n] = " ";
            if (city[n] != 'nice' and city[n] != 'sophia antipolis' and city[n] != 'valbonne' and n not in trackauth):
                todelete.add(n)
    for n in todelete:
        test = True
        if (n in Gc):
            for n2 in trackauth:
                if (G.has_edge(n, n2) or G.has_edge(n2, n)):
                    test = False
            if (test):
                Gc.remove(n)

    ########################################################################

    # Gc = max(nx.connected_components(G), key=len)
    largest_cc = G.subgraph(Gc.copy())

    debug("Partitions")

    start = time.perf_counter()

    # global k
    # partlabel=cmm.label_propagation.label_propagation_communities(largest_cc)
    # k+=2
    # partition={}
    # counti=0
    # for s in partlabel:
    #     partition.update(dict.fromkeys(s, counti))
    #     counti+=1
    global oldpart
    if(not oldpart):
        partition = cm.best_partition(largest_cc,random_state=1) # clustering the graph
        oldpart=partition.copy()
    else:
        maximum = max(oldpart.values())
        alln=list(largest_cc.nodes)
        allclust=list(oldpart.keys())
        for i in alln:
            if(i not in allclust):
                oldpart[i]=maximum+1
                maximum+=1

        partition = cm.best_partition(largest_cc,partition=oldpart,random_state=1)
        # if (int(filename[-4:]) == 2018):
        #     sys.stderr.write("Done")
        #     json.dump(partition, open("partition2018.json", 'w'))

#################################collect number of nodes evolution#######################################################

    for i in range(0,21):
        it=[k for k, v in partition2018.dict() if v == i]
        for k1 in it:
            sb=1
            for k2 in it[sb:]:
                sb+=1
                if(k1!=k2 and G.has_edge(int(k1),int(k2))):

                    nintraedges[i][int(filename[-4:])]+=1

                    nintrapublications[i][int(filename[-4:])]+=G[int(k1)][int(k2)]['weight']







    # print(partition)
    ########################################################################
    doclist = set()
    partition2  ={}
    if (enc1 in partition.keys()):
        doclist.add(enc1)
        partition2[enc1] = '#00A4CCFF'
        # sys.stderr.write("\n yes \n")
        for k, v in partition.dict():

            if (partition[k] == partition[enc1]):
                doclist.add(k)
                partition2[k] = '#00A4CCFF'

    if (enc2 in partition.keys()):
        doclist.add(enc2)
        partition2[enc2] = '#F95700FF'
        # sys.stderr.write("\n yes \n")
        for k, v in partition.dict():

            if (partition[k] == partition[enc2]):
                doclist.add(k)
                partition2[k] = '#F95700FF'



###################################################################################################
    execution_time = 0 # we dont need it anymore


    docgraph = largest_cc.subgraph(list(doclist).copy())

    sizenode = []
    for n in docgraph:
        if (n==enc1 or n==enc2):
            sizenode.append(50)
        else:
            sizenode.append(25)


    if not os.path.exists('D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\'):
        os.makedirs('D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\')
    plotIn(largest_cc,partition2,auth_name,'D:\\Internship\\Codes\\clusterFredInt\\'+clustersdic+'\\'+ filename[:9],sizenode) #plot the clusters
    plt.clf()
    plt.close()
    plt.clf()
    plt.close()
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

    return partition, nbr_partitions, mod, execution_time


def Union(lst1, lst2):
    final_list = list(set(lst1) | set(lst2))
    return final_list

def plotIn(lc,p,names,filen,sz):

    ''' This function is for drawing the clusters, it takes a s parameter
     lc : largest_connected component that we clustered
     p : the partition that we calculated using louvain method
     names : a list that contains the names of all authors in the largest connected component
     filen : the name of the file where we want to save the figure
     se : the size of noded (large for authors that we want to track
     '''

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
    '''' used to draw a dictionary '''
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
    '''' used to draw 2 dictionaries on the same plot '''

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
    '''' the main function initiates the graph parsing '''
    # domain = input()
    #####################################Initiate number of nodes dict########################################
    # nclusters=max(partition2018.values())
    # print(nclusters)
    # for i in range(nclusters+1):
    #     nintraedges[i]={}
    #     nintrapublications[i]={}
    #     for j in range(1990,2019):
    #         nintraedges[i][j]=0
    #         nintrapublications[i][j] = 0


    ###########################################################################################################

    for file in os.scandir('D:\\ourPFEstatistics\\json'):
        if (file.is_dir() and len(file.name) == 4 and (file.name == 'COMP')):
            domain = file.name
            extract_all(domain)


    print("#################saving #############################")
    print("Number of nodes : "+str(G.number_of_nodes()))
    print("Number of edges  : " + str(G.number_of_edges()))

if __name__ == '__main__':
    main()