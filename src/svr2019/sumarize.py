#!/usr/bin/python3
import os

from sklearn.metrics import calinski_harabaz_score, silhouette_score
import numpy as np

from svr2019.metrics import davies_bouldin_score, dunn_index
from svr2019.datasets import *

import matplotlib.pyplot as plt
import seaborn as sns

def internal_summary(points, labels):
    """
    Generate a summary of internal validation measures.
    Returns a dictionary containing elements:
        - 'calinski-harabaz'
        - 'davies-bouldin'
        - 'dunn-index'
        - 'silhouette-score'
    
    :param points: a numpy array of data points
    :param labels: a numpy array of labels for each point
    """

    labels = np.array(labels)

    calinski_harabaz = calinski_harabaz_score(points, labels)
    davies_bouldin = davies_bouldin_score(points, labels)
    di = dunn_index(points, labels)
    silhouette = silhouette_score(points, labels)

    return {
            'calinski-harabaz':calinski_harabaz,
            'davies-bouldin':davies_bouldin,
            'dunn-index':di,
            'silhouette-score':silhouette,
           }


def print_summaries(path_list):
    head = True
    for path,dataset,labels in path_list:
        #labels = DuoBenchmark('data/datasets/'+dataset+'.csv').tags 
        with open(path,'rb') as fh:
            embedding = np.load(fh).astype(np.float32)
        try:
            summary_dict = internal_summary(embedding, labels)
            summary_list = [path]+[str(summary_dict[x]) for x in sorted(summary_dict.keys())]
            if head:
                print(','.join(['path']+sorted(summary_dict.keys())))
                head = False
            print(','.join(summary_list))
        except ValueError:
            pass

def get_table_dict(results_file,lwr_bnd_dims=2,upr_bnd_dims=90):
    """
    :param results_file: path to results file. Should be a csv in the format
        dataset,method,dimensions,log,vrc,db,di,ss
        however, do not include both log = True/False for the same entry
    : param lwr_bnd_dims: exclude entries with dimensionality below this
    : param upr_bnd_dims: exclude entries with dimensionality above this
    
    Note that due to upr/lwr bounds, 'full' datasets will likely be excluded.
    To work around this format the dimension like '22k' 
    """
    table_dict = dict()
    # organize results into a dictionary
    # Keys are dataset names
    # entries are also dictionaries of the form
    # {'ch':[],'db':[],'di':[],'ss':[]} 
    # Where each list contains entries of [value,method,dimensions]
    with open(results_file,'r') as fh: 
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

            # The exception we expect to see here is in the case
            # of a dimension formatted like '22k' which will fail
            # integer conversion.  This is used as a convenience to
            # allow for plotting of the heatmaps without too many
            # digits.
            try:
                if int(dims) < lwr_bnd_dims or int(dims) >= upr_bnd_dims:
                    continue
            except:
                pass
            ch = [float(v[4]),dims,meth]
            db = [float(v[5]),dims,meth]
            di = [float(v[6]),dims,meth]
            ss = [float(v[7]),dims,meth]

            if name not in table_dict.keys():
                table_dict[name] = {'ch' : list(),
                                    'db' : list(),
                                    'di' : list(),
                                    'ss' : list()}

            table_dict[name]['ch'].append(ch)
            table_dict[name]['db'].append(db)
            table_dict[name]['di'].append(di)
            table_dict[name]['ss'].append(ss)

    return table_dict

def get_rankings(table_dict,score,methods):
    res_dict = dict()
    for key in table_dict.keys():
        res_dict[key] = list()
        seen = list()
        order = -1
        if score == 'db':
            order = 1
        c = 1

        for i,entry in enumerate(sorted(table_dict[key][score],key = lambda x: order*x[0])):
            if entry[2] not in seen:
                seen.append(entry[2])
                entry.append(c)
                c += 1
                res_dict[key].append(entry)

        for m in methods:
            if m not in seen:
                res_dict[key].append([np.nan,np.nan,m,len(m)])

    return res_dict

def plot_optimal_heatmap(metric, results_file, methods):

    table_dict = get_table_dict(results_file)

    # produce a dictionary of rankings from the table
    # but only for the metric of intrest
    ss_res = get_rankings(table_dict,metric,methods)
    for i in sorted(ss_res.keys()):
        ss_res[i] = sorted(ss_res[i],key = lambda x: x[2])
    data = list()
    annot = list()
    for i in sorted(ss_res.keys()):
        data.append([x[-1] for x in ss_res[i]])
        annot.append([x[1] for x in ss_res[i]])
    annot = np.array(annot)
    ylabs = sorted(ss_res.keys())
    xlabs = sorted([x[2] for x in ss_res['chen']])
    #sns.heatmap(data,xticklabels=xlabs,yticklabels=ylabs,cmap="YlGnBu")
    sns.heatmap(data,xticklabels=xlabs,yticklabels=ylabs,annot=annot,fmt="s")
    plt.tight_layout()
    plt.savefig(os.path.join('results/plots',metric))

if __name__ == '__main__':
    pass
