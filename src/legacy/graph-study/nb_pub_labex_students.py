import os
import sys
import json
import time
import traceback
import networkx as nx
import community as cm
import collections
import math
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import rcParams
import random

# trackauth=[23392711700,8905960300,6603178468,7003638977,24765908100,53880298500,7003954863,55884599100,57200498082,6603550679,6602188705,55888328400,7006015230,6603827744,7006945745,55885318000,57203999691,7004269287,12545018500,56211628500,55887022200,55902164500,56343725100,6603671578,11339046600]
count1=0
count2=0 
enc1=7003638977
enc2=6603178468
doc=57205481547
trackauth=[25929341100,8976201700,57205481547,57195638233,15061529900,6701836992,56516772600,6602211855,35583036400,14021020300,55888328400,23977126600,57190576899,57189034692,55557927000,7006929810,11339046600,23392711700,8905960300,6603178468,7003638977,24765908100,7003954863,55884599100,57200498082,6603550679,55546759400,56613081700,57191622205,56826065900,57190883130,57043755900,57191505920]
authtk=[23392711700,6603178468]
te=[(7003638977,55546759400),(6603178468,55546759400),(55546759400,7003638977),(55546759400,6603178468)]
te2=[(56613081700,11339046600),(7006929810,11339046600),(56613081700,11339046600),(7006929810,11339046600)]
currpub=set([doc,enc1,enc2])
bothenc=0
nb_pub1={doc:0}
nb_pub2={doc:0}
G = nx.Graph()
affiliation_city = {}
auth_city = {}
city = {}
cities = set()
auth_name = {}
auth_pub={}
todelete=set()

def debug(x, end = '\n'):
    sys.stderr.write(x)
    sys.stderr.write(end)


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
        if (type(aff) is list):
            for a in aff:
                if(a.get('afid') and a.get('affiliation-city') and a.get('affiliation-country') and a['affiliation-country'].lower()=='france'):
                    affid = int(a['afid'])
                    affiliation_city[affid] = a['affiliation-city'].lower()
        else:
            if(aff.get('afid') and aff.get('affiliation-city') and aff.get('affiliation-country') and aff.get('affiliation-country').lower()=='france'):
                affid = int(aff['afid'])
                affiliation_city[affid] = aff['affiliation-city'].lower()

        # if that entry doesn't have an author ==> it's not a paper
        if (not paper.get('author')):
            continue

        authors = paper['author']

        # if there is only 1 author, ignore this paper
       
                

        if (not type(authors) is list):
            continue
        else:
            comp=set()
            
            for i in range(len(authors)):
                comp.add(int(authors[i]['authid'])) 
            if(len(comp.intersection(currpub))==3):
                bothenc+=1

              
            

            for i in range(len(comp)):
                u = int(list(comp)[i])
                
                for j in range(i):
                    v = int(list(comp)[j])

                    # since we are looping over the same array, we should skip this case
                    
                    #if ((v,u) not in pairs and (u,v) not in pairs):
                        
                                            # undirected graph ==> (u,v) == (v, u)
                        # to store only 1/2 of the memory
                        # we will always use key (u,v) such as u is smaller than v
                    #u, v = min(u, v), max(u, v)

                        # checking if edge already exists
                    if G.has_edge(u, v):
                            # update the edge weight
                        G[u][v]['weight'] += 1
                    else:
                        G.add_edge(u, v, weight = 1)
            comp.clear()


    return G.number_of_nodes(), len(papers)



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
    global bothenc
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
        bothenc=0
        if filename.endswith('.json'):

            domain = filename[:4]
            year = filename[5:9]

            data = extract_data_from_json(filename, domain)
            if(data == None):
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
  




    # export_graphml("whole_graph_" + domain + ".graphml", '')

def export_stats(filename, domain):
    global count1
    global count2
    global bothenc
    # dictionary = {1: 27, 34: 1, 3: 72, 4: 62, 5: 33, 6: 36, 7: 20, 8: 12, 9: 9, 10: 6, 11: 5,
    #               12: 8, 2: 74, 14: 4, 15: 3, 16: 1, 17: 1, 18: 1, 19: 1, 21: 1, 27: 2}
    # plt.bar(list(auth_pub.keys()), auth_pub.values(), color='g')
    # plt.show()

    ######################### Calculating Data ########################################################

    var=0
    if not os.path.exists('stats'):
        os.makedirs('stats')

    dir = 'stats\\' + domain
    if(G.has_edge(doc,enc1 )):
        nb_pub1[doc]=G[doc][enc1]['weight']-count1
        count1+=nb_pub1[doc]
    if(G.has_edge(doc,enc2)):
        var=G[doc][enc2]['weight']
        
        nb_pub2[doc]=G[doc][enc2]['weight']-count2
        count2+=nb_pub2[doc]
    if not os.path.exists(dir):
        os.makedirs(dir)

    sys.stdout = open(dir + '\\' + "statsFile_" + "number of publicationsGOGUNSKA Karyna  ENGI" + ".log", "a")
    print("--------------------------------------------------------------------"+filename+"-------------------------------------------------------------------------")
    print("Number of pubs of GOGUNSKA Karyna  with 2 sups are: ",bothenc)
    print("Number of pubs of GOGUNSKA Karyna with first sup are: ",nb_pub1[doc])
    print("Number of pubs of GOGUNSKA Karyna  with second sup are: ",nb_pub2[doc])
    


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
    partition=0
    nbr_partitions=0
    execution_time=0
    mod=0

    return partition, nbr_partitions, mod, execution_time



def Union(lst1, lst2):
    final_list = list(set(lst1) | set(lst2))
    return final_list
def drawdict(D,D1,D2):
    plt.figure(figsize=(20,10))
    plt.plot(*zip(*sorted(D.dict())), linestyle='--', marker='o', color='red', label="Comodularity: the difference between the modularity of the parition given by louvain (Modularity 1), and the modularity of the partition that merges fredric's and guillaume's clusters(Modularity 2)")
    plt.plot(*zip(*sorted(D1.dict())), linestyle='--', marker='o', color='yellow', label="Modularity 1")
    plt.plot(*zip(*sorted(D2.dict())), linestyle='--', marker='o', color='green', label='Modularity 2')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)
    plt.title("comodularity plot")
    plt.xlabel("Years")
    plt.ylabel("Modularity")
    plt.savefig("COMODULARITY")

def drawlist(L):

def main():
    # domain = input()
    directory = 'D:\\ourPFEstatistics\\json'

    for file in os.scandir(directory):
        if(file.is_dir() and len(file.name) == 4 and (file.name == 'ENGI')):
            domain = file.name
            extract_all(domain)
            G.clear()
    # print(cities)
    # print(cities)
    # print(len(cities))
    with open('cities.csv', 'w') as f:
        for key in city.keys():
            f.write("%s,%s\n" % (key, city[key]))



if __name__ == '__main__':
    main()