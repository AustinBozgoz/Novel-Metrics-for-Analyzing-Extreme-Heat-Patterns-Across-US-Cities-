import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress,skewnorm,norm
import numpy as np
from scipy import stats
import math
import os
import calendar
import logging

logger = logging.getLogger(__name__)


#import daily csv
def daily_csv_importer(LCD_path,file,years='all',base=''):#imports and prepares daily csv file of LCD data
    csv=pd.read_csv(base+LCD_path+file)
    #delete relic 
    for i in csv.columns:#purge relic columns
        if 'Unnamed' in i: csv=csv.drop(i,axis=1)
    #convert date column to date-time format
    csv['Date']=pd.to_datetime(csv['Date'])#prep dates
    if years!='all':
        csv[(csv['Date'].dt.year>=years[0])&(csv['Date'].dt.year<=years[1])]
    return csv

def daily_climograph(file,csv,quantity,month,day,LCD_path,base='',save=False,display=True): #Must be run before the other climograph functions. Creates a time series climograph of a station for a given day of the year, returns a line of best fit (with time as the independent value) and the probability that the graph is actually constant (determined by the p-value)
    y=csv[(csv['Date'].dt.month==month)&(csv['Date'].dt.day==day)&(csv[quantity]!=0)].dropna(subset=[quantity]) #pulls the data for the chosen month and day
    x=y['Date'].dt.year #prepares the yearly values as the independent variable
    
    #linear regression
    m, b, r, p, se = linregress(x.tolist(), y[quantity].tolist(),alternative='two-sided') #two sided dictates that the alt. hypothesis is that the slope is nonzero (i.e. the dependent value changes with time)
    linepts=np.linspace(min(x),max(x)) #independent values for the line of best fit
    linedep=m*linepts+b #dependent values for the line of best fit
    #the returned values include slope (m), intercept (b), r value between the two values (r), p value describing evidence for the null hypothesis (p), standard error for the estimated slope (se)
    #if the p-value is less than 0.05, that is strong statistical evidence that the slope is nonzero (i.e. the value is increasing or decreasing with time) 
    
    title=file[0:-4]+' of '+quantity+' for '+str(month)+'-'+str(day)
    
    #plot
    fig=plt.figure()
    plt.title(title)
    plt.plot(x,y[quantity],marker='o',ls='none') #plot actual data values
    if 'RH' in quantity:plt.ylabel(quantity)
    else:plt.ylabel(quantity+r' ($^o$f)')
    plt.xlabel('m:%.3f b:%.3f r:%.3f p:%.3f se:%.3f'%(m,b,r,p,se))
    plt.plot(linepts,linedep,ls='solid') #plot line of best fit
    if display==True:plt.show()
    
    os.makedirs(base+LCD_path+'climographs\\', exist_ok=True) #checks to see if the folder housing the plots has already been made. This is the reason this function has to be run first.
    if save==True:fig.savefig(base+LCD_path+'climographs\\'+title+' timeseries') #saves figure if passed the save command
    
    return

def daily_histogram_grapher(file,csv,quantity,month,day,LCD_path,base='',save=False,display=True): #creates a histogram climograph of a station for a given day of the year, returns the average, stddev, and skew values for the histogram. 
    #These returned values make the assumption that the values are independent of time, and therefore if the p-value from the timeseries histograph is less than 0.05, these values and the subsequent theoretical histogram are not viable for use in analysis
    y=csv[(csv['Date'].dt.month==month)&(csv['Date'].dt.day==day)&(csv[quantity]!=0)].dropna(subset=[quantity]) #pulls the data for the chosen month and day
    x=y['Date'].dt.year #prepares the yearly values as the independent variable
    
    #histogram grapher
    TauMin=min(y[quantity])#record ranges
    TauMax=max(y[quantity])
    bins=np.arange(int(TauMin),int(TauMax),1)#create bins with length=1
    
    title=file[0:-4]+' of '+quantity+' for '+str(month)+'-'+str(day)
    
    #plot
    fig=plt.figure(figsize=(10,6))
    plt.title(title)
    plt.hist(y[quantity],density=True,bins=bins,color='black')#plot data values
    plt.ylabel('Probabilty')
    if 'RH' in quantity:plt.xlabel(quantity)
    else:plt.xlabel(quantity+r' ($^o$f)')
    if display==True:plt.show()
    
    
    avg,std,skew=np.average(y[quantity]),np.std(y[quantity]),stats.skew(y[quantity]) #find values used to reproduce the histogram
    if save==True:fig.savefig(base+LCD_path+'climographs\\'+title+' histogram') #save histogram
    return avg,std,skew

def daily_theoretical_histogram(avg,std,skew,file,quantity,month,day,LCD_path,base='',save=False,display=True):  #creates a theoretical histogram climograph of a station for a given day of the year, based on the derived average, stddev, and skew values from the past values
    num_samples = 10000 #set a number of datapoints to be generated
    data = skewnorm.rvs(a=skew, loc=avg, scale=std, size=num_samples)  #generate the histogram data points
    
    title=file[0:-4]+' of '+quantity+' for '+str(month)+'-'+str(day)
    
    #plot
    fig=plt.figure(figsize=(10, 6))
    plt.title(title)
    plt.hist(data, bins=50, density=True, alpha=0.6, color='b', label='Generated Skewed Data') #plot the histogram
    plt.ylabel('Probability')
    if 'RH' in quantity:plt.xlabel(quantity+'avg=%.3f std=%.3f skew=%.3f'%(avg,std,skew))
    else:plt.xlabel(quantity+r' ($^o$f) avg=%.3f std=%.3f skew=%.3f'%(avg,std,skew))
    plt.show()
    
    if save==True:fig.savefig(base+LCD_path+'climographs\\'+title+' theoretical histogram') #save the histogram
    return

def histogram_value_at_percentile(avg,std,skew,roll): #returns the value of a histogram at a given percentile (out of 1). Takes the derived results from an analyzed histogram (avg, stddev, and skew)
    num_samples = 10000 #set a number of datapoints to be generated
    data = skewnorm.rvs(a=skew, loc=avg, scale=std, size=num_samples) #generate the histogram's data points
    adj_roll=math.ceil(num_samples*roll) #grab the data entry corresponding to the point at the percentile. Round up 
    data.sort() #order the data by value
    
        
    return data[adj_roll] #return the corresponding histogram value

def month_day_range(month): #returns a iterable list of all the days for a given month. Skip the 29th day in february since there won't be enough values to make a statistically significant estimation
    max_days=calendar.monthrange(2025,month)
    if month==2: return range(1,29) #skip the last day in a leap-year february
    else: return range(1,max_days[1]+1)

def pd_index(database,column,status):#returns the first index in a column with a certain value (status)
    stop,i=0,0 #loop controls
    while stop==0: #search until target is found
        if i==len(database): #if target is not in list, print error message and stop code
            print('%s not present in %s[%s]'%(status,database,column)) #print error
            input()#wait for user to recognize
        elif database[column][i]==status:stop=1 #target found
        else: i+=1#otherwise cycle entries
    return i #return index


def progress_controller_climograph(checkpoint='checkpoint.csv',update=False,city='',base=''): #manages the checkpoint file and returns entries needed to operate the LCD file program
    ##load checkpoint file    
    masterFile=pd.read_csv(base+checkpoint)
    
    ##update list
    if update==True:#if we've completed a city
        print('completed city %s'%city) #print that
        completedIndex=pd_index(masterFile,'dirNames',city) #locate city in checkpoint
        masterFile.loc[completedIndex,'graphs']=1 #record it's completion
        masterFile.to_csv(base+checkpoint)#save updated masterfile
    
    ##find info on next city
    nextIndex=pd_index(masterFile,'graphs',0) #find next city in checkpoint
    currentCity=masterFile['dirNames'][nextIndex] #record the city name/1st directory
    stationID=masterFile['stationIDs'][nextIndex]
    currentDir=currentCity+'\\'+stationID+'\\'#record directory
    
    stopCity=masterFile['dirNames'].iloc[-1]
    return currentCity,currentDir,stationID,stopCity

def daily_max_file_find(currentDir,stationID,base=''): #locates the daily max file for the current city directory
    count=0 #tracks how many daily max files are in the folder
    for root,dirs,files in os.walk(base+currentDir): #find all files in the directory
        for item in files: #inspect each
            if 'daily maxes' in item: #if it's a daily max file
                count+=1 #add to the count
                if count==1:file=item #mark the name to be returned if it's the first we found
                else: #if it's not the first we found,
                    logger.info('More than 1 daily max file in %s for station %s'%(currentDir,stationID)) #log the error in the file
                    if int(file[20:24])>int(item[20:24]):file=item #take the daily max file with the earliest beginning (assuming they have the same end date here)
    return file

def daily_climograph_trend_analysis(date='annual',city='all',stationID='',years='all',quantity='all',base='',save_plots=True,display_plots=False):
    logger.info('Beginning Climograph Analysis')
    quantityList=['Tmax','Tavg','HImax','WBTmax','WBTavg','RHavg','RHmax']
    
    if city=='all': #for all the cities
        logger.info('Analyzing all cities')
        currentCity,currentDir,stationID,stopCity=progress_controller_climograph(checkpoint='checkpoint.csv',update=False,city='',base=base) #pull the data for the first city
        logger.info('Analyzing city: %s station %s'%(currentCity,stationID))
        stop=0
        while stop!=1: #stop after analyzing the last city
            logger.info('Pulling Daily Max File')
            file=daily_max_file_find(currentDir,stationID,base) #find the name of the daily max file
            logger.info('Cleaning Daily Max Database')
            csv=daily_csv_importer(currentDir,file,years,base) #pull csv for the given station
            if date=='annual': #for the full year
                logger.info('Analyzing For the Full Year')
                months=range(1,13) #create iterative list for months
                for month in months: #for each month
                    logger.info('Analyzing Month %i'%month)
                    days=month_day_range(month) #create iterative list for days
                    for day in days: #for each day in month
                        logger.info('Analyzing Day %i'&day)
                        if quantity=='all': #for all quantities
                            for Tau in quantityList: #go through each quantity
                                logger.info('Analyzing Quantity %s'%Tau)
                                logger.info('Creating Climograph')
                                daily_climograph(file,csv,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                                logger.info('Creating Histogram')
                                avg,std,skew=daily_histogram_grapher(file,csv,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                                logger.info('Creating Theoretical Histogram')
                                daily_theoretical_histogram(avg,std,skew,file,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                                logger.info('Done with %s'%Tau)
                        
                        else: #for one quantity
                            logger.info('Analyzing Quantity %s'%quantity)
                            logger.info('Creating Climograph')
                            daily_climograph(file,csv,quantity,month,day,currentDir,base,save=save_plots,display=display_plots)
                            logger.info('Creating Histogram')
                            avg,std,skew=daily_histogram_grapher(file,csv,quantity,month,day,currentDir,base,save=save_plots,display=display_plots)
                            logger.info('Creating Theoretical Histogram')
                            daily_theoretical_histogram(avg,std,skew,file,quantity,month,day,currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Done with %i - %i'%(month,day))
            else: #for a singular date
                if quantity=='all': #for all quantities
                    for Tau in quantity: #go through each quantity
                        logger.info('Analyzing Quantity %s'%Tau)
                        logger.info('Creating Climograph')
                        daily_climograph(file,csv,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Creating Histogram')
                        avg,std,skew=daily_histogram_grapher(file,csv,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Creating Theoretical Histogram')
                        daily_theoretical_histogram(avg,std,skew,file,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Done with %s'%Tau)
                else: #for one quantity
                    logger.info('Creating Climograph')
                    daily_climograph(file,csv,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Creating Histogram')
                    avg,std,skew=daily_histogram_grapher(file,csv,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Creating Theoretical Histogram')
                    daily_theoretical_histogram(avg,std,skew,file,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Done')
            if currentCity==stopCity: 
                stop=1
                logger.info('Done with city: %s station %s'%(currentCity,stationID))
                logger.info('Done with Analysis')
            else:
                logger.info('Done with city: %s station %s'%(currentCity,stationID))
                currentCity,currentDir,stationID,stopCity=progress_controller_climograph(checkpoint='checkpoint.csv',update=True,city=currentCity,base=base)#pull the  information for the next city
                logger.info('Analyzing city: %s station %s'%(currentCity,stationID))
    
    else: #for a singular city
        currentDir=currentCity+'\\'+stationID+'\\'#record directory
        logger.info('Checking directory %s'%currentDir)
        logger.info('Pulling Daily Max File')
        file=daily_max_file_find(currentDir,stationID,base) #find the name of the daily max file
        logger.info('Cleaning Daily Max Database')
        csv=daily_csv_importer(currentDir,file,years,base) #pull csv for the given station
        if date=='annual': #for the full year
            logger.info('Analyzing For the Full Year')
            months=range(1,13) #create iterative list for months
            for month in months: #for each month
                logger.info('Analyzing Month %i'%month)
                days=month_day_range(month) #create iteratiive list for days
                for day in days: #for each day in month
                    logger.info('Analyzing Day %i'&day)
                    if quantity=='all': #for all quantities
                        for Tau in quantity: #go through each quantity
                            logger.info('Analyzing Quantity %s'%Tau)
                            logger.info('Creating Climograph')
                            daily_climograph(file,csv,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                            logger.info('Creating Histogram')
                            avg,std,skew=daily_histogram_grapher(file,csv,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                            logger.info('Creating Theoretical Histogram')
                            daily_theoretical_histogram(avg,std,skew,file,Tau,month,day,currentDir,base,save=save_plots,display=display_plots)
                            logger.info('Done with %s'%Tau)
                    else: #for one quantity
                        logger.info('Analyzing Quantity %s'%quantity)
                        logger.info('Creating Climograph')
                        daily_climograph(file,csv,quantity,month,currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Creating Histogram')
                        avg,std,skew=daily_histogram_grapher(file,csv,quantity,month,day,currentDir,base,save=save_plots,display=display_plots)
                        logger.info('Creating Theoretical Histogram')
                        daily_theoretical_histogram(avg,std,skew,file,quantity,month,day,currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Done with %i - %i'%(month,day))
        else: #fr a singular date
            if quantity=='all': #for all quantities
                for Tau in quantity: #go through each quantity
                    logger.info('Analyzing Quantity %s'%Tau)
                    logger.info('Creating Climograph')
                    daily_climograph(file,csv,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Creating Histogram')
                    avg,std,skew=daily_histogram_grapher(file,csv,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Creating Theoretical Histogram')
                    daily_theoretical_histogram(avg,std,skew,file,Tau,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                    logger.info('Done with %s'%Tau)
            else: #for one quantity 
                logger.info('Creating Climograph')
                daily_climograph(file,csv,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                logger.info('Creating Histogram')
                avg,std,skew=daily_histogram_grapher(file,csv,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                logger.info('Creating Theoretical Histogram')
                daily_theoretical_histogram(avg,std,skew,file,quantity,date[0],date[1],currentDir,base,save=save_plots,display=display_plots)
                logger.info('Done')
    return


