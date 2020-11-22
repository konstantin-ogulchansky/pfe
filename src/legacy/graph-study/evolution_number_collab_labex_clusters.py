import matplotlib.pylab as plt
import numpy as np
import json
import os
from pylab import *

'''' This code was used to build the evolution of the number of collaborations between labex clusters'''

labextitles={"5-8":"Student: E. KOFMAN - Supervisor 1: R.DE-SIMONE - Supervisor 2: F.VERDIER - Thesis topic:'Active and Passive Inference of Network Neutrality'","4-10":"Student: A. KADAVANKANDY - Supervisor 1: K. Avrachenkov - Supervisor 2: L. Cottatellucci  - Thesis topic:' Random matrix analysis for distributed algorithms and complex networks'","a":"Student: L. VIGNERI - Supervisor 1: T. Spyropoulos- Supervisor 2: C.Barakat - Thesis topic:'  Vehicles as a Mobile Cloud : Leveraging Mobility for Content Storage and Dissemination'","0-15":"Student: V. MASTANDREA - Supervisor 1: L. Henrio - Supervisor 2: C. Laneve - Thesis topic:' Deadlock analysis for concurrent and distributed programing'","4-15":"Student: H. MYKHAILENKO - Supervisor 1: P. Nain - Supervisor 2: F. Huet - Thesis topic:' Probabilistic Approaches for Big Data Analysis'","2-16":"Student:F. LUGOU - Supervisor 1: L. Apvrille - Supervisor 2: A. Francillon - Thesis topic:'Environnement pour l\'analyse de sécurité d\'objets communicants'","2-14":"Student: N. HUIN - Supervisor 1: F. Giroire - Supervisor 2: D.Lopez - Thesis topic:' Energy-Efficient Software Defined Networks'","7-8":"Student: A. DIHISSOU - Supervisor 1: R.Staraj - Supervisor 2: R. Knopp - Thesis topic:' Système antennaire directif et reconfigurable pour réseaux de capteurs sans fil'","1-12":"Student: E. PALAGI - Supervisor 1: A. Giboin - Supervisor 2: R. Troncy - Thesis topic:' Conception d\’une méthode d\’évaluation des moteurs sémantiques de recherche exploratoire'","2-8":"Student: M. MAHFOUDI - Supervisor 1: W. Dabbous - Supervisor 2:R. Staraj - Thesis topic:' Towards Cross-layer MIMO for 5G networks'","8-15":"Student: V. NGUYEN - Supervisor 1: P. Le Thuc - Supervisor 2: S. Lantéri - Thesis topic:' Small Animals RFID Integrated Antenna Tracking System'","b":"Student: A. Tuholukova - Supervisor 1: T. Spyropoulos - Supervisor 2: G. Neglia - Thesis topic:' Caching at the Edge: Distributed Phy-aware Caching Policies for 5G Cellular Networks'","4-16":"Student: D. POLITAKI - Supervisor 1: S.Alouf - Supervisor 2: F. Hermenier - Thesis topic:' RGreening Data Centers'","5-16":"Student: H. ZHAO - Supervisor 1: F. Mallet - Supervisor 2: L. Apvrille - Thesis topic:' Multi-Level Design for Cyber Physical Systems'"}
labexstart={"5-8":2013,"4-10":2013,"a":2013,"0-15":2013,"4-15":2014,"2-16":2014,"2-14":2014,"7-8":2014,"1-12":2015,"2-8":2015,"8-15":2015,"b": 2016,"4-16":2016,"5-16":2016}
numbcollab={55546759400: 2, 56613081700: 5, 56826065900: 7, 57190883130: 5, 57043755900: 13, 57191505920: 3, 55557927000: 2, 57189376990: 4, 57189034692: 10, 57194446159: 3, 57191328845: 2, 56732733900: 4, 56516772600: 18, 57199220111: 3, 57190576899: 8, 57195638233: 1, 57194761095: 2, 57205481547: 3}
new={55546759400: 2, 56613081700: 5, 56826065900: 7, 57190883130: 5, 57043755900: 13, 57191505920: 3, 55557927000: 2, 57189376990: 4, 57189034692: 10, 57194446159: 3, 57191328845: 2, 56732733900: 4, 56516772600: 18, 57199220111: 3, 57190576899: 8, 57195638233: 1, 57194761095: 2, 57205481547: 3}
numpub={55546759400: 4, "5-8": 3, "4-10":8, "a": 8, 57043755900: 6, "0-15": 3, "4-15": 3, "2-16": 5, "2-14": 10, "7-8": 1, 57191328845: 3, "1-12": 3, "2-8": 7, "8-15": 1, "b": 3, "4-16": 1, "5-16": 1, 57205481547:1}
degree={55546759400: 2, "5-8": 5, "4-10": 7, "a": 5, 57043755900: 13, "0-15": 3, "4-15": 2, "2-16": 4, "2-14": 10, "7-8": 3, 57191328845: 2, "1-12": 4, "2-8": 18, "8-15": 3, "b": 8, "4-16": 1, "5-16": 2, 57205481547: 3}
numbcol={55546759400: 8, "5-8": 7, "4-10": 21, "a": 19, 57043755900: 21, "0-15": 5, "4-15": 6, "2-16": 11, "2-14": 34, "7-8": 3, 57191328845: 6, "1-12": 9, "2-8": 32, "8-15": 3, "b": 15, "4-16": 1, "5-16": 2, 57205481547: 3}
labexyears={"5-8":["2015","2016"],"4-10":["2015","2016","2017","2018"],"a":["2016","2017","2018"],"0-15":["2016","2017"],"4-15":["2017"],"2-16":["2016","2017","2018"],"2-14":["2015","2017","2018"],"7-8":["2017"],"1-12":["2017","2018"],"2-8":["2017","2018"],"8-15":["2018"],"b": ["2016"],"4-16":["2017"],"5-16":["2017"]}

def export_legend(legend, filename="legend.png", expand=[-5,-5,5,5]):
    fig  = legend.figure
    fig.canvas.draw()
    bbox  = legend.get_window_extent()
    bbox = bbox.from_extents(*(bbox.extents + np.array(expand)))
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi="figure", bbox_inches=bbox)
def drawdict2(D,D1,title,x,yy,c1,c2,m1,m2,test):
    fig=plt.figure(figsize=(25,15))
    # figlegend = plt.figure(figsize=(25, 15))
    # ax = fig.add_subplot(111)

    thismanager = plt.get_current_fig_manager()
    thismanager.window.SetPosition = ((500, 0))

    plt.tick_params(labelsize=70)
    plt.rcParams['axes.labelsize'] = 100
    plt.rcParams['axes.titlesize'] = 100

    plt.plot(*zip(*sorted(D1.dict())), linestyle='--', marker='o', color=c2, label=m2, linewidth=10)
    plt.plot(*zip(*sorted(D.dict())), linestyle='--', marker='o', color=c1, label=m1, linewidth=10)

    if(test!=" " and test!="2-7"):
        plt.axvline(x=str(labexstart[test]),label="Start Year - Number of collaborations = "+ str(numbcol[test])+" Nb publis = "+str(numpub[test]),linestyle="dotted",linewidth=10)
        # fig.text(.1,.03,labextitles[test],color='g',fontsize=14)
        for y in labexyears[test]:
            plt.axvline(x=y, linestyle="dashdot", linewidth=4,ymax=0.5)
    if(test=="2-7"):
        plt.axvline(x=str(labexstart["a"]),linewidth=10, label="Start Year - L. VIGNERI - Number of collaborations = "+ str(numbcol["a"])+" Number of publications = "+str(numpub["a"]), linestyle="dotted",color="b")
        for y in labexyears["a"]:
            plt.axvline(x=y, linestyle="dashdot", linewidth=4,ymax=0.5,color="b")
        plt.axvline(x=str(labexstart["b"]),linewidth=10, label="Start Year - A. Tuholukova- Number of collaborations = "+ str(numbcol["b"])+" Number of publications = "+str(numpub["b"]), linestyle="dotted",color="r")
        for y in labexyears["b"]:
            plt.axvline(x=y, linestyle="dashdot", linewidth=4,ymax=0.5,color="r")
        # fig.text(.1, .01, labextitles["a"], color='g', fontsize=14)
        # fig.text(.1, .03, labextitles["b"], color='g', fontsize=14)

    # plt.legend(loc='upper right', bbox_to_anchor=(0.5, -0.05),fancybox=True, shadow=True, ncol=5)
    L=plt.legend()
    export_legend(L)
    # plt.legend(fontsize=30)
    # plt.title(title)

    # plt.xlabel(x,fontsize=70)


    plt.ylabel(yy,fontsize=70)
    plt.xticks(["1990",'1996',"2002","2008", "2018"], visible=True, rotation="horizontal")


    # plt.yticks(np.arange(min(D.values()), max(D.values()) +10, 1.0))



    if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\Evolution of number of number of edges and publications between clusters"  ):
        os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\Evolution of number of number of edges and publications between clusters")
    plt.savefig("D:\\Internship\\Codes\\stats\\Plots\\Evolution of number of number of edges and publications between clusters\\"+title)
    plt.close()
edges=json.load( open( "politakibetterinteredges.json" ) )
pubs=json.load( open( "politakibetterinterpub.json" ) )

x="YEARS"
y="Nb edges/publis"
c1="pink"
c2="purple"
m1="Nb collabs"
m2="Nb publis"
test=" "
for i in range(21):
    for j in range(i + 1, 21):
        if (i != j):

            D = pubs[str(i)+"-"+str(j)]
            D1 = edges[str(i)+"-"+str(j)]
            title = "Evolution of edges+publications between cluster id= " + str(i)+" and cluster id= "+str(j)
            if((str(i)+"-"+str(j)) in labextitles.keys() or (i==2 and j==7) ):
                test=str(i)+"-"+str(j)
            else:
                test=" "
            if (test in labexstart.keys() or test=="2-7"):
                print(str(i) + "-" + str(j))
                drawdict2(D, D1, title, x, y, c1, c2, m1, m2,test)






