import matplotlib.pylab as plt
import numpy as np
import json
import seaborn as sns
import pandas as pd

import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
import seaborn as sns

'''' This code was used to calculate the stochastic block matrix for that u will need 2 files politakibetterinteredges.json and politakibetterintraedges.json.
   These 2 files are in the internship.zip that I sent'''

plotb=[]
bin=[]
i=-2
while(i<=15):
    bin.append(i)
    i+=0.1
np.set_printoptions(threshold=np.inf)

labexstart=["5-8","4-10","2-7","0-15","4-15","2-16","2-14","7-8","1-12","2-8","8-15","4-16","5-16"]


edgesinter=json.load( open( "politakibetterinteredges.json" ) )
edgeintra=json.load( open( "politakibetterintraedges.json" ) )


def Matcalc(year):
    '''' calculate the SBM matrix for a certain year  '''
    somme={}
    for i in range(21):
        somme[i]=0

    for i in range(21):
        for j in range(i , 21):
            if (i != j):
                if(edgesinter[str(i)+"-"+str(j)][year]==0):
                    somme[i]+=0
                else:
                    somme[i]+=edgesinter[str(i)+"-"+str(j)][year]

        somme[i]+=edgeintra[str(i)][year]

    # for i in range(22):
    #     for j in range(i + 1, 22):
    #         if (i != j):
    P = np.zeros( (21, 21))


    for i in range(21):
        for j in range(21):
            if(i!=j):
                if(i<j):
                    if(somme[i]==0):
                        P[i][j]==0
                    else:
                        P[i][j]=edgesinter[str(i)+"-"+str(j)][year]/somme[i]
                else:
                    if (somme[i] == 0):
                        P[i][j] == 0
                    else:
                        P[i][j] = edgesinter[str(j) + "-" + str(i)][year] / somme[i]



            else:
                if (somme[i] == 0):
                    P[i][j] == 0
                else:
                    P[i][j]=edgeintra[str(i)][year]/somme[i]

    return P,somme



P1,somme1=Matcalc("2018")
P2,somme2=Matcalc("2013")
P=P2-P1
M=np.zeros( (21, 21))
global nmbr
nmbr=0
for i in range(21):
    for j in range(21):
        if(P1[i][j]!=0):
            P[i][j]=1-P2[i][j]/P1[i][j]

        else:

            if(P2[i][j]>0):
                P[i][j] =0
                nmbr += 1
            if(P2[i][j]==0):
                P[i][j] =5000


            else:
                nmbr += 1
                P[i][j] = 0


def buildHistogram(matrix):
#     h,b= np.histogram(matrix)
#     print(h)
#     print(b)
    fig = plt.figure(figsize=(20, 20))


    plt.rcParams['axes.labelsize'] = 45
    plt.rcParams['axes.titlesize'] = 45

    plt.tick_params(labelsize=40)
    plt.hist(matrix,bins=bin,cumulative=True,histtype='step')


    # plt.boxplot(matrix)
    plt.xlabel("Probability Augmentation")
    plt.ylabel("Frequency")     
    plt.title("CDF -Formule1 - ALL clusters Div2018")
    # fig.text(0.3, 0.8, "Mean : " + str(round(np.sum(matrix)/(len(matrix)-1),2)), color='b', fontsize=24)


    plt.savefig("CDF -Formule1 - ALL clusters Div2018")
    plt.clf()
    plt.close()

V=[]

def boxp(data):
    '''' this funtion was used to build the box plots '''
    fig, ax = plt.subplots(figsize=(20, 20))
    plt.rcParams['axes.labelsize'] = 45
    plt.rcParams['axes.titlesize'] = 45

    plt.tick_params(labelsize=40)
    data1=data[0]
    data2=data[1]
    # plt.xlabel("Probability Augmentation")
    plt.ylabel("Probability Augmentation")
    plt.title("Plot box-Formule1 - LABEX+All clusters div2018" )
    bp1 = ax.boxplot(data1,positions=[1],  notch=True, widths=0.35,
                     patch_artist=True, boxprops=dict(facecolor="C0"))
    bp2 = ax.boxplot(data2,positions=[2], notch=True, widths=0.35,
                     patch_artist=True, boxprops=dict(facecolor="C2"))

    ax.legend([bp1["boxes"][0], bp2["boxes"][0]], ['ALL Clusters', 'Labex Clusters'], loc='upper right',fontsize=40)
    ax.set_ylim([-6, 2],)

    ax.set_xlim(0, 6)
    plt.savefig("Plot box-Formule1 - LABEX+All clusters div2018 with ylim [-6,2]")
    plt.clf()

    plt.close()

for n in labexstart:
    c1=n.split('-')[0]
    c2=n.split('-')[1]
    V.append(P[int(c2)][int(c1)])

#     print(np.round(P[int(c2)][int(c1)],2))
# #
# # A=P.flatten()
# # c=len(A)-nmbr
# print(nmbr)
# buildHistogram(P.flatten())
# plotb.append(P.flatten())
# plotb.append(V)
# boxp(plotb)



# fig=plt.figure(figsize=(25,30))
# ax=fig.add_subplot(111)
# ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
# ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
# ax.add_patch(Rectangle((21, 21), 1, 1, edgecolor='black', fill=False, lw=3))
#
# plt.matshow(P, cmap=cm.Spectral_r)
#
# plt.colorbar()
# plt.show()
# plt.savefig("HEATMAP2018-2013")
# plt.close()
# np.set_printoptions(precision=3)
# print(np.mean(sum(V)/len(V)))
##############################################################"
# for n in labexstart:
#     c1=n.split('-')[0]
#     c2=n.split('-')[1]
#     print(n+" : "+str(P[int(c1)][int(c2)])+" / "+str(P[int(c2)][int(c1)]))
# # part=json.load( open( "bettersortedpartition2018.json" ) )
# #
# nnodes=len(part)
# M=[]
# v=0
# for i in range(21):
#     c=len([k for k, v in part.items() if v == i])
#     v+=c/nnodes
#     M.append(c/nnodes)
# print(v)
# np.savetxt("VectorM2018.txt",np.asarray(M),fmt='%1.1e')
#

# fig = plt.figure(figsize=(28, 20))
# sns.set(font_scale=1.8)
# g = sns.heatmap(P2.round(2),cmap="cubehelix",annot=True)
# ax = g.axes
# for n in labexstart:
#     c1=n.split('-')[0]
#     c2=n.split('-')[1]
#     ax.add_patch(Rectangle((int(c1), int(c2)), 1, 1, fill=False, edgecolor='red', lw=3))
# plt.savefig("Matrix 2013")
# plt.show()
def deleteFrom2D(arr2D, row, column):
    'Delete element from 2D numpy array by row and column position'
    modArr = np.delete(arr2D, row * arr2D.shape[1] + column)
    return modArr

lis=[]
pairs=[]
for n in labexstart:
    c1=n.split('-')[0]
    c2=n.split('-')[1]
    pairs.append((int(c1),int(c2)))
for i in range(21):
    for j in range(21):
        if(not((i,j) in pairs)):
            lis.append(P[i][j])


# json.dump(P1.tolist(), open("Matrice 2018.json", 'w'))
# json.dump(P2.tolist(), open("Matrice 2013.json", 'w'))

x=[]
y=[]
for i in range(21):
    for j in range(i, 21):
        if (i != j ):
            x.append(edgesinter[str(i)+"-"+str(j)]["2013"])
            y.append(edgesinter[str(i)+"-"+str(j)]["2018"]-edgesinter[str(i)+"-"+str(j)]["2013"])

fig, ax = plt.subplots(figsize=(20, 20))
plt.scatter(x,y)
plt.xlabel('AB[2013]', fontsize=25)
plt.ylabel('AB[2018]-AB[2013]', fontsize=25)
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
# ax.set_ylim([-2, 1.5])
plt.title("#edges[2018]-#edges[2013]/# edges between clusters in 2013",fontsize=25)
plt.savefig("AB(2018)-AB(2013) + AB(2013)")
listP=[]
# for i in range(0,21):
#     for j in range(0,21):
#         if(P[i][j]!=5000):
#             )

for n in labexstart:
    c1=n.split('-')[0]
    c2=n.split('-')[1]
    if (P[int(c1)][int(c2)] != 5000):
        listP.append(P[int(c1)][int(c2)])
json.dump(listP, open("Listlabex.json", 'w'))