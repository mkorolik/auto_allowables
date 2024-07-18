import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd

from scipy.stats import norm
from scipy.stats import weibull_min
from scipy.stats import gamma

from scipy.stats import nct
from scipy.optimize import root

from scipy import integrate

import statsmodels.api as sm

import math


# types = [norm, weibull_min, gamma]
types = [norm, gamma]
# type_names = ['Normal', 'Weibull', 'Gamma']
type_names = ['Normal', 'Gamma']
colors = ['orange', 'green', 'red']


## FUNCTIONS

def p_value(AD):
    if AD >= .6:
        p = np.exp(1.2937 - 5.709*AD - .0186*(AD**2))
    elif AD >=.34:
        p = np.exp(.9177 - 4.279*AD - 1.38*(AD**2))
    elif AD >.2:
        p = 1 - np.exp(-8.318 + 42.796*AD - 59.938*(AD**2))
    else:
        p = 1 - np.exp(-13.436 + 101.14*AD - 223.73*(AD**2))

    return p


def fit(data, type, ax=None, type_name=None, plot=True, plot_hist=True, hc='lightblue', lc='red'):
    params = type.fit(data)
    
    if ax is None:
        ax = plt.gca()

    if plot_hist:
            values,bins,hist = ax.hist(data, color=hc, edgecolor='black', density=True)
    else:
        values, bins = np.histogram(data, density=True)

    x = np.linspace(bins[0]-15, bins[-1]+10, 100)

    AD = sm.stats.diagnostic.anderson_statistic(data, type)
    p = p_value(AD)

    if plot:
        ax.plot(x, type.pdf(x, *params), color=lc, label=type_name)

    return p


def get_interval_normal(data, p=0.99, conf=1-0.95):
    n = len(data)

    qp = norm.ppf(p, loc=np.mean(data), scale=np.std(data, ddof=1))
    zp = (qp-np.mean(data))/np.std(data, ddof=1)

    nc = zp * np.sqrt(n)

    # t = nct(df=n-1, nc=nc).ppf(conf)
    t = nct.ppf(1-conf, df=n-1, nc=nc)

    L = np.mean(data) - t * np.std(data, ddof=1)/np.sqrt(n)

    return L


def get_interval_gamma(data, p=0.99, conf=1-0.95):
    data_transformed = data**(1/3)

    L_ = get_interval_normal(data_transformed, p=p, conf=conf)

    L = L_**3

    return L


def get_interval_weibull(data, p=0.99, conf=1-0.95):
    
    data_transformed = np.log(data)

    shape, location, scale = weibull_min.fit(data_transformed)

    alpha = np.log(-np.log(1-conf))

    L_ = weibull_min.mean(shape, loc=location, scale=scale) + alpha * weibull_min.std(shape, loc=location, scale=scale)

    L = np.exp(L_)

    return L



## CLASS

class subset:
    def __init__(self, df):
       self.df = df 
       
       self.headers = self.df.columns.values

       self.id = df['Number']
       self.w = df['Width (in)']
       self.t = df['Thickness (in)']
       self.yield_force = df['Force at Yield (lbf)']
       self.yield_tensilestress = df['Tensile stress at Yield (Offset 0.2 %)']
       self.max_force = df['Max Force']
       self.maxforce_tensilestress = df['Tensile stress at Max Force']
       self.maxforce_tensilestrain = df['Tensile strain at Max Force']
       self.break_tensilestrain = df['Tensile strain at Break ']
       self.modulus = df['Modulus ']
       self.elongation = df['Elongation (%) Calipers']
       self.area_reduction = df['Reduction of area']
       self.temp = df['Test Temperature (°F)'] 

    def sort_by_temp(self, temp):
        return subset(self.df[self.temp==temp][self.df['MC'].notna()])
    
    def sort(self, sortby, sortvar):
        return subset(self.df[self.df[sortby]==sortvar][self.df['MC'].notna()])
    
    
    def get_allowable(self, y, weib=False, all_types=None):
        data = self.df[y]

        ps = []

        for i in range(len(types)):
            ps.append(fit(data, types[i], type_name=type_names[i], plot=False, plot_hist=False, lc=colors[i]))

        if not weib:
            ps[1] = 0
        
        best_type_name = type_names[np.argmax(ps)]
        best_type = types[np.argmax(ps)]

        if best_type_name == 'Normal':
            allowable = get_interval_normal(data)
        if best_type_name == 'Weibull':
            raise NotImplementedError('Weibull allowables are not yet supported')
        if best_type_name == 'Gamma':
            allowable = get_interval_gamma(data)

        if all_types is not None:
            print(get_interval_normal(data), get_interval_weibull(data), get_interval_gamma(data))
            return [get_interval_normal(data), get_interval_weibull(data), get_interval_gamma(data)]
        else:
            return [allowable, best_type_name]
    
    def plot_dists(self, y, ax=None, units=''):
        data = self.df[y]

        print(np.mean(data), np.std(data, ddof=1), len(data))

        if ax is None:
            ax = plt.gca()
        
        ps = []

        for i in range(len(types)):
            ps.append(fit(data, types[i], ax=ax, type_name=type_names[i], lc=colors[i]))

        allow, type_ = self.get_allowable(y)
        print(allow)

        ax.axvline(x=allow, color='magenta', linestyle='--', label=f'{allow:.1f}' + units + ' (' + type_ + ')')

        ax.set_xlabel(y)
        ax.set_ylabel('Normalized Density')
        ax.legend()

        print(ps)

        
        
