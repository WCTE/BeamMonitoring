#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from time import sleep

# Parse arguments
parser = ArgumentParser(
    description=__doc__,
    formatter_class=ArgumentDefaultsHelpFormatter,
)

# Shared parser for subcommands
parser.add_argument('-f', '--filename',type=str,help='input logfile name',default='wcte-hv.log')
parser.add_argument('-d', '--dateappend',type=bool,help='append date to output image filenames',default=False)
parser.add_argument('-m','--maxrecord',type=int,help='maximum number of entries to plot',default=200)
args = parser.parse_args()
hvdf = pd.read_csv(args.filename,sep=' ')


def plot_together( df, keys, xlabel, ylabel, maxlen=200 ):
    fig=plt.figure(figsize=(6,3),dpi=200)
    curlen = len(df['Date'])
    if curlen > maxlen:
        curlen=maxlen
    dates = df['Date'][-curlen:]
    times = df['Time'][-curlen:]
    dtimes = []
    for date, time in zip(dates,times):
        dtimes.append( datetime.strptime( date+' '+time, '%Y-%m-%d %H:%M:%S.%f') )
    for key in keys:
        plt.plot( dtimes, df[key][-curlen:], label=key )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=90)
    return fig
                      

actvoltages = plot_together( hvdf, 
                            ['ACT0-L-VMon','ACT0-R-VMon','ACT1-L-VMon','ACT1-R-VMon','ACT2-L-VMon','ACT2-R-VMon','ACT3-L-VMon','ACT3-R-VMon','ACT4-L-VMon','ACT4-R-VMon','ACT5-L-VMon','ACT5-R-VMon'],
                            'Time','Voltage (V)',args.maxrecord)

actcurrents = plot_together( hvdf, 
                            ['ACT0-L-IMon','ACT0-R-IMon','ACT1-L-IMon','ACT1-R-IMon','ACT2-L-IMon','ACT2-R-IMon','ACT3-L-IMon','ACT3-R-IMon','ACT4-L-IMon','ACT4-R-IMon','ACT5-L-IMon','ACT5-R-IMon'],
                            'Time','Current (uA)',args.maxrecord)

t0voltages = plot_together( hvdf, 
                            ['T0-0L-VMon','T0-0R-VMon','T0-1L-VMon','T0-1R-VMon',
                             'T1-0L-VMon','T1-0R-VMon','T1-1L-VMon','T1-1R-VMon',
                             'T2-VMon','T3-VMon'],
                            'Time','Voltage (V)',args.maxrecord)

t0currents = plot_together( hvdf, 
                            ['T0-0L-IMon','T0-0R-IMon','T0-1L-IMon','T0-1R-IMon',
                             'T1-0L-IMon','T1-0R-IMon','T1-1L-IMon','T1-1R-IMon',
                             'T2-IMon','T3-IMon'],
                           'Time','Current (uA)',args.maxrecord)

hodovoltages = plot_together( hvdf, 
                            ['HD-0-VMon','HD-1-VMon','HD-2-VMon','HD-3-VMon','HD-4-VMon',
                             'HD-5-VMon','HD-6-VMon','HD-7-VMon','HD-8-VMon','HD-9-VMon',
                            'HD-10-VMon','HD-11-VMon','HD-12-VMon','HD-13-VMon','HD-14-VMon'],
                            'Time','Voltage (V)',args.maxrecord)

hodocurrents = plot_together( hvdf, 
                            ['HD-0-IMon','HD-1-IMon','HD-2-IMon','HD-3-IMon','HD-4-IMon',
                             'HD-5-IMon','HD-6-IMon','HD-7-IMon','HD-8-IMon','HD-9-IMon',
                            'HD-10-IMon','HD-11-IMon','HD-12-IMon','HD-13-IMon','HD-14-IMon'],
                             'Time','Current (uA)',args.maxrecord)

othervoltages = plot_together( hvdf, 
                            ['HC-0-VMon', 'HC-1-VMon', 'HC2-VMon', 'PbGlass-VMon',
                            'MuonTag-R-VMon', 'MuonTag-L-VMon','WMS-source-VMon',
                            'WMS-reci-VMon'],
                            'Time','Voltage (V)',args.maxrecord)
othercurrents = plot_together( hvdf, 
                            ['HC-0-IMon', 'HC-1-IMon', 'HC2-IMon', 'PbGlass-IMon',
                            'MuonTag-R-IMon', 'MuonTag-L-IMon','WMS-source-IMon',
                            'WMS-reci-IMon'],
                             'Time','Current (uA)',args.maxrecord)

datetag=''
if args.dateappend:
	datetag = '_'+str(datetime.now()).replace(' ','_')
actvoltages.savefig( 'actvoltages'+datetag+'.png', bbox_inches='tight')
actcurrents.savefig( 'actcurrents'+datetag+'.png', bbox_inches='tight')
t0voltages.savefig( 't0voltages'+datetag+'.png', bbox_inches='tight')
t0currents.savefig( 't0currents'+datetag+'.png', bbox_inches='tight')
hodovoltages.savefig( 'hodovoltages'+datetag+'.png', bbox_inches='tight')
hodocurrents.savefig( 'hodocurrents'+datetag+'.png', bbox_inches='tight')
othervoltages.savefig( 'othervoltages'+datetag+'.png', bbox_inches='tight')
othercurrents.savefig( 'othercurrents'+datetag+'.png', bbox_inches='tight')

