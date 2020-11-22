#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:02:48 2020

@author: ttrollie
"""

import numpy as np
from matplotlib import pyplot as plt
import time
from numpy import random
from scipy.optimize import curve_fit
import Graph_study as gs
import json





def graphe_init(n0,N,qm):

    if n0<qm:
        raise NameError('n0 must be higher than the number of communities.')

#    d = [2 for i in range(n0)] + [0 for i in range(n0,N)]
#    e = [i for i in range(n0)] + [i for i in range(n0)]
#    vlist = [[1,n0-1]] + [[i-1,i+1] for i in range(1,n0-1)] + [[n0-2,0]] + [[] for i in range(n0,N)]
#    len_e = 2*n0
#    return d, e, vlist, len_e

    d = [0 for i in range(N)]
    e = [[] for i in range(qm)]
    vlist = [[] for i in range(N)]
    nb_edges = 0

#    Q = list(range(qm))
    Q = []
    nodes_by_communities = [[] for i in range(qm)]
    for nn in range(n0):
        nodes_by_communities[nn%qm].append(nn)
        Q.append(nn%qm)
    return d, e, vlist, Q, nodes_by_communities, nb_edges


#def proba_rand(alpha, a, b, nb_n, nb_edges): 
##    return b * alpha / (a * (1-alpha) + b * alpha)
#    return b * nb_n / (a * nb_edges + b * nb_n)

def proba_rand(alpha, b, e, nodes_by_communities, q):
    sum_d_q = len(e[q])
    nb_n_q = len(nodes_by_communities[q])
    return b * nb_n_q / (sum_d_q + b * nb_n_q)



# =============================================================================
# Without cliques
# =============================================================================


def Dynamic_Community(n0, alpha, M, P, a, b, N):
    ''''''

    qm = len(P)
    list_of_communities = list(range(qm))
    
    if alpha>1 or alpha<0:
        raise NameError('alpha n\'est pas entre 0 et 1.')
    if len(M)!= qm:
        raise NameError('M n\'est pas de la bonne forme.')
    for i in range(qm):
        if len(P[i])!=qm:
            raise NameError('P n\'est pas carré !')

    if sum([sum([P[i][j] for j in range(qm)]) for i in range(qm)]) != 1 :
        raise NameError('P n\'est pas bien normalisé !')
    if sum(M) != 1 :
        raise NameError('M n\'est pas bien normalisé !')
        

    d, e, vlist, Q, nodes_by_communities, nb_edges = graphe_init(n0,N, qm)
#    list_of_nodes = list(range(n0))
    couples_of_communities = list(range(qm*qm))

#    new_P = [[P[i][j] * M[i] * M[j] for j in range(qm)] for i in range(qm)]
    new_P = P
    new_P_list = []
    for i in range(qm):
        new_P_list += new_P[i]
    new_P_list = np.array(new_P_list)/sum(new_P_list)

    nb_n = n0-1
    while nb_n!=N-1:
        rand1 = np.random.random()
#        print(rand1<alpha)
        if rand1<alpha:
            nb_n += 1
            qn = np.random.choice(list_of_communities, p=M)
            Q.append(qn)
#            list_of_nodes.append(nb_n)
            nodes_by_communities[qn].append(nb_n)

        else:
            
            case = np.random.choice(couples_of_communities, p = new_P_list)
            q1 = int(case / qm)
            q2 = case - int(case / qm) * qm
            
#            print(q1,q2)

#            print(proba_rand(alpha, a, b, e, nodes_by_communities, q1))
            if np.random.random() < proba_rand(alpha, a, b, e, nodes_by_communities, q1):
                u = np.random.choice(nodes_by_communities[q1])
            else:
                u = e[q1][int(len(e[q1])*np.random.random())]
#                print('u',u)

            if np.random.random() < proba_rand(alpha, a, b, e, nodes_by_communities, q2):
                v = np.random.choice(nodes_by_communities[q2])
            else:
                v = e[q2][int(len(e[q2])*np.random.random())]
#                print('v',v)

            vlist[u].append(v)
            vlist[v].append(u)
            e[q1].append(u)
            e[q2].append(v)
            d[u] += 1
            d[v] += 1

            nb_edges += 1
#            print(e)


#    vlist = [sorted(list(set(x).difference([i]))) for i,x in enumerate(vlist)]
#    d = [len(x) for x in vlist]


    return (nodes_by_communities, Q, new_P, vlist, d)


# =============================================================================
# With cliques
# =============================================================================




def graphe_init_cliques(n0,N,qm):

    if n0<qm:
        raise NameError('n0 must be higher than the number of communities.')

#    d = [2 for i in range(n0)] + [0 for i in range(n0,N)]
#    e = [i for i in range(n0)] + [i for i in range(n0)]
#    vlist = [[1,n0-1]] + [[i-1,i+1] for i in range(1,n0-1)] + [[n0-2,0]] + [[] for i in range(n0,N)]
#    len_e = 2*n0
#    return d, e, vlist, len_e

    d = [0 for i in range(N)]
    e = [[] for i in range(qm)]
    vlist = [[] for i in range(N)]
    list_of_hyperedges = []

#    Q = list(range(qm))
    Q = []
    nodes_by_communities = [[] for i in range(qm)]
    for nn in range(n0):
        nodes_by_communities[nn%qm].append(nn)
        Q.append(nn%qm)
    
    return d, e, vlist, Q, nodes_by_communities, list_of_hyperedges

    

def random_taille_multiedge(distrib, moy, ecart_type):
    if distrib=='Gaussian':
        H = round(np.random.normal(loc=moy,scale=ecart_type))
    else:
        raise NameError('La distribution pour tirer H n\'est pas connue.')
    return H


def separate_H(H,q1,q2,M):
    count = 0
    for h in range(H):
        if np.random.random() < M[q1] / (M[q1]+M[q2]):
            count += 1
    return count, H-count



def Dynamic_Community_with_cliques(n0, alpha, M, P, b, N, distrib='Gaussian', moy=5, ecart_type=2):
    ''''''

    qm = len(P)
    list_of_communities = list(range(qm))
    couples_of_communities = list(range(qm*qm))

    
    if alpha>1 or alpha<0:
        raise NameError('alpha n\'est pas entre 0 et 1.')
    if len(M)!= qm:
        raise NameError('M n\'est pas de la bonne forme.')
    for i in range(qm):
        if len(P[i])!=qm:
            raise NameError('P n\'est pas carré !')

    # if sum([sum([P[i][j] for j in range(qm)]) for i in range(qm)]) != 1 :
    #     raise NameError('P n\'est pas bien normalisé !')
    # if sum(M) != 1 :
    #     raise NameError('M n\'est pas bien normalisé !')
        

    d, e, vlist, Q, nodes_by_communities, list_of_hyperedges = graphe_init_cliques(n0,N, qm)
#    list_of_nodes = list(range(n0))

#    new_P = [[P[i][j] * M[i] * M[j] for j in range(qm)] for i in range(qm)]
    new_P = P
    new_P_list = []
    for i in range(qm):
        new_P_list += new_P[i]
    new_P_list = np.array(new_P_list)/sum(new_P_list)

    nb_n = n0-1
    while nb_n!=N-1:
        rand1 = np.random.random()
#        print(rand1<alpha)
        if rand1<alpha:
            nb_n += 1
            qn = np.random.choice(list_of_communities, p=M)
            Q.append(qn)
#            list_of_nodes.append(nb_n)
            nodes_by_communities[qn].append(nb_n)

        else:
            
            case = np.random.choice(couples_of_communities, p = new_P_list)
            q1 = int(case / qm)
            q2 = case - int(case / qm) * qm
            
            H = max(2, random_taille_multiedge(distrib, moy, ecart_type))
            (h1,h2) = separate_H(H,q1,q2,M)

            h1list = []
            for hh in range(h1):
                if np.random.random() < proba_rand(alpha, b, e, nodes_by_communities, q1):
                    u = np.random.choice(nodes_by_communities[q1])
                else:
                    u = e[q1][int(len(e[q1])*np.random.random())]
    #                print('u',u)
                h1list.append(u)

            h2list = []
            for hh in range(h2):
                if np.random.random() < proba_rand(alpha, b, e, nodes_by_communities, q2):
                    v = np.random.choice(nodes_by_communities[q2])
                else:
                    v = e[q2][int(len(e[q2])*np.random.random())]
    #                print('v',v)
                h2list.append(v)

            list_of_hyperedges.append(h1list+h2list)
            hyperedge_nb = len(list_of_hyperedges)
            for u in h1list:
                vlist[u].append(hyperedge_nb)
                d[u] += 1
                e[q1].append(u)
            for v in h2list:
                vlist[v].append(hyperedge_nb)
                d[v] += 1
                e[q2].append(v)

#    vlist = [sorted(list(set(x).difference([i]))) for i,x in enumerate(vlist)]
#    d = [len(x) for x in vlist]

    return (nodes_by_communities, Q, new_P, vlist, d, list_of_hyperedges)








# =============================================================================
# Execution
# =============================================================================

n0 = 21
alpha = 0.1
#M = 
#P = 
b = 1

N2013=170745
N2018=257281
N=N2013
#P = [[0.25,0.25],[0.25,0.25]]
#M = [0.5,0.5]
matrice2018=json.load( open( "Matrice 2018.json" ) )
matrice2013=json.load( open( "Matrice 2013.json" ) )
vectorM=json.load( open( "Vector M.json" ) )
P = matrice2013
M = vectorM

#P = [[0.5,0.],[0.,0.5]]
#M = [0.5,0.5]

#P = [[1.]]
#M = [1.]

qm = len(M)

#M = [1/qm for i in range(qm)]
#P = [[0 for i in range(qm)] for j in range(qm)]
#for i in range(qm):
#    P[i][i]=1/qm


#M = np.array(M)/sum(M)

norm = sum([sum([P[i][j] for j in range(qm)]) for i in range(qm)])
for i in range(qm):
    for j in range(qm):
        P[i][j] = P[i][j] / norm




#(nodes_by_communities, Q, new_P, vlist, d) = Dynamic_Community(n0, alpha, M, P, a, b, N)
(nodes_by_communities, Q, new_P, vlist, d, list_of_hyperedges) = Dynamic_Community_with_cliques(n0, alpha, M, P, b, N, distrib='Gaussian', moy=4.55, ecart_type=16.05)

ind, hist = gs.histo(d)
gs.plot_d(ind,hist, a = 1.5, cut_beggining = 8, cut_end = 'end')


#Z = [(a * (1-alpha) * sum([new_P[q][q2]+new_P[q2][q] for q2 in range(qm)]) + alpha * b * M[q]) for q in range(qm)]
#kappa = sum([sum([new_P[q1][q2] * (a/Z[q1] + a/Z[q2]) for q2 in range(qm)]) for q1 in range(qm)])
#alpha_th = 1 + 1/((1-alpha)*kappa)
#print('alpha theorique :', alpha_th)



#B = [b/a*M[q]*alpha for q in range(qm)]
#alpha_th_2 = 1 + 1 / (sum([1/(1+ B[q]/((1-alpha)*sum([P[q1][q]+P[q][q1] for q1 in range(qm)]))) for q in range(qm)]))
#print('alpha theo 2', alpha_th_2)




#alpha_th_3 = 2 + (b/a)*M[0]*alpha / (2*(1-alpha)*(sum([P[0][q] for q in range(qm)]))) 
#print('alpha theo correct', alpha_th_3)
#plt.loglog([10,1000],[xx**(-alpha_th_3)*np.exp(12) for xx in [10,1000]], label='a la main')
#gs.plot_d(ind,hist, a = 1.5, cut_beggining = 5, cut_end = 'end')




