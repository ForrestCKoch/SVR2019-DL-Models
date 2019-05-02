#!/usr/bin/python3
import os
import sys
import pickle

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import spearmanr

from sklearn.metrics import pairwise_distances

from svr2019.datasets import *
from svr2019.summarize import *

def reject_outliers(data, m=5):
    mu = np.mean(data)
    sd = np.std(data)
    return data[abs(data - mu) < m * sd]

def trim_data(data, m=0.5):
    intvl = np.percentile(data,[m,100-m])
    return data[(data >= intvl[0]) & (data <= intvl[1])]

table_dict = dict()

with open('results/csvs/internal_metrics_reduced.csv','r') as fh:
    methods = list()
    header = fh.readline().rstrip('\n')
    for line in fh:
        # extract our values
        v = line.rstrip('\n').split(',')
        name = v[0]
        meth = v[1]
        dims = v[2]
        if meth not in methods:
            methods.append(meth)
        try:
            if int(dims) < 2 or int(dims) >= 90:
                continue
        except:
            pass

        ss = [float(v[7]),dims,meth]
      
        if name not in table_dict.keys():
            table_dict[name] = {'ss' : list()}

        table_dict[name]['ss'].append(ss)

ss_res = get_rankings(table_dict,'ss',methods)

n_meth = len(methods) - 1
n_data = len(ss_res.keys())
count = 1

plt.rcParams["figure.figsize"] = (8,11)
first_row=True
for dataset in ss_res.keys():
    print(dataset)
    #ds = DuoBenchmark('data/datasets/'+dataset+'.csv',split_head=False)
    #raw_data = ds.data
    #pw_raw = pairwise_distances(raw_data)
    first_col=True
    colour = 1
    for entry in sorted(ss_res[dataset],key = lambda x:x[2]):
        method = entry[2]
        dims = entry[1]
        if method == 'full':
            continue
        if method == 'sdae':
            emb_file = 'data/embeddings/'+dataset+'/'+method+'/'+dims+'-log-True.pickle'
        else:
            emb_file = 'data/embeddings/'+dataset+'/'+method+'/'+dims+'-log-False.pickle'
        with open(emb_file,'rb') as fh:
            emb_data = pickle.load(fh)
        pw_emb = pairwise_distances(emb_data).flatten()
        
        plt.subplot(n_data,n_meth,count)
        count += 1
        r = np.random.randn(100,100).flatten()
#        hist = plt.hist(trim_data(r),bins='scott')
#        hist = plt.hist(reject_outliers(pw_emb),bins='scott')
        hist = plt.hist(trim_data(pw_emb),bins='scott')
        # remove our ticks and labels
        plt.xticks(ticks=[],labels=[])
        # add the dataset to the first column
        p = hist[0]
        if first_col:
            plt.yticks(ticks=[np.max(p)/2],labels=[dataset])
            first_col=False
        else:
            plt.yticks(ticks=[],labels=[])
        # add titles only to the first row
        if first_row:
            plt.title(method)

#        plt.text(7*np.max(hist[1])/8,7*np.max(p)/8,'test')
        #scor = np.mean([spearmanr(pw_emb[i],pw_raw[i]).correlation for i in range(0,len(pw_emb))])
        #print('\t'+method+' : '+str(scor))
        print('\t'+method)
    first_row = False
        
#plt.savefig('test.pdf') 
plt.show(block=True)
