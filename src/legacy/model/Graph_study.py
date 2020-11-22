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
#    return x_bin[:-1], y_bin
    return x_bin_end, y_bin_end


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
#    print('qwepfjahiovnskmc')
    plt.loglog(indice,hist, '.', label='DD')#, color='blue')
    plt.loglog(x,y,'x', label='log binning', color='black')
    plt.loglog(x[cut_beggining:cut_end],[xx**fit[0]*np.exp(fit[1]) for xx in x[cut_beggining:cut_end]], label=r'fit : $\alpha$={}'.format(round(fit[0],3)), color='red')
    
    plt.xlabel('degree')
    plt.ylabel('#Nodes with this degree')
    plt.legend()
    plt.grid()
    plt.rcParams.update({'font.size': 16})
    plt.title("Degree distribution 2018")
    plt.savefig("Degree distribution 2018")
    
    return fit[0]



### Fit
    

def PL_function(x, a, b):
    '''power-law function.'''
    return a*x**b


'''curve_fit(func,x_out,y_out): Fit la courbe (x_out,y_out) par la fonction func.
    popt1_out correspond à la pente.'''




#Exemple :

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



'''Example 

#d = [5,5,2,2,1,1,1,1,1]
d = DD_power_law(10**5,2.5) # On construit une Power-Law de pente -2.5 avec 10**5 points
indice, hist = histo(d)
slope = plot_d(indice, hist, cut_beggining= 3)
print('slope', slope)

#x, y = log_binning(indice, hist,a=1.5)
#fit_parameters, cov = curve_fit(PL_function, x, y)
#print('parameters', fit_parameters)
#slope = fit_parameters[0]
#print(slope)

'''


def estimate_alpha_with_MLE(d, xmin=1):
    def create_histogram(d):
        # Check: ok
        '''Création de l'histogramme (degree distribution) à partir d'une liste de degrés.
        d : liste de degrés.
        hist : histogramme (ie nombre de fois où la valeur d'absisse apparait dans d).'''
    
        hist = {key:0 for key in set(d)}
        for degree in d:
            hist[degree] += 1 
        Z = len(d)
        for key in hist.keys():
            hist[key] = hist[key] / Z
        return hist
    
    def create_CDF(d):
        # Check: ok
        '''Création de la CDF à partir d'une liste de degrés.
        d : liste de degrés.
        CDF : CDF de d.'''
        histo = create_histogram(d)
    
        CDF = {}
        previous_value = 0
        reversed_keys = list(histo.keys())
        reversed_keys.sort(reverse=True)
        for key in reversed_keys:
            CDF[key] = histo[key] + previous_value
            previous_value = CDF[key]
        return CDF, histo

    N = len(d)
    CDF, histo = create_CDF(d)
    estimated_alpha = 1 + (CDF[xmin]*N) / (sum([histo[degree]*N * np.log(degree / (xmin-0.5)) for degree in histo.keys() if degree>=xmin]))
    return (- estimated_alpha)




### Taille de la macrostructure


def taille_macro(N,in_tot,out_tot):
    taille_IN = 0
    taille_OUT = 0
    taille_DISC = 0
    
    for i in range(N):
        if in_tot[i]==0:
            taille_IN += 1
        if out_tot[i]==0:
            taille_OUT += 1
        if in_tot[i]==0 and out_tot[i]==0:
            taille_DISC += 1
    
    IN = 100*(taille_IN-taille_DISC)/float(N)
    OUT = 100*(taille_OUT-taille_DISC)/float(N)
    DISC = 100*taille_DISC/float(N)
    
    print('IN',IN)
    print('OUT',OUT)
    print('DISC',DISC)

    return (IN,OUT,DISC)