import numpy as np
from matplotlib import pyplot as plt
import time
from scipy.optimize import curve_fit
from scipy import stats
import math

def histo(d_out):
    '''Création de l'histogramme (degree distribution) à partir d'une liste de degrés.
    
    d_out : liste de degrés.
    indice : abscisse de l'histogramme.
    hist : ordonnée de l'histogramme (ie nombre de fois où la valeur d'absisse apparait dans d_out.'''

    hist = {key:0 for key in set(d_out)}
    for d in d_out:
        hist[d] += 1
    return list(hist.keys()), list(hist.values())



########################
### Logarithmic binning


def log_binning(x,y,a=1.5):
    '''Retourne le binning de l'histogramme en entrée.
    Typiquement, x est indice et y hist.
    a > 1 determine le pas de l'intervalle : quand a augmente, les intervalles 
    sont moins nombreux mais plus précis.
    En sortie, on a deux liste contenant les abscisses et ordonnées des points
    obtenus par le log binning.'''
    if a<=1:
        raise Exception('a must be > 1 to have correct intervals.')
    #
    # print("x[-1] = %f" % (x[-1]))
    # print("a = %f" % (a))
    # print("np.log(x[-1]) = %f" % (np.log(x[-1])))
    # print("np.log(x[a]) = %f" % (np.log(x[a])))
    n = range(int(np.log(x[-1]) / np.log(a))+2)
    power_x = [a**i for i in n]
    y_bin = stats.binned_statistic(x, y, 'sum', bins=power_x)[0]
    x_bin = [(a**(i+1) + a**i -1)/2 for i in n]

    diff_x = np.array(power_x[1:])-np.array(power_x[:-1])
    y_bin = np.array(y_bin) / diff_x
#    x_plot = [(a**(i+1) + a**i -1)/2 for i in n]

    y_bin_end = []
    x_bin_end = []
    for i in range(len(y_bin)):
        if y_bin[i]>0:
            y_bin_end.append(y_bin[i])
            x_bin_end.append(x_bin[i])

    return x_bin[:-1], y_bin


def plot_d(filename,indice,hist,title, a = 1.5, cut_beggining = 0, cut_end = 'end'):
    '''Trace la distribution des degrés, coupée si besoin.
    cut_beggining et cut_end déterminent le début et la fin de ce qu'on veut prendre.'''
    x,y = log_binning(indice,hist, a=a)
    elemrm=[]
    for i in range(0,len(x)):
        if(x[i]<=0 or y[i]<=0):
            elemrm.append(i)
    if cut_end=='end':
        cut_end=len(x)
    newx=np.delete(x,elemrm)
    newy=np.delete(y,elemrm)
    logx = np.log(np.array(newx))
    logy = np.log(np.array(newy))
    fit = np.polyfit(logx[cut_beggining:cut_end],logy[cut_beggining:cut_end],1)
    # print(fit)
    print(round(fit[0],3))

    plt.loglog(indice,hist, '.', label='DD')#, color='blue')
    plt.loglog(newx,newy,'x', label='log binning', color='black')
    plt.loglog(newx[cut_beggining:cut_end],[xx**fit[0]*np.exp(fit[1]) for xx in newx[cut_beggining:cut_end]], label=r'fit : $\alpha$={}'.format(round(fit[0],3)), color='red')
    plt.title(title)
    plt.xlabel('Augmentation')
    plt.ylabel('Count')
    plt.legend()
    plt.rcParams.update({'font.size': 8})
    plt.grid()
    plt.tight_layout()
    plt.ylim(top=10**9,bottom=0.01)
    plt.xlim(left=0.01,right=10**5)

    plt.savefig(filename)
    plt.close()
    return round(fit[0], 3)
### Fit


def PL_function(x, a, b):
    '''power-law function.'''
    return a*x**b


'''curve_fit(func,x_out,y_out): Fit la courbe (x_out,y_out) par la fonction func.
    popt1_out correspond à la pente.'''





#La fonction suivante est juste utilisee pour l exemple
def DD_power_law(N,alpha):
    #Construit une DD en power law avec pente alpha
    proba_PL = np.array([i**(-alpha) for i in range(1,N)])
    proba_PL = proba_PL/sum(proba_PL)
    while sum(proba_PL)>=1: # Juste parce que multinomial rale si la somme est >1. on est un peu en dessous de 1, mais de pas grand chose donc ca n'influence pas.
        proba_PL = proba_PL/(1.00001*sum(proba_PL))
    tirages = np.random.multinomial(N,proba_PL) # distribution des degres : tirage[i] donne le nombre de noeuds de degré (i+1)
    
    d = [] # liste des degrés
    for x,v in enumerate(tirages):
       for j in range(v):
           d.append(x+1)
          
    ii = -1
    while d[ii]==N-1: # Probleme avec le tirage ... la derniere proba est trop haute -> plusieurs noeuds de degres N-1. On les vire (arbitrairement mis comme des noeuds de degre 1).
        d[ii]=1
        ii-=1
    return d





# d = DD_power_law(10**5,2.5) # On construit une Power-Law de pente -2.5 avec 10**5 points

def export_log_pl(d,filename,title):
    indice, hist = histo(d)
    slope = plot_d(filename,indice, hist,title ,cut_beggining=3)

    x, y = log_binning(indice, hist, a=1.5)
    fit_parameters, cov = curve_fit(PL_function, x, y,maxfev=5000)
    # slope = fit_parameters[0]
    print("yes")
    return slope





