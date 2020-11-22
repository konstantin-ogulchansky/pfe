'''' This code was used to compare different distrubtions in order to find the distribution of values in the SBM matrix'''

import matplotlib.pylab as plt
import numpy as np
import json
import seaborn as sns
import pandas as pd
import statistics as ss
from distfit import distfit
import scipy
import scipy.stats
import time

dist_names = ['norm', 'beta','gamma', 'pareto', 't', 'lognorm', 'invgamma', 'invgauss',  'loggamma', 'alpha', 'chi', 'chi2']

sse = np.inf
sse_thr = 0.10

import os
from log_binning import *

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
import seaborn as sns
dist=json.load( open( "Listlabex.json" ) )

def removeOutliers(x, outlierConstant=5):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    for y in a.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
    return resultList

bin=[]

for i in np.arange(min(dist)-0.05,max(dist)+0.05,0.05):
    bin.append(i)
def drawdist(L,year,title):
    # c = Counter(L)
    #
    #
    # plt.hist(L,bins=range(max(L)+2))
    # print(max(L))
    #
    # plt.xlabel("i")
    # plt.ylabel("F(i)")
    # plt.title("Distribution of # publis "+ year)
    # if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\DsitPublis"  ):
    #     os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\DsitPublis")
    # plt.savefig("D:\\Internship\\Codes\\stats\\Plots\\DsitPublis\\"+year)
    # plt.close()
    # plt.clf()
    # plt.close()
    if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\DsitPublisfitforcom"  ):
        os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\DsitPublisfitforcom")
    export_log_pl(list(L), "AuthPubDist",title)
def gaussian(x, mean, amplitude, standard_deviation):
    return amplitude * np.exp( - ((x - mean) / standard_deviation) ** 2)


def buildHistogram(matrix):
#     h,b= np.histogram(matrix)
#     print(h)
#     print(b)
    fig = plt.figure(figsize=(15, 15))


    plt.rcParams['axes.labelsize'] = 40
    plt.rcParams['axes.titlesize'] = 40

    plt.tick_params(labelsize=40)
    bin_heights, bin_borders, _=plt.hist(matrix,bins=bin,label="Histogram")
    bin_centers = bin_borders[:-1] + np.diff(bin_borders) / 2
    popt, _ = curve_fit(gaussian, bin_centers, bin_heights, p0=[1., 0., 1.],maxfev=1000)

    x_interval_for_fit = np.linspace(bin_borders[0], bin_borders[-1], 10000)
    # plt.plot(x_interval_for_fit, gaussian(x_interval_for_fit, *popt), label='fit')



    # plt.boxplot(matrix)
    plt.xlabel("Probability")
    plt.ylabel("Frequency")
    plt.title("Distribution of the augmentation of probability - ALL",fontsize=25)
    plt.legend(loc='upper left',fontsize=30)
    # fig.text(0.5, 0.8, "Mean : " + str(round(ss.mean(dist),2))+" variance : " + str(round(ss.variance(dist),2))+" Median : " + str(round(ss.median(dist),2)), color='b', fontsize=24)


    plt.savefig("D:\\Internship\\Codes\\stats\\Plots\\Fitalllistlabex\\Distribution of the augmentation of probability ALL")
    plt.clf()
    plt.close()

# buildHistogram(removeOutliers(list(dist)))
data=dist

y, x = np.histogram(data,density=True,bins=bin)


x = (x + np.roll(x, -1))[:-1] / 2.0
for name in dist_names:
    # Modéliser
    ds = getattr(scipy.stats, name)
    param = ds.fit(data)
    # Paramètres
    loc = param[-2]
    scale = param[-1]
    arg = param[:-2]
    # PDF
    pdf = ds.pdf(x, *arg, loc=loc, scale=scale)
    # SSE
    model_sse = np.sum((y - pdf)**2)
    print((name,np.round(model_sse,2)))
    ##############################################
    plt.figure(figsize=(12, 8))
    plt.plot(x, pdf, label=name, linewidth=2)
    plt.plot(x, y, alpha=0.6, label="histogram")
    plt.title("All without outliers  - fit name : " +name + " SSE = " + str(np.round(model_sse, 2)))
    plt.legend()
    if not os.path.exists("D:\\Internship\\Codes\\stats\\Plots\\Fitalllistlabex"):
        os.makedirs("D:\\Internship\\Codes\\stats\\Plots\\Fitalllistlabex")
    m="D:\\Internship\\Codes\\stats\\Plots\\Fitalllistlabex\\"+name
    plt.savefig(m)
    plt.close()
    # Si le SSE est ddiminué, enregistrer la loi
    if model_sse < sse :
        best_pdf = pdf
        sse = model_sse
        best_loc = loc
        best_scale = scale
        best_arg = arg
        best_name = name

    # Si en dessous du seuil, quitter la boucle
    # if model_sse < sse_thr :
    #     break

buildHistogram(removeOutliers(dist))
