import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
import random
def plotter(res, u="years", count="probability",plot="power-law",limit=None, **args):
    bins = [i for i in range(int(min(res)),int(max(res)))]    
    hist,bins = np.histogram(res, bins=bins)
    save = args.pop("save", None)
    path = args.pop("path", None)
    if save==True and path==None:
        raise ValueError("Filename not provided. path='file_path_to_save'")
    
    bins_plot=bins[:-1]
    # bins_plot = (bins[1:]+bins[:-1])/2
    if count=="probability": hist = hist / len(res)
    elif count=="ccdf": hist = 1 - np.cumsum(hist)/len(res)
    else: hist = hist

    if len(bins)==0 or len(hist)==0: return None
    left, right, bottom, top = min(bins), max(bins), min(hist), max(hist) #max(hist)==0
    if limit==None:    
        if count=="probability" or count=="ccdf":
            yaxislabel = "Probability"
            if plot == "power-law" or plot=="poisson": bottom, top = hist[-1],2
        else:
            yaxislabel = "Frequency"
    else:
        left, right, bottom, top = limit
        if count=="probability" or count=="ccdf":
            yaxislabel = "Probability"
        else:
            yaxislabel = "Frequency"
            
    if plot=="power-law": xscale, yscale = 'log', 'log'
    elif plot=="poisson": xscale, yscale = 'linear', 'log'
    elif plot=="log": xscale, yscale = 'log', 'linear'
    elif plot=="linear": xscale, yscale = 'linear', 'log'
    else: raise ValueError("plot parameter received invalid string. plot must be one of {'power-law','poisson','log','linear'}")
    
    plt.legend()
    plt.title(args.pop("title", "Coauthorship interval"))
    plt.xlabel(f'{args.pop("xlabel", "Coauthorship interval")} [{u}]')
    plt.ylabel(yaxislabel)
    
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.xlim(left, right)
    plt.ylim(bottom, top)
    
    if count=="number":
        plt.xlim(1,max(bins)*1.5)
        plt.ylim(0.5,max(hist)*2)
        plt.ylabel('Frequency')
    
    if args.pop("line", False):
        plt.plot(bins_plot[:-1], hist,**args)
    else:
        plt.scatter(bins_plot, hist,**args)

    plt.tight_layout()

    if save==True:
        plt.savefig(path)
        plt.close()
    
    return hist, bins_plot
    
def calculate_coauth_intervals(id,authors_valid,year_df):
    works = authors_valid['eid'][authors_valid['authid']==id]
    if works.shape[0]<3: return None

    selected_papers = year_df[year_df.index.isin(works.values)]
    selected_papers = selected_papers.assign(seq=list(range(0,len(selected_papers))))
    coauthors = authors_valid[authors_valid['eid'].isin(works)].query(f"authid!={id}")
    
    df_seqyear = pd.merge(coauthors,selected_papers, how='left', on='eid').sort_values(by='seq')
    df_seqyear_multi = df_seqyear.groupby(by='authid', group_keys=True).filter(lambda x: len(x) > 1)
    if len(df_seqyear_multi) < 1: return None
    df_seqyear_delta = df_seqyear_multi.groupby(by='authid', group_keys=True)[['year','seq']] \
    .apply(lambda x:  x - x.shift(1)) \
    .dropna().astype(int).reset_index()
    
    df_seqyear_delta = pd.merge(df_seqyear_delta, df_seqyear["eid"], how="left", left_on="level_1", right_index=True).drop(columns=["level_1"])
    df_seqyear_delta["source_authid"] = id
    df_seqyear_delta["previous_work"] = df_seqyear_delta.groupby("authid").shift(1)["eid"]

    df_seqyear_delta = df_seqyear_delta.dropna()
    return df_seqyear_delta