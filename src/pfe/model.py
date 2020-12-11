#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 21:02:48 2020

@author: ttrollie
"""

import numpy as np
from numpy import random

from pfe.misc.log import Log, Pretty
from pfe.misc.style import gray, magenta, strike, bold


def proba_rand(b, e, nodes_by_communities, q):
    sum_d_q = len(e[q])
    nb_n_q = len(nodes_by_communities[q])
    return b * nb_n_q / (sum_d_q + b * nb_n_q)


# =============================================================================
# Without cliques
# =============================================================================

def graphe_init(n0, N, qm):
    if n0 < qm:
        raise NameError('n0 must be higher or equal to the number of communities.')

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
        nodes_by_communities[nn % qm].append(nn)
        Q.append(nn % qm)
    return d, e, vlist, Q, nodes_by_communities, nb_edges


def Dynamic_Community_Thibaud(n0, alpha, M, P, b, N):
    '''Compute a graph following the model proposed by Thibaud,
    i.e. with pve=0, 1 seul evenement, ...
    n0 : initial graph
    alpha : probability to add a node (alone)
    M : vector ofprobability to belong to a community
    P : matrice of collaboration
    b : proba to chose a node u is deg(u)+b
    N : number of nodes of the final graph

    qm : number of communities
    '''

    qm = len(P)
    list_of_communities = list(range(qm))

    if alpha > 1 or alpha < 0:
        raise NameError('alpha n\'est pas entre 0 et 1.')
    if len(M) != qm:
        raise NameError('M n\'est pas de la bonne forme.')
    for i in range(qm):
        if len(P[i]) != qm:
            raise NameError('P n\'est pas carré !')

    if sum([sum([P[i][j] for j in range(qm)]) for i in range(qm)]) != 1:
        raise NameError('P n\'est pas bien normalisée !')
    if sum(M) != 1:
        raise NameError('M n\'est pas bien normalisé !')

    d, e, vlist, Q, nodes_by_communities, nb_edges = graphe_init(n0, N, qm)
    #    list_of_nodes = list(range(n0))
    couples_of_communities = list(range(qm * qm))

    #    new_P = [[P[i][j] * M[i] * M[j] for j in range(qm)] for i in range(qm)]
    new_P = P
    new_P_list = []
    for i in range(qm):
        new_P_list += new_P[i]
    new_P_list = np.array(new_P_list) / sum(new_P_list)

    nb_n = n0 - 1
    while nb_n != N - 1:
        rand1 = np.random.random()
        #        print(rand1<alpha)
        if rand1 < alpha:
            nb_n += 1
            qn = np.random.choice(list_of_communities, p=M)
            Q.append(qn)
            #            list_of_nodes.append(nb_n)
            nodes_by_communities[qn].append(nb_n)

        else:

            case = np.random.choice(couples_of_communities, p=new_P_list)
            q1 = int(case / qm)
            q2 = case - int(case / qm) * qm

            if np.random.random() < proba_rand(b, e, nodes_by_communities, q1):
                u = np.random.choice(nodes_by_communities[q1])
            else:
                u = e[q1][int(len(e[q1]) * np.random.random())]
            #                print('u',u)

            if np.random.random() < proba_rand(b, e, nodes_by_communities, q2):
                v = np.random.choice(nodes_by_communities[q2])
            else:
                v = e[q2][int(len(e[q2]) * np.random.random())]
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


def graphe_init_cliques(n0, N, qm):
    '''Initialize with a graph of n0 nodes with no edges and reparted
    equally between communities (node 0 in community 0, 1 in 1, ...)
    Return some values needed for the function of the model.
    '''

    if n0 < qm:
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
        nodes_by_communities[nn % qm].append(nn)
        Q.append(nn % qm)

    return d, e, vlist, Q, nodes_by_communities, list_of_hyperedges


def random_taille_multiedge(distrib, moy, ecart_type):
    '''Distribution H(h) giving the probability for a multiedge to have h nodes.'''
    if distrib == 'Gaussian':
        H = round(np.random.normal(loc=moy, scale=ecart_type))
    else:
        raise NameError('La distribution pour tirer H n\'est pas connue.')
    return H


def separate_H(H, q1, q2, M):
    count = 0
    for h in range(H):
        if np.random.random() < M[q1] / (M[q1] + M[q2]):
            count += 1
    return count, H - count


def number_of_nodes_random(distrib, moy, ecart_type):
    '''Distribution H(h) giving the probability for a multiedge to have h nodes.'''
    if distrib == 'Gaussian':
        H = round(np.random.normal(loc=moy, scale=ecart_type))
    else:
        raise NameError('La distribution pour tirer H n\'est pas connue.')
    return H


def Dynamic_Community_with_cliques(n0, pv, pve, M, P, gamma, N, distrib='Gaussian', moy=5, ecart_type=2):
    '''
    Compute a graph following the model with communities, 
    i.e. with pve=0, 1 seul evenement, ... '''  # TO CHECK!
    '''
    n0 : initial graph
    pv : probability to add a node alone 
    pv : probability to add a node + an edge
    M : vector ofprobability to belong to a community
    P : matrice of collaboration
    gamma : proba to chose a node u is deg(u)+gamma
    N : number of nodes of the final graph

    qm : number of communities
    d : list of the degrees of each nodes (size N)
    e : list of list, each list corresponds to one community, and 
        contains a list of nodes repeated as their degrees; useful to pick 
        randomly a node depending of its degree (size qm)
    vlist : list of the labels of hyperedges associated to each nodes (v[0] is
        the list of the label of the hyperedges the node 0 belongs to; the 
        correspondance between the label and the hyperedges can be found using
        list_of_hyperedges)
    list_of_hyperedges : list of all the hyperedges of the graph.
    Q : Q[i] is the community of the node i
    nodes_by_communities : list of list, each list contains the nodes of 
        a given community.
    '''

    qm = len(P)
    list_of_communities = list(range(qm))
    couples_of_communities = list(range(qm * qm))

    if pv > 1 or pv < 0:
        raise NameError('pv n\'est pas entre 0 et 1.')
    if pve > 1 or pve < 0:
        raise NameError('pve n\'est pas entre 0 et 1.')
    if len(M) != qm:
        raise NameError('M n\'est pas de la bonne forme.')
    for i in range(qm):
        if len(P[i]) != qm:
            raise NameError('P n\'est pas carré !')

    if sum([sum([P[i][j] for j in range(qm)]) for i in range(qm)]) != 1:
        raise NameError('P n\'est pas bien normalisée !')
    if sum(M) != 1:
        raise NameError('M n\'est pas bien normalisé !')

    d, e, vlist, Q, nodes_by_communities, list_of_hyperedges = graphe_init_cliques(n0, N, qm)

    #    new_P = [[P[i][j] * M[i] * M[j] for j in range(qm)] for i in range(qm)]
    new_P = P
    new_P_list = []
    for i in range(qm):
        new_P_list += new_P[i]
    new_P_list = np.array(new_P_list) / sum(new_P_list)

    nb_n = n0 - 1
    while nb_n != N - 1:
        rand1 = np.random.random()
        if rand1 < pv:  # addition of a node alone
            nb_n += 1
            qn = np.random.choice(list_of_communities, p=M)
            Q.append(qn)
            nodes_by_communities[qn].append(nb_n)

        elif rand1 < pv + pve:  # addition of a node + an edge
            '''TODO'''
            raise NameError("pve case is not treated yet.")

        else:  # addition of an edge

            case = np.random.choice(couples_of_communities, p=new_P_list)
            q1 = int(case / qm)
            q2 = case - int(case / qm) * qm

            #            H = max(2, random_taille_multiedge(distrib, moy, ecart_type))
            #            (h1,h2) = separate_H(H,q1,q2,M)

            h1 = number_of_nodes_random(distrib, moy, ecart_type)
            h2 = number_of_nodes_random(distrib, moy, ecart_type)

            h1list = []
            for hh in range(h1):
                if np.random.random() < proba_rand(gamma, e, nodes_by_communities, q1):
                    # determine if we pick completely randomly because of gamma...
                    u = np.random.choice(nodes_by_communities[q1])
                else:  # or according to the degree
                    u = e[q1][int(len(e[q1]) * np.random.random())]
                h1list.append(u)

            h2list = []
            for hh in range(h2):
                if np.random.random() < proba_rand(gamma, e, nodes_by_communities, q2):
                    v = np.random.choice(nodes_by_communities[q2])
                else:
                    v = e[q2][int(len(e[q2]) * np.random.random())]
                h2list.append(v)

            list_of_hyperedges.append(h1list + h2list)
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

    return nodes_by_communities, Q, vlist, d, list_of_hyperedges


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting.')

    with log.info('Generating a graph.'):
        parameters = dict(
            n0=10,
            pv=0.3,
            pve=0.,
            P=[[0.25, 0.25], [0.25, 0.25]],
            M=[0.5, 0.5],
            N=10**3,
            gamma=20,
            distrib='Gaussian',
            moy=2,
            ecart_type=0,
        )

        with log.info('Parameters.'):
            for key, value in parameters.items():
                log.info(f'{str(magenta | key):<20} = {value}')

        data = Dynamic_Community_with_cliques(**parameters)

        with log.info('Generated.'):
            for i, x in enumerate(data, start=1):
                log.info(f'{magenta | i}: {repr(x)}')
