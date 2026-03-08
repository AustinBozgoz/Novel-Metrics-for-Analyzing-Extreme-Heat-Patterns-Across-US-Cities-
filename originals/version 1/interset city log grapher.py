#### controls ####
ind_dataset='temp' #dataset for x axis: wb, temp, or hi
ind_variable='AAO90' #variable as it's written in dataset (mind ACDO and AAO)

dep_dataset='hi' #dataset for y axis
dep_variable='AAO90' #variable as it's written

onetoone=True #plot y=x line? (true/false)
title=False #custom title, record false for default
approach='regional' #commands are none, regional, climate1 (koppen by region),
#or climate2 (koppen by coordinates); the approach for the graph to identify and label points

#### actual code ####

#import packages
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import plotly.io as pio
import plotly.express as px
import numpy as np
import pandas as pd
import mplcursors

#assign color codes for legends
region_legend=[Line2D([0],[0],marker='o',markerfacecolor='#000000',markeredgecolor='k',label='Miami'),
               Line2D([0],[0],marker='o',markerfacecolor='#00FF00',markeredgecolor='k',label='SW'),
               Line2D([0],[0],marker='o',markerfacecolor='#FFFF00',markeredgecolor='k',label='SE'),
               Line2D([0],[0],marker='o',markerfacecolor='#FFA500',markeredgecolor='k',label='NE'),
               Line2D([0],[0],marker='o',markerfacecolor='#ff0000',markeredgecolor='k',label='W'),
               Line2D([0],[0],marker='o',markerfacecolor='#800080',markeredgecolor='k',label='WC'),
               Line2D([0],[0],marker='o',markerfacecolor='#0000FF',markeredgecolor='k',label='MW'),
               Line2D([0],[0],marker='o',markerfacecolor='#FFC0CB',markeredgecolor='k',label='H')]

climate1_legend=[Line2D([0],[0],marker='o',markerfacecolor='#000000',markeredgecolor='k',label='A'),
                 Line2D([0],[0],marker='o',markerfacecolor='#ff0000',markeredgecolor='k',label='B'),
                 Line2D([0],[0],marker='o',markerfacecolor='#FFFF00',markeredgecolor='k',label='C'),
                 Line2D([0],[0],marker='o',markerfacecolor='#0000FF',markeredgecolor='k',label='D'),
                 Line2D([0],[0],marker='o',markerfacecolor='#964B00',markeredgecolor='k',label='A/B'),
                 Line2D([0],[0],marker='o',markerfacecolor='#00FF00',markeredgecolor='k',label='C/D'),
                 Line2D([0],[0],marker='o',markerfacecolor='#800080',markeredgecolor='k',label='B/D'),
                 Line2D([0],[0],marker='o',markerfacecolor='#FFA500',markeredgecolor='k',label='B/C'),
                 Line2D([0],[0],marker='o',markerfacecolor='#FFFFFF',markeredgecolor='k',label='B/C/D')]

climate2_legend=[Line2D([0],[0],marker='o',markerfacecolor='#000000',markeredgecolor='k',label='A'),
                 Line2D([0],[0],marker='o',markerfacecolor='#ff0000',markeredgecolor='k',label='B'),
                 Line2D([0],[0],marker='o',markerfacecolor='#FFFF00',markeredgecolor='k',label='C'),
                 Line2D([0],[0],marker='o',markerfacecolor='#0000FF',markeredgecolor='k',label='D')]

approach_text={'regional':'regional','climate1':'climate by surroundings','climate2':'climate by coordinates'}#approach written in title

def point_maker(city,labels,approach):#given the city, list of labels (registry), and approach type, return a color code
    city_info=labels[labels['City']==city] #in registry, find the entry for the correct city
    category=city_info[approach]#pull the appropriate category
    print(city)
    if approach=='Region':
        region_dictionary={'Miami':'#000000','SW':'#00FF00','SE':'#FFFF00','NE':'#FFA500','W':'#ff0000','WC':'#800080','MW':'#0000FF','H':'#FFC0CB'}
        return region_dictionary[category.iloc[0]] 
    
    if approach=='Koppen (by city)':
        koppen_dictionary={'A':'#000000','B':'#ff0000','C':'#FFFF00','D':'#0000FF','A/B':'#964B00','C/D':'#00FF00','B/D':'#800080','B/C':'#FFA500','B/C/D':'#FFFFFF'}
        return koppen_dictionary[category.iloc[0]]
    if approach=='Koppen (by station coordinates)':
        koppen_dictionary={'A':'#000000','B':'#ff0000','C':'#FFFF00','D':'#0000FF'}
        return koppen_dictionary[category.iloc[0]]

#import data
ind_log=pd.read_csv('geospatial %s data.csv'%ind_dataset)
dep_log=pd.read_csv('geospatial %s data.csv'%dep_dataset)

#grab subsets
ind_subset=ind_log[ind_variable]
dep_subset=dep_log[dep_variable]

#ensure the cities for all the databases matchup
for i in range(len(ind_log['City'])):
    if (ind_log['City'][i]==dep_log['City'][i])==False:
        print('error on city matchup: %s for ind and %s for dep'%(ind_log['city'][i],T_logs['city'][i]))
    

Names=ind_log['City']

#various things for graphing
labels=pd.read_csv('registry.csv')#registry for city classification
approach_dictionary={'regional':'Region','climate1':'Koppen (by city)','climate2':'Koppen (by station coordinates)'}#approach written in dictionary
ind,dep=[],[]#placeholders for all variables

#record information into lists
for i in range(len(ind_log)):
    ind.append(ind_subset.iloc[i])
    dep.append(dep_subset.iloc[i])

#set up y=x line if chosen
if onetoone==True:
    x=np.linspace(min(ind),max(ind))#range for line
    y=lambda t:t #y(t) function
    
#plot graph
fig=plt.figure()#setup blank figure
for i in range(len(ind)):#go through each point
    if approach!='none':#find a color if an approach is chosen
        color=point_maker(Names[i],labels,approach_dictionary[approach])
    else:
        color='b'
    plt.plot(ind[i],dep[i],marker='o',markerfacecolor=color,markeredgecolor='k',label=Names[i])
plt.xlabel('%s[%s]'%(ind_variable,ind_dataset))
plt.ylabel('%s[%s]'%(dep_variable,dep_dataset))
if onetoone==True: #plot y=x line if selected
    plt.plot(x,y(x),'k')
if title==False:
    plt.title('%s[%s] vs %s[%s]'%(ind_variable,ind_dataset,dep_variable,dep_dataset))
else:
    plt.title(title)
if approach=='regional':
    fig.legend(handles=region_legend,loc=1)
if approach=='climate1':
    fig.legend(handles=climate1_legend,loc=1)
if approach=='climate2':
    fig.legend(handles=climate2_legend,loc=1)
mplcursors.cursor()#set up annotations
plt.show()
fig.savefig('interset 2D graphs\\%s[%s] vs %s[%s] by %s approach'%(ind_variable,ind_dataset,dep_variable,dep_dataset,approach_text[approach]))
