import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd

from scipy.stats import norm
from scipy.stats import gumbel_r
from scipy.stats import gamma

from scipy.stats import nct
from scipy.optimize import root
from scipy.special import factorial

from scipy import integrate

import statsmodels.api as sm

import math


types = [norm, gamma, gumbel_r]
# types = [norm, gamma]
type_names = ['Normal', 'Gamma', 'Weibull']
# type_names = ['Normal', 'Gamma']
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

    x = np.linspace(bins[0]-5, bins[-1]+5, 100)

    AD = sm.stats.diagnostic.anderson_statistic(data, type)
    p = p_value(AD)

    if plot:
        ax.plot(x, type.pdf(x, *params), color=lc, label=type_name)

    return p


def get_interval_normal(data, p=0.99, conf=0.95):
    n = len(data)

    qp = norm.ppf(p, loc=np.mean(data), scale=np.std(data, ddof=1))
    zp = (qp-np.mean(data))/np.std(data, ddof=1)

    nc = zp * np.sqrt(n)

    t = nct.ppf(conf, df=n-1, nc=nc)

    L = np.mean(data) - t * np.std(data, ddof=1)/np.sqrt(n)

    return L


def get_interval_gamma(data, p=0.99, conf=0.95):
    data_transformed = data**(1/3)

    L_ = get_interval_normal(data_transformed, p=p, conf=conf)

    L = L_**3

    return L


def get_interval_weibull(data, p=0.99, conf=0.95):
    data_transformed = np.log(data)

    loc, scale = gumbel_r.fit(data_transformed)
    mean = (loc - np.euler_gamma * scale)
    std = np.sqrt(np.pi**2 * scale**2 / 6)

    z = (data_transformed - mean)/std
    n = len(data_transformed)

    
    def cz():
        def integrand_cz(t):
            return t**(n-2) * np.exp( (t-1) * np.sum(z) ) / ( 1/n * np.sum(np.exp(z*t)))**n
        return 1 / integrate.quad(integrand_cz, -1, 1)[0]


    def ig(s):
        def integrand_ig(t):
            return t**(n-1) * np.exp(-t)
        return integrate.quad(integrand_ig, 0, s)[0] / factorial(n-1)

    def g(x):
        def integrand_g(t):
            return t**(n-2) * np.exp( (t-1) * np.sum(z) ) * ig(np.exp(np.log(-np.log(p)) -x*t) * np.sum(np.exp(z*t))) / ((1/n * np.sum(np.exp(z*t)))**n)
        return cz() * integrate.quad(integrand_g, -1, 1)[0]
    
    # x_ = np.linspace(-3*np.std(data), 3*np.std(data), 200)
    # gs = []
    # for x in x_:
    #     try:
    #         gs.append(g(x) - conf)
    #     except:
    #         print("Error in Weibull limit calculation. Is your standard deviation too large?")

    # x = - x_[np.argmin(np.abs(gs))]
    #TEMPORARY:
    x = - np.log(-np.log(conf))

    L_ = loc - x * scale

    L = np.exp(L_)
    
    return(L)



## CLASS

class subset:
    def __init__(self, df):
        self.df = df 
        self.headers = self.df.columns.values
    
    def sort(self, sortby, sortvar):
        try:
            return subset(self.df[self.df[sortby]==sortvar])
        except:
            if len(sortvar)==1:
                return subset(self.df[self.df[sortby]==sortvar[0]])
            if len(sortvar)==2:
                return subset(self.df[(self.df[sortby]==sortvar[0]) | (self.df[sortby]==sortvar[1])])
            if len(sortvar)==3:
                return subset(self.df[(self.df[sortby]==sortvar[0]) | (self.df[sortby]==sortvar[1]) | (self.df[sortby]==sortvar[2])])
            else:
                print(f'selected {len(sortvar)} options but can only handle up to 3 right now')
    
    def get_ps(self, y):
        data = self.df[y].values.astype(float)

        ps = []
        for type in types:
            ps.append(fit(data, type, plot=False, plot_hist=False))
        
        return ps

    def get_allowable(self, y, weib=False, all_types=False):
        data = self.df[y].values.astype(float)

        ps = []

        for type in types:
            ps.append(fit(data, type, plot=False, plot_hist=False))

        if not weib:
            ps[1] = 0
        
        best_type_name = type_names[np.argmax(ps)]
        best_type = types[np.argmax(ps)]

        if best_type_name == 'Normal':
            allowable = get_interval_normal(data)
        if best_type_name == 'Weibull':
            allowable = get_interval_weibull(data)
        if best_type_name == 'Gamma':
            allowable = get_interval_gamma(data)

        if all_types is True:
            print(y)
            pn, pg, pw = self.get_ps(y)
            print(f'Average: {np.mean(data):.3f}; StDev: {np.std(data, ddof=1):.3f}')
            print(f'Normal method: {get_interval_normal(data):.3f}, p = {pn}')
            print(f'Gamma Method: {get_interval_gamma(data):.3f}, p = {pg}')
            print(f'Weibull (ish) Method: {get_interval_weibull(data):.3f}, p = {pw}')
            return [get_interval_normal(data), get_interval_gamma(data), get_interval_weibull(data)]
        else:
            return [allowable, best_type_name]
    
    def plot_dists(self, y, ax=None, units=''):
        data = self.df[y].values.astype(float)

        if ax is None:
            ax = plt.gca()
        

        for i in range(len(types)):
            fit(data, types[i], ax=ax, type_name=type_names[i], lc=colors[i])

        allow, type_ = self.get_allowable(y)

        ax.axvline(x=allow, color='magenta', linestyle='--', label=f'{allow:.1f}' + units + ' (' + type_ + ')')

        ax.set_xlabel(y)
        ax.set_ylabel('Normalized Density')
        ax.legend()


    def plot_temperature(self, y, temp, room_temp, ax=None, deg=1):
        data = np.array(self.df[y])
        data_rt = data/float(room_temp)

        if ax is None:
            ax = plt.gca()        

        temp_data = np.array(self.df[temp])

        temperatures = list(set(temp_data))
        data_binned = []
        for t in temperatures:
            data_binned.append(np.mean(data_rt[np.argwhere(temp_data==t)]))

        params, residuals, rank, sv, rcond = np.polyfit(temperatures, data_binned, deg, full=True)
        r2 = 1 - residuals/np.sum(np.abs(data_rt - np.mean(data_rt)))
        print(r2)

        x = np.linspace(min(temperatures)-1, max(temperatures)+1, 100)

        ax.scatter(temp_data, data_rt, color='lightblue', alpha=0.7)
        ax.scatter(temperatures, data_binned)
        ax.plot(x, np.polyval(params, x))

        ax.set_xlabel(temp)
        ax.set_ylabel(f'{y} % of RT Mean')
        
        return params, r2
        
