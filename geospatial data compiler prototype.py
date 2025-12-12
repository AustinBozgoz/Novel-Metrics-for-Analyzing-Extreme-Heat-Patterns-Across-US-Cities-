#compiles city log infromation with registries
############controls############
months=[6,10]
years=[]

#############actual code#########
import numpy as np
import pandas as pd

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

dtype=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']
def geospatial_compiler(product,cityLog):#given product database with registry information and the correct city logs, fill out missing information and return finished product
    columns=cityLog.columns[2:]#list of all columns to be used recorded from city_logs to product
    
    for i in range(len(product)):#for each city
        city=product['City'][i]#call city name from product db
        
        subframe=cityLog[cityLog['city']==city]#from the city log, pull the row for the correct city
        if len(subframe)==0:#if the city can't be called, raise an error and alert operator
            print('error: City cannot be called for %s'%city)
            input()
        
        for j in columns:#for each entry in columns
            print('i:%i'%i)
            print('j:%s'%j)
            product.loc[i,j]=subframe[j].iloc[0]
    return product

for i in dtype:
    if 'WBT' in i:#wbt uses a 80 degree cutoff temperature for certain variables
        data={'City':[],'Region':[],'Koppen (by city)':[],'Koppen (by station coordinates)':[],'Latitude':[],'Longitude':[],
              'station':[],'category':[],'avg':[],'std':[],'skew':[],'n':[],'min':[],'max99':[],'True_max':[],'median':[],'mode':[],
              'AAOMM':[],'AAO80':[],'95Q':[],'ACDO80':[],'ACDOMM':[],'Urange':[],'Delta':[],'RHavgOverall':[]}
    elif 'HI' in i:
        data={'City':[],'Region':[],'Koppen (by city)':[],'Koppen (by station coordinates)':[],'Latitude':[],'Longitude':[],
              'station':[],'category':[],'avg':[],'std':[],'skew':[],'n':[],'min':[],'max99':[],'True_max':[],'median':[],'mode':[],
              'AAOMM':[],'AAO90':[],'95Q':[],'ACDO90':[],'ACDOMM':[],'Urange':[],'Delta':[],'RHavgOverall':[],'Pcau':[],'POcau':[],'Pexcau':[],'POexcau':[],'Pdan':[],'POdan':[],'Pexdan':[]}
    else:#90 degree cutoff otherwise
        data={'City':[],'Region':[],'Koppen (by city)':[],'Koppen (by station coordinates)':[],'Latitude':[],'Longitude':[],
              'station':[],'category':[],'avg':[],'std':[],'skew':[],'n':[],'min':[],'max99':[],'True_max':[],'median':[],'mode':[],
              'AAOMM':[],'AAO90':[],'95Q':[],'ACDO90':[],'ACDOMM':[],'Urange':[],'Delta':[],'RHavgOverall':[]}

    product=pd.DataFrame(data)#<- final csv to eventually be saved
    #open registry and record information into product
    registry=pd.read_csv('registry.csv')
    product=pd.concat([product,registry],ignore_index=True)#ignore_index makes the new concated database searchable, v important
    if years:
        yearNames='%i-%i'%(Tau['Date'].iloc[0].year,Tau['Date'].iloc[-1].year)
        all_time=True
    else:
        yearNames='all time'
    #open selected city log and save corresponding variables to the right slots
    selected_log=pd.read_csv('city logs %s %s %s.csv'%(i,monthNames,yearNames))#open city log
    product=geospatial_compiler(product,selected_log)#rewrite all entries

    #save finished product
    product.to_csv('geospatial %s %s %s.csv'%(i,monthNames,yearNames))
