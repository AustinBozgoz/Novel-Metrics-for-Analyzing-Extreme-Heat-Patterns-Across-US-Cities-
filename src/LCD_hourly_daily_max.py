#opens multiple files from NOAA's LCD data set and saves the Tmax, HImax, WBmax, RHavg, and RHmax in a seperate file
#files must be in a jan 1st to dec 31st format, spaced nine years apart
#must be saved in form STA_LCD_xxX0-xxX9.csv
#exports as STA_MAX_xxX0-xxX9.csv
#-----------actual code--------------


import pandas as pd
import numpy as np
from metpy.calc import heat_index
from metpy.units import units
import time
import os


def pd_index(database,column,status):#returns the first index in a column with a certain value (status)
    stop,i=0,0 #loop controls
    while stop==0: #search until target is found
        if i==len(database): #if target is not in list, print error message and stop code
            print('%s not present in %s[%s]'%(status,database,column)) #print error
            input()#wait for user to recognize
        elif database[column][i]==status:stop=1 #target found
        else: i+=1#otherwise cycle entries
    return i #return index

def progress_controller(checkpoint='checkpoint.csv',update=False,city=None,base=None): #manages the checkpoint file and returns entries needed to operate the LCD file program
    ##load checkpoint file    
    masterFile=pd.read_csv(base+checkpoint)
    
    ##update list
    if update==True:#if we've completed a city
        print('completed city %s'%city) #print that
        completedIndex=pd_index(masterFile,'dirNames',city) #locate city in checkpoint
        masterFile.loc[completedIndex,'status']=1 #record it's completion
        masterFile.to_csv(base+checkpoint)#save updated masterfile
    
    ##find info on next city
    nextIndex=pd_index(masterFile,'status',0) #find next city in checkpoint
    currentCity=masterFile['dirNames'][nextIndex] #record the city name/1st directory
    stationID=masterFile['stationIDs'][nextIndex]
    if currentCity=='MIA second try':
        currentDir=currentCity+'\\'
        stationID='MIA'
    else:
        currentDir=currentCity+'\\'+stationID+'\\'#record directory
    
    ###>write file names
    fileNames,startYears,endYears=[],[],[]
    for root,dirs,files in os.walk(currentDir):
        for item in files:
            if (item[-3:]=='csv') and (item[0:7]==stationID[0:3]+'_LCD'):
                fileNames.append(item)
                startYears.append(item[8:12])
                endYears.append(item[8:11]+'9')
    
    stopCity=masterFile['dirNames'][-1]
    return currentCity,currentDir,stationID,fileNames,startYears,endYears,stopCity



    
def HV_csv(startYears,endYears):#create an empty version of the product csv for hourly values
    #record start and end dates
    start='1/1/'+startYears[0]
    end='12/31/'+endYears[-1]

    dateRange=pd.date_range(start=start,end=end)#create a date range for my data frame
   
    #create PDF
    dictionary={'Date':dateRange,'Tmax':[0]*len(dateRange),'Tavg':[0]*len(dateRange),'HImax':[0]*len(dateRange),'HIavg':[0]*len(dateRange),'WBTmax':[0]*len(dateRange),'WBTavg':[0]*len(dateRange),'RHavg':[0]*len(dateRange),'RHmax':[0]*len(dateRange)}
    productCSV=pd.DataFrame(dictionary)
    return productCSV
   




def unit_assigner(T,R):#assigns fahrenheit units to T and puts RH on the [0,1] scale
    return float(T)*units.fahrenheit,float(R)/100.0

def load_LCD(currentDir,fileNames,position):#loads a specific data set, and prepares the date-time correction
    data=pd.read_csv(currentDir+fileNames[position],dtype=str)#call a data set
    data['DATE']=pd.to_datetime(data['DATE'])#scrub each date in the data set (full year)
    
    dictionary={'DATE':data['DATE'],'HourlyDryBulbTemperature':data['HourlyDryBulbTemperature'],'HourlyRelativeHumidity':data['HourlyRelativeHumidity'],'HourlyWetBulbTemperature':data['HourlyWetBulbTemperature']}#reduce the database to the columns needed
    data=pd.DataFrame(dictionary)
    return data

def entry_parser_LCD(entry):#LCD data contains some random letters in entries, this scrubs the nonnumerical values and returns something useable
     if type(entry)==str:#if its a string
         if entry.isnumeric()==False:#if the string contains a letter
             result=''#create a product array (str) that gets built
             for k in range(len(entry)):#parse each value in the entry
                 if (entry[k].isnumeric==True) or (entry[k]=='.'):#only record numbers
                     result+=entry[k]
             if result=='':#if nothing gets recorded (it's not a not numerical entry)
                 return 'M' #record missing value
             else: #otherwise
                 return float(result) #return numbers and the error message
         else: #if a string with only numbers
            return float(entry) #return original string
     else: #if not a string
         return float(entry) #otherwise it's a number, just return that
        
    
def daily_max(data,date,RHavgall):#returns daily results as a list in with T/RH/HI/WBT/ interspered with max/avg values
    #pull data for the day
    examined_date=data[(data['DATE'].dt.year==date.year)&(data['DATE'].dt.month==date.month)&(data['DATE'].dt.day==date.day)]
    #create containers for information
    dailyResults=[-1000,-1000,-1000,-1000,-1000,-1000,-1000,-1000]#T/RH/HI/WBT interspered with max/avg values; final results 
    
    if examined_date.empty==True:#record null values for missing days
        dailyResults=['M','M','M','M','M','M','M','M']
        
    else: #if not empty
        array=[[0]*12*48 for i in range(4)]#array for all daily values; make enough for 12*24 daily entries in case of multiple per hour
        #written as T,RH,HI,WBT
        for i in range(len(examined_date)):#for each entry in list
            array[0][i]=entry_parser_LCD(examined_date['HourlyDryBulbTemperature'].iloc[i]) #record Temp
            array[1][i]=entry_parser_LCD(examined_date['HourlyRelativeHumidity'].iloc[i]) #record RH
            if (array[0][i]!='M')&(array[1][i]!='M'):#if the temp and RH aren't missing for this time entry
                T,R=unit_assigner(array[0][i],array[1][i])#assign units for HI calculation
                array[2][i]=heat_index(T,R,mask_undefined=False).magnitude[0]#record heat index
            else: array[2][i]='M' #if either is missing, record HI as missing
            array[3][i]=entry_parser_LCD(examined_date['HourlyWetBulbTemperature'].iloc[i])
        
        #record max values
        dailyResults[0]=max([item for item in array[0] if (pd.isnull(item)==False) and (item!='M')])
        dailyResults[2]=max([item for item in array[1] if (pd.isnull(item)==False) and (item!='M')])
        dailyResults[4]=max([item for item in array[2] if (pd.isnull(item)==False) and (item!='M')])
        dailyResults[6]=max([item for item in array[3] if (pd.isnull(item)==False) and (item!='M')])
         
        #pull out nonmissing entries averages
        dailyResults[1]=np.average([item for item in array[0] if (item!='M') and (pd.isnull(item)==False) and (item!=0)])
        dailyResults[3]=np.average([item for item in array[1] if (item!='M') and (pd.isnull(item)==False) and (item!=0)])
        dailyResults[5]=np.average([item for item in array[2] if (item!='M') and (pd.isnull(item)==False) and (item!=0)])
        dailyResults[7]=np.average([item for item in array[3] if (item!='M') and (pd.isnull(item)==False) and (item!=0)])
        RHavgall[0]+=sum([item for item in array[1] if (pd.isnull(item)==False) and (item!='M')])
        RHavgall[1]+=len([item for item in array[1] if (item!=0) and (pd.isnull(item)==False) and (item!='M')])
        
        #if all values are missing or errored and somehow don't get changed before this, change it
        for i in range(len(dailyResults)):
            if dailyResults[i]==-1000:dailyResults[i]='M'
    
    return dailyResults,RHavgall
   
def HV_writer(dailyResults,currentProduct,Date):#record daily results into a selected date on the csv
    columns=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']#columns to be cycled through
    index=pd_index(currentProduct,'Date',Date)
    
    for i in range(len(columns)):
        currentProduct.loc[index,columns[i]]=dailyResults[i]#record daily results into the respective columns
    
    return currentProduct


def LCD_analyze(currentDir,fileNames,endYears,currentProduct,RHavgall):#returns how long it takes to prepare a single file and how long it takes to calculate a single day
    filePosition=0#select the first file
    data=load_LCD(currentDir,fileNames,filePosition)#load first file
    for i in range(len(currentProduct)):    
        date=currentProduct['Date'].iloc[i]#pull date
    
        if date.year>int(endYears[filePosition]):#if this is the start of the new year, switch to the next file
            filePosition+=1
            if filePosition==len(fileNames):#prevent loading nonexistent files
                print('error trying to load too many files')
                input()
            else:data=load_LCD(currentDir,fileNames,filePosition)#load data
        else:
            print(currentDir)
            print('%i/%i'%(i,len(currentProduct)))#print progress
            results,RHavgall=daily_max(data,date,RHavgall)#get results
            currentProduct=HV_writer(results,currentProduct,date)#record results
            print(currentProduct.loc[i])#print results
            print(RHavgall)
    return currentProduct,RHavgall
    



def LCD_hourly_daily_max(base):
    stop,update,city=0,False,0#set up variables for initial run
    while stop==0:
        currentCity,currentDir,currentStation,fileNames,startYears,endYears,stopCity=progress_controller(update=update,city=city,base=base)#pull all variables needed to analyze this city
        currentProduct=HV_csv(startYears,endYears)#create the blank csv
        RHavgall=[0,0] #2-d array with [sum, number of entries] for calculating the overall RH for a city
        
        
        ##analyze data
        currentProduct,RHavgall=LCD_analyze(base+currentDir,fileNames,endYears,currentProduct,RHavgall)#record info
        
        #add overall RH column
        RHoverall=RHavgall[0]*1.0/RHavgall[1]#calculate overall average
        currentProduct.insert(9,'RHavgOverall',[RHoverall]*len(currentProduct),True)#add it to the product database

        #save file
        currentProduct.to_csv(base+currentDir+currentStation+' daily maxes %s - %s.csv'%(startYears[0],endYears[-1]))
        update=True#rewrite status of analyzed city on next loop
        city=currentCity#name of city analyzed
        if city==stopCity:stop=1
    return
