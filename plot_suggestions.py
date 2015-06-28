import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as math
from IPython.display import display
from IPython.core.pylabtools import getfigs
import sklearn.metrics
import seaborn as sns
import pickle

def plot_probability_funding_freq(subset_predictor_df,outcomes_df,\
    feature_name,bins = range(12),step=1,vline_x=-1,if_log=False):
    import matplotlib.gridspec as gridspec
    sns.set_style("whitegrid")
    # set up axes
    
    plt.rcParams.update({'font.size': 14})
    label_font_size = 14
    fig = plt.figure(figsize=(6*1.618,6))
    #fig = plt.figure(figsize=(5.5875, 6.2))


    gs = gridspec.GridSpec(2,1,height_ratios=[.3,.7])
    gs.update(wspace=0.1, hspace=0.1)
    
    hist_ax = plt.subplot(gs[1,0])  
    success_ax  = plt.subplot(gs[0,0]) 
    
    # get predictor, success and failure points
    this_predictor = subset_predictor_df[feature_name].values
    
    success_is = np.where(outcomes_df['Outcome'] == 1)[0]
    fail_is = np.where(outcomes_df['Outcome'] == 0)[0]
    chance = len(success_is)/float(len(success_is) + len(fail_is))

    # if if_log:
    #     bins = numpy.log2(data)
            
    hist_ax.hist(this_predictor[fail_is],bins=bins,align='left',histtype='step',\
        color='black', fill=False,linewidth=4,normed=True)

    hist_ax.hist(this_predictor[success_is],bins=bins,align='left',histtype='step',\
        color='#32CD32', fill=False,linewidth=4,normed=True)
    
    hist_ax.set_xlabel(feature_name,fontsize=label_font_size)
    hist_ax.set_ylabel('Relative frequency',fontsize=label_font_size)
    hist_ax.set_xlim([-.75,max(bins)-.25])
    success_ax.set_xlim([-.75,max(bins)-.25])

    # annotate success and failure
    hist_y_lim = hist_ax.get_ylim()
    hist_x_lim = hist_ax.get_xlim()
    
    label1_y = hist_y_lim[1]*.925
    label1_x = hist_x_lim[1]*.80

    label2_y = hist_y_lim[1]*.85
    label2_x = hist_x_lim[1]*.80

    hist_ax.annotate('succeeded', xy=(label1_x,label1_y),\
             xytext=(label1_x,label1_y),color='#32CD32')
    hist_ax.annotate('failed', xy=(label2_x,label2_y),\
             xytext=(label2_x,label2_y),color='black')

    
    if vline_x > -1:
        hist_ax.axvline(vline_x,color='purple',linewidth=1.5)
        hist_ax.annotate('your campaign', xy=(vline_x,.5),\
             xytext=(vline_x+.2,.5),color='purple')

    # calc, plot success frequency
    success_freq = np.empty_like(bins[:-1],dtype=float)

    for i,bin in enumerate(bins[:-1]):
        
        this_bin_is = np.intersect1d(np.where(subset_predictor_df[feature_name]>=bin)[0],
                                     np.where(subset_predictor_df[feature_name]<bin+step)[0])

        n_this_bin = len(this_bin_is)
        n_success = sum(outcomes_df.ix[this_bin_is,'Outcome'].values)
        if n_this_bin:
            success_freq[i] = float(n_success)/n_this_bin
        else:
            success_freq[i] = np.nan
    
    #show chance    
    success_ax.axhline(chance,color='grey',linewidth=2)

    success_ax.plot(np.asarray(bins[:-1]),success_freq,'.',color='blue',markersize=15)
    success_ax.set_ylim([0,1])
    success_ax.set_ylabel('Success probability',fontsize=label_font_size)

    #annotate chance
    success_ax.annotate('chance', xy=(1,chance),\
             xytext=(.25,chance+.025),color='black')

    success_ax.set_xticklabels([])
    
    #saveas_path = '/Users/jamie/insight_data/figures/'
    #plt.savefig(saveas_path + feature_name +' success rate and hist.png',bbox_inches='tight',dpi=400) 

def plot_feature_importances(feature_importances,X_cols,n_top):
    #plt.rcParams.update({'font.size': 10})

    fig = plt.figure(figsize=(5*1.618,5))
    feature_importance_is = np.argsort(feature_importances)
    feature_importance_is_decending = feature_importance_is[-1::-1]
    plt.title("Feature importances")
    plt.bar(range(n_top), feature_importances[feature_importance_is_decending[0:n_top]],
           color="b", align="center")
    plt.xticks(range(n_top), X_cols[feature_importance_is_decending[0:n_top]],rotation='vertical')
    plt.xlim([-1, n_top])
    plt.xlabel('Feature')
    plt.ylabel('Feature importance (Gini importance)')
    plt.show()
    saveas_path = '/Users/jamie/insight_data/figures/'
    plt.savefig(saveas_path + 'feature_importances.png',bbox_inches='tight',dpi=400) 


def plot_coefficients(feature_importances,X_cols,n_top):
    #plt.rcParams.update({'font.size': 10})

    fig = plt.figure(figsize=(5*1.618,5))
    feature_importance_is = np.argsort(feature_importances)
    feature_importance_is_decending = feature_importance_is[-1::-1]
    plt.title("Feature importances")
    plt.bar(range(n_top), feature_importances[feature_importance_is_decending[0:n_top]],
           color="b", align="center")
    plt.xticks(range(n_top), X_cols[feature_importance_is_decending[0:n_top]],rotation='vertical')
    plt.xlim([-1, n_top])
    plt.xlabel('Logistic regression coefficients')
    plt.ylabel('Coefficient')
    plt.show()
    saveas_path = '/Users/jamie/insight_data/figures/'
    plt.savefig(saveas_path + 'coefficients.png',bbox_inches='tight',dpi=400) 
