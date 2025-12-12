#opens T and HI city logs and plots graphs based on given columns
##############controls##############
months=[6,10]
years=[]
dependent='Delta'#y axis column for graph, use delta for max99-avg
independent='Latitude'#x axis column for graph, use delta for max99-avg

title=False #custom title, record false for default
approach='all' #commands are none, regional, climate1 (koppen by region), or all
#or climate2 (koppen by coordinates); the approach for the graph to identify and label points

ref_line=False #should there be a consistent reference line in each graph?
m=1 #slope of ref line
b=-20 #y-intercept of ref line
##########actual code##################

#import packages
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import plotly.io as pio
import plotly.express as px
import numpy as np
import pandas as pd
import mplcursors

dtype=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']

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

def month_translator(months):#given start and end months, return 3 letter abrieviations, otherwise return the word annual
    if months:
        product=[0,0]    
        for i in range(2):
            if months[i]==1:product[i]='jan'
            if months[i]==2:product[i]='feb'
            if months[i]==3:product[i]='mar'
            if months[i]==4:product[i]='apr'
            if months[i]==5:product[i]='may'
            if months[i]==6:product[i]='jun'
            if months[i]==7:product[i]='jul'
            if months[i]==8:product[i]='aug'
            if months[i]==9:product[i]='sep'
            if months[i]==10:product[i]='oct'
            if months[i]==11:product[i]='nov'
            if months[i]==12:product[i]='dec'
        return product[0]+'-'+product[1]
    else:
        return 'annual'

def year_translator(years):#unpacks years selected to a string
    if years:
        product='%s-%s'%(years[0],years[1])
    else:product='all time'
    return product

def city_log_import(csv,dependent,independent,dtype):#import data, return x and y
    log=pd.read_csv(csv)
    if dependent=='ACDO' or dependent=='AAO':
        if 'WBT' in dtype:
            dependent=dependent+'80'
        else: depdendent=dependent+'90'
    if independent=='ACDO' or independent=='AAO':
        if 'WBT' in dtype:
            independent=independent+'80'
        else: indepdendent=independent+'90'
    
    depSubset=[]
    indSubset=[]
    City=[]
    for i in range(len(log)):
        depSubset.append(log[dependent].iloc[i])
        indSubset.append(log[independent].iloc[i])
        City.append(log['City'].iloc[i])
    return log, dependent, independent,depSubset,indSubset,City
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


def city_log_grapher(dtype,depSubset,indSubset,cities,ref_line,m,b,approach,dependent,independent,title,monthNames,yearNames):#given x and y data, return and save the selected plots
    approach_text={'regional':'regional','climate1':'climate by surroundings','climate2':'climate by coordinates'}
    approach_dictionary={'regional':'Region','climate1':'Koppen (by city)','climate2':'Koppen (by station coordinates)'}
    labels=pd.read_csv('registry.csv')
   
    #setup reference line
    
    #plot graph
    fig=plt.figure()
    for i in range(len(indSubset)):
        if approach!='none':
            color=point_maker(cities[i],labels,approach_dictionary[approach])
        else:
            color='b'
        plt.plot(indSubset[i],depSubset[i],marker='o',markerfacecolor=color,markeredgecolor='k',label=cities[i])
    plt.xlabel(independent)
    plt.ylabel(dependent)
    if ref_line==True:
        #x range and y function
        x=np.linspace(0,max(indSubset))
        y=lambda t:m*t+b
        xmin,xmax,ymin,ymax=plt.axis()
        
        #plot line
        plt.plot(x,y(x),'c--')
        
        #restore limits
        plt.xlim(xmin,xmax)
        plt.ylim(ymin,ymax)
        
        if title==False:
            plt.title('%s vs %s for %s %s %s (m=%.2f, b=%.2f)'%(independent,dependent,dtype,monthNames,yearNames,m,b))
        else:
            plt.title('%s %s %s %s (m=%.2f, b=%.2f)'%(dtype,title,monthNames,yearNames,m,b))
    
    else:
        if title==False:
            plt.title('%s vs %s for %s %s %s'%(independent,dependent,dtype,monthNames,yearNames))
        else:
            plt.title('%s %s %s %s'%(dtype,title,monthNames,yearNames))
    if approach=='regional':
        fig.legend(handles=region_legend,loc=1)
    if approach=='climate1':
        fig.legend(handles=climate1_legend,loc=1)
    if approach=='climate2':
        fig.legend(handles=climate2_legend,loc=1)
    mplcursors.cursor()#set up annotations
    plt.show()
        #save figure
    if ref_line==True:
        fig.savefig('2D graphs\\%s vs\\%s vs %s for %s by %s approach w reference.png'%(independent,independent, dependent,dtype,approach_text[approach]))
    else:
        fig.savefig('2D graphs\\%s vs\\%s vs %s for %s by %s approach.png'%(independent,independent, dependent,dtype,approach_text[approach]))

    
        
yearNames=year_translator(years)
monthNames=month_translator(months)
lastLog=0
if approach=='all'
    approachTypes=['regional','climate1','climate2']
else:
    approachTypes=[approach]
for approach in approachTypes:
    for i in dtype:
        log,dependent,independent,depSubset,indSubset,cities=city_log_import('geospatial %s %s %s.csv'%(i,monthNames,yearNames),dependent,independent,i)
        if type(lastLog)!=int:
            for j in range(len(log['City'])):
                if (log['City'][j]==lastLog['City'][j])==False:
                    print('error on city matchup: %s for %s and %s for %s'(log['City'][j],log['category'][j],lastLog['City'][j],lastLog['category'][j]))
                    input()
            lastLog=log
    
        #various things for graphing
        city_log_grapher(i,depSubset,indSubset,cities,ref_line,m,b,approach,dependent,independent,title,monthNames,yearNames)
    