import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
import random

def plotter(res, u="years", count="probability",plot="power-law",limit=None, **args):
    bins = [i for i in range(int(min(res)),int(max(res)))]
    bins_plot = np.add(bins,0.5)
    
    hist,bins = np.histogram(res, bins=bins)
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
        
    if args.get("line", False):
        plt.plot(bins[:-1], hist,color=args.get("c", "blue"),label=args.get("l", None))
    else:
        plt.scatter(bins[:-1], hist,color=args.get("c", "blue"),s=20,label=args.get("l", None))

    plt.legend()
    plt.title(args.get("title", "Coauthorship interval"))
    plt.xlabel(f'{args.get("xlabel", "Coauthorship interval")} [{u}]')
    plt.ylabel(yaxislabel)
    
    plt.xscale(xscale)
    plt.yscale(yscale)
    plt.xlim(left, right)
    plt.ylim(bottom, top)
    
    if count=="number":
        plt.xlim(1,max(bins)*1.5)
        plt.ylim(0.5,max(hist)*2)
        plt.ylabel('Frequency')
    
    plt.tight_layout()

    if args.get("save", None)==True:
        if args.get("path", None)==None: raise ValueError("Filename not provided")
        plt.savefig(args.get("path", "./plot.png"))
        plt.close()
    
    return hist, bins_plot