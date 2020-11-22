import numpy as np
from matplotlib import pyplot as plt
import time
from scipy.optimize import curve_fit
from scipy import stats


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


def plot_d(indice,hist, a = 1.5, cut_beggining = 0, cut_end = 'end'):
    '''Trace la distribution des degrés, coupée si besoin.
    cut_beggining et cut_end déterminent le début et la fin de ce qu'on veut prendre.'''
    x,y = log_binning(indice,hist, a=a)
    if cut_end=='end':
        cut_end=len(x)
    logx = np.log(np.array(x))
    logy = np.log(np.array(y))
    fit = np.polyfit(logx[cut_beggining:cut_end],logy[cut_beggining:cut_end],1)
    print(fit)

    plt.loglog(indice,hist, '.', label='DD')#, color='blue')
    plt.loglog(x,y,'x', label='log binning', color='black')
    plt.loglog(x[cut_beggining:cut_end],[xx**fit[0]*np.exp(fit[1]) for xx in x[cut_beggining:cut_end]], label=r'fit : $\alpha$={}'.format(round(fit[0],3)), color='red')
    
    plt.xlabel('degree')
    plt.ylabel('#Nodes with this degree')
    plt.legend()
    plt.grid()
    plt.rcParams.update({'font.size': 16})



### Fit
    

def PL_function(x, a, b):
    '''power-law function.'''
    return a*x**b


'''curve_fit(func,x_out,y_out): Fit la courbe (x_out,y_out) par la fonction func.
    popt1_out correspond à la pente.'''


#'''Exemple :
d = [5,5,2,2,1,1,1,1,1]
d = [int(1/Pi) for Pi in np.random.power(2.5, 10**5)] # On crée une power-law avec 10**5 points et de pente -2.5
indice, hist = histo(d)
plot_d(indice, hist)

x, y = log_binning(indice, hist,a=1.5)
fit_parameters, cov = curve_fit(PL_function, x, y)
slope = fit_parameters[0]
print(slope)
#'''



