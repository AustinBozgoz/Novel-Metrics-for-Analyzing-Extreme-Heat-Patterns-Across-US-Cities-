#####controls####
#months=[6,10] #range of months to be examined
#years=[] #range of years to be examined

#city=False #if you want to examine a specific city, use it's dirName divider, otherwise put false
#record_city_logs=True #should this information be recorded into the city logs?
#HI_overlay=True #should the final HI plot have the category divisions overlayed?
###actual code###
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from datetime import datetime
from scipy import stats
import os
import logging

logger = logging.getLogger(__name__)

#define functions for determining graph variables
def miami_PDF(root,TauNames,checkpoint='checkpoint.csv',months=[],years=[]):#tests if miami has been analyzed, and if not registers the city log info needed for the rest of the program
    TauColumns=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']#columns to be read
    masterFile=pd.read_csv(root+checkpoint)
    max99s,Q99s=[0]*8,[0]*8
    monthNames=month_translator(months)
    if masterFile[masterFile['dirNames']=='MIA second try']['graphs'].iloc[0]==0:#if it hasn't been analyzed yet
        Tau=tau_loader(root+'MIA second try\\MIA daily maxes 1950 - 2019.csv',months=months,years=years)#open miami tau file
        for i in range(len(max99s)):
            Q99s[i]=np.percentile([item for item in Tau[TauColumns[i]] if item!='M'],99)#call the 99th percentile value for each daily value
            n=0
            for j in range(len(Tau[TauColumns[i]])):
                if Tau[TauColumns[i]].loc[j]!='M':
                    if Tau[TauColumns[i]].loc[j]>=Q99s[i]:
                        max99s[i]+=Tau[TauColumns[i]].loc[j]
                        n+=1.0
            max99s[i]=max99s[i]/n
        return max99s
    else:
        for i in range(len(max99s)):
            log=pd.read_csv(root+'city logs '+TauColumns[i]+' '+monthNames+' '+str(years[0])+'-'+str(years[1])+'.csv')
            max99s[i]=log[log['city']=='MIA second try']['max99']
        return max99s

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
def aaomm_finder(data,mm,category):#given the miami max and data set, finds the annual average over the miami maximum (average number of days per year over miami maximum T or HI)
    year=data['Date'].iloc[0].year#pull the first entry's year
    product=0 #the average that gets returned
    num_years=1.0#the number of years examined
    subset=data[category]#pull out the data set we're examining
    year_total=0 #num of days for the given year
    
    for i in range(len(data)):#for each data entry
        if data['Date'].iloc[i].year!=year:#if we're on to a new year
            num_years+=1.0 #add another year
            product+=year_total #add this number of days to the average numerator
            year_total=0 #reset the number of days in this year
            year=data['Date'].iloc[i].year#change the year
        if (subset.iloc[i]!='M')&(pd.isnull(subset.iloc[i])==False):#if entry isn't missing
            if float(subset.iloc[i])>mm: year_total+=1#if this entry is greater than the mm, add one to the day counter
    
    product=product/num_years #average the numerator
    return product #return the average

def consecutive_day_counter(data,value):#given a data set and a comparative value, calculate the average consecutive number of days above that value
    product=0#average to be returned
    num_groups=0#number of groupings of consecutive days
    num_days=0#number of days in the current group
    
    for i in range(len(data)):#for each data entry
        if num_days==0:#if we're not currently in a combo
            if (data[i]!='M' and i!=(len(data)-1) and pd.isnull(data[i])==False):#if entry isn't missing and isn't the last entry in the list
                if float(data[i])>value: #if entry is above value
                    if data[i+1]!='M':#if next entry isn't missing
                        if float(data[i+1])>value: #and that next day is above value
                            num_groups+=1.0#add another grouping
                            num_days=1 #add a day 1 to the combo
        else:#if we are in a combo
            if data[i]!='M':#if the current data isn't missing
                if float(data[i])>value:#if the entry is above value
                    num_days+=1#that's another day in the combo
                else:#otherwise
                    product+=num_days#the combo is over, add the length we currently have
                    num_days=0#end combo
            else: #if the current day is missing
                if i!=(len(data)-1):#if this isn't the last entry in the list
                    if data[i+1]=='M':#if the next entry is missing as well
                        product+=num_days#the combo is over, add the length we currently have
                        num_days=0#end combo
                    elif float(data[i+1])>value:#otherwise if the next day is above the value
                        num_days+=1#treat this day as another day above the value and move on
                    else: #otherwise, the next day is below the value and we dump this missing one
                        product+=num_days#the combo is over, add the length we currently have
                        num_days=0#end combo
                    
    if num_groups==0:
        product=0
    else:
        product=product/num_groups
    return product

def pd_index(database,column,status):#returns the first index in a column with a certain value (status)
    stop,i=0,0 #loop controls
    while stop==0: #search until target is found
        if i==len(database): #if target is not in list
            print('%s not present in %s[%s]'%(status,database,column)) #print error
            input()#wait for user to recognize
        elif database[column][i]==status:stop=1 #target found
        else: i+=1#otherwise cycle entries
    return i #return index

def PDF_progress(base,checkpoint='checkpoint.csv',update=False,city=None):#tracks progress of the graphs made or loads info on a select city
    #load file and select city    
    masterFile=pd.read_csv(base+checkpoint)
    
    if (update==False)&(city!=None):#if I'm calling a specific city
        nextIndex=pd_index(masterFile,'dirNames',city)#call that city on the list
    else:
        if update==True:
            print('completed city %s'%city) #print that
            completedIndex=pd_index(masterFile,'dirNames',city) #locate city in checkpoint
            masterFile.loc[completedIndex,'graphs']=1 #record it's completion
            masterFile.to_csv(base+checkpoint)#save updated masterfile
        nextIndex=pd_index(masterFile,'graphs',0) #otherwise, call the next incomplete graph
    #load city info
    cityDir=masterFile['dirNames'][nextIndex]
    stationID=masterFile['stationIDs'][nextIndex]
    if cityDir=='MIA second try':
        stationID=''
    for root,dirs,files in os.walk(base+cityDir+'\\'+stationID):
        for i in range(len(files)):
            if 'daily maxes' in files[i]:
                fileName=files[i]
    file=base+cityDir+'\\'+stationID+'\\'+fileName
    stopCity=masterFile['dirNames'][-1]
    return file,cityDir,stationID        
        
def tau_loader(file,months=[],years=[]):#imports daily values files and preps histogram data
    #load data and select timeline
    TauColumns=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']#columns to be read
    Tau=pd.read_csv(file)#load file
    Tau['Date']=pd.to_datetime(Tau['Date'])#prep dates
    if months:#if we selected specific months, pull them out
        Tau=Tau[(Tau['Date'].dt.month>=months[0])&(Tau['Date'].dt.month<=months[1])]
    if years:#same for years
        Tau=Tau[(Tau['Date'].dt.year>=years[0])&(Tau['Date'].dt.year<=years[1])]
    Tau=Tau.reset_index()#reset the index so that it's searchable
    #load dataset
    for i in TauColumns:#for each column
        for j in range(len(Tau)):#for every entry
            if (Tau[i].loc[j]=='M') or (pd.isnull(Tau[i].loc[j])==True):Tau.loc[j,i]=='M'#turn nulls into M
            else:Tau.loc[j,i]=float(Tau[i].loc[j])#otherwise float the number (only thing it could be)
    return Tau
#open and parse data

def PDF_maker(root,Tau,months,years,TauName,miamiMax,cityName,stationID,folder,city=False,HI_overlay=False,record_city_logs=False):
    column=[item for item in Tau[TauName] if (item!='M')&(pd.isnull(item)==False)]#select the column were analyzing
    
    ##analyze complex values
    Q99=np.percentile(column,99)#find the 99th quartile
    n=0 #num of entries in average
    TauMax99=0#calculate Max99 values, defined as the avg of the top 99% of quanities
    
    for i in range(len(column)): #rerecord max99 values
        if column[i]>=Q99:#if in the 99th quartile
            n+=1
            TauMax99+=column[i]#add to average
    TauMax99=TauMax99*1.0/n#average the sum

    
    AAOMM=aaomm_finder(Tau,miamiMax,TauName)
    if 'WBT' in TauName:#if analyzing WBT,
        threshold=80 #the cutoff of interest is 80 degrees
    else: threshold=90 #otherwise it's 90 degrees/percent
    AAOthreshold=aaomm_finder(Tau,threshold,TauName)
    
    Q95=np.percentile(column,95)
    ACDOthreshold=consecutive_day_counter(Tau[TauName],threshold)
    ACDOMM=consecutive_day_counter(Tau[TauName],miamiMax)
    Urange=max(column)-np.average(column)
    Delta=TauMax99-np.average(column)
    
    ##plot graph
    #prep PDF
    TauMin=min(column)#record ranges
    TauMax=max(column)
    bins=np.arange(int(TauMin),int(TauMax),1)#create bins with length=1
    monthNames=month_translator(months)
    if not years:#if no years were selected
        yearNames='%i-%i'%(Tau['Date'].iloc[0].year,Tau['Date'].iloc[-1].year)
        all_time=True
    else:
        yearNames='%i-%i'%(years[0],years[1])
        all_time=False
    #set up graph
    fig=plt.figure(figsize=(24,8))
    plt.hist(column,density=True,bins=bins,color='black')
    plt.ylabel('Probability',fontsize='32')
    plt.xlabel('avg=%.3f  std=%.3f  skew=%.3f #points=%i min=%.3f max99=%.3f median=%.3f mode=%.3f'%(np.average(column),np.std(column),stats.skew(column),len(column),TauMin,TauMax99,np.median(column),stats.mode(column)[0][0]),fontsize='24')
    plt.xticks(np.arange(TauMin-TauMin%5,TauMax-TauMax%5+5,5),fontsize='28')
    plt.yticks(fontsize='28')
    plt.title('Probability of daily %s recorded at %s for %s %s'%(TauName,stationID,monthNames,yearNames))
    
    if ('HI' in TauName) &(HI_overlay==True):#if HI graph and overlays are selected
        #record limits before adding overlay
        xmin,xmax,ymin,ymax=plt.axis()
        #plot categories
        plt.fill_between([80,90],[1,1],0,facecolor='yellow',alpha=.4)
        plt.fill_between([90,103],[1,1],0,facecolor='orange',alpha=.4)
        plt.fill_between([103,124],[1,1],0,facecolor='red',alpha=.4)
        plt.fill_between([124,150],[1,1],0,facecolor='brown',alpha=.4)
        #apply labels
        category_labels=[Line2D([0],[0],marker='s',markerfacecolor='yellow',markeredgecolor='black',label='caution'),
                         Line2D([0],[0],marker='s',markerfacecolor='orange',markeredgecolor='black',label='extreme caution'),
                         Line2D([0],[0],marker='s',markerfacecolor='red',markeredgecolor='black',label='danger'),
                         Line2D([0],[0],marker='s',markerfacecolor='brown',markeredgecolor='black',label='extreme danger')]
        plt.legend(handles=category_labels,loc=1)
        #restore limits
        plt.xlim(xmin,xmax)
        plt.ylim(ymin,ymax)
        fig.savefig(folder+stationID+' '+TauName+' overlay '+monthNames+' '+yearNames)
    
    else:
        fig.savefig(folder+stationID+' '+TauName+' '+monthNames+' '+yearNames)
    if city!=False:#if a specific city is selected, show the graphs
        plt.show()
    
    ##record in logs
    if record_city_logs==True:
        if all_time==True:
            yearNames='all time'
        else:years=str(years[0])+'-'+str(years[1])
        log=pd.read_csv(root+'City_logs\\city logs '+TauName+' '+monthNames+' '+yearNames+'.csv')
        if 'HI' in TauName:
            Pcau,POcau,Pexcau,POexcau,Pdan,POdan,Pexdan=0,0,0,0,0,0,0
            for i in range(len(column)):
                if column[i]>=80:
                    POcau+=1.0
                    if column[i]<90:Pcau+=1.0
                if column[i]>=90:
                    POexcau+=1.0
                    if column[i]<103:Pexcau+=1.0
                if column[i]>=103:
                    POdan+=1.0
                    if column[i]<124:Pdan+=1.0
                if column[i]>=124:Pexdan+=1.0
            Pcau/=len(column)
            POcau/=len(column)
            Pexcau/=len(column)
            POexcau/=len(column)
            Pdan/=len(column)
            POdan/=len(column)
            Pexdan/=len(column)
            row={'city':cityName,'station':stationID,'category':TauName,'avg':np.average(column),
                        'std':np.std(column),'skew':stats.skew(column),'n':len(column),'min':min(column),
                        'max99':TauMax99,'True_max':max(column),'median':np.median(column),'mode':stats.mode(column)[0][0],
                        'AAOMM':AAOMM,'AAO90':AAOthreshold,'95Q':Q95,'ACDO90':ACDOthreshold,'ACDOMM':ACDOMM,
                        'Urange':Urange,'Delta':Delta,'RHavgOverall':Tau['RHavgOverall'].iloc[0],'Pcau':Pcau,'POcau':POcau,'Pexcau':Pexcau,
                        'POexcau':POexcau,'Pdan':Pdan,'POdan':POdan,'Pexdan':Pexdan}
    
        elif 'WBT' in TauName:
            row={'city':cityName,'station':stationID,'category':TauName,'avg':np.average(column),
                        'std':np.std(column),'skew':stats.skew(column),'n':len(column),'min':min(column),
                        'max99':TauMax99,'True_max':max(column),'median':np.median(column),'mode':stats.mode(column)[0][0],
                        'AAOMM':AAOMM,'AAO80':AAOthreshold,'95Q':Q95,'ACDO80':ACDOthreshold,'ACDOMM':ACDOMM,
                        'Urange':Urange,'Delta':Delta,'RHavgOverall':Tau['RHavgOverall'].iloc[0]}
    
        else:
            row={'city':cityName,'station':stationID,'category':TauName,'avg':np.average(column),
                        'std':np.std(column),'skew':stats.skew(column),'n':len(column),'min':min(column),
                        'max99':TauMax99,'True_max':max(column),'median':np.median(column),'mode':stats.mode(column)[0][0],
                        'AAOMM':AAOMM,'AAO90':AAOthreshold,'95Q':Q95,'ACDO90':ACDOthreshold,'ACDOMM':ACDOMM,
                        'Urange':Urange,'Delta':Delta,'RHavgOverall':Tau['RHavgOverall'].iloc[0]}
        row=pd.DataFrame(row,index=[len(log)])
        print(log)
        log=pd.concat([log, row], ignore_index = True)
        print(log)
        delete=False
        for i in range(len(log.columns)):
            if 'Unnamed' in log.columns[i]:
                clear_row=log.columns[i]
                delete=True
        if delete==True: del log[clear_row]
        print(log)
        log.to_csv(root+'City logs\\city logs '+TauName+' '+monthNames+' '+yearNames+'.csv')
    return

def PDF_plotter(root,months,years,city=False,record_city_logs=True,HI_overlay=True):
    TauNames=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']
    checkpoint='checkpoint.csv'
    
    logger.info('Begin PDF plotting')
    #miamiMaxes=miami_PDF(root,TauNames=TauNames,months=months,years=years)#gather miami max99
    miamiMaxes=[0]*8 #edit this out if you want to use another city in comparison, you might also want to rename the variables
    if city!=False:#for a specific city
        file,cityDir,stationID=PDF_progress(root,city=city)#pick out city info
        Tau=tau_loader(root+file,months,years)#read file and store tau columns in tuple
        for i in range(len(TauNames)):
            PDF_maker(Tau,months,years,TauNames[i],miamiMaxes[i],cityDir,stationID,folder=root+cityDir+'\\'+stationID+'\\',city=city,HI_overlay=HI_overlay,record_city_logs=record_city_logs)
    else:#for the full list
        stop=0
        update=False
        city=None
        while stop==0:
            file,cityDir,stationID,stopCity=PDF_progress(root,update=update,city=city)
            logger.info('Analyzing %s'%stationID)
            Tau=tau_loader(root+file,months,years)#read file and store tau columns in tuple
            for i in range(len(TauNames)):
                logger.info('Creating PDF %s %s'%(stationID,TauNames[i]))
                PDF_maker(root,Tau,months,years,TauNames[i],miamiMaxes[i],cityDir,stationID,folder=root+cityDir+'\\'+stationID+'\\',city=False,HI_overlay=HI_overlay,record_city_logs=record_city_logs)
            update=True#update the city we just did
            city=cityDir
            logger.info('Done with City'%stationID)
            if city==stopCity:stop=1
    return





