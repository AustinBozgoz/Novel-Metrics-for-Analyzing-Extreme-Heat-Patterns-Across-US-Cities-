import requests
import pandas as pd
from io import StringIO
import sys
import os
import logging

logger = logging.getLogger(__name__)

def get_lcd_data(station_id, startYear, endYear): #request to pull the LCD data using NOAA's API
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    
    #adjust the download date for the beginning and end of the selected decade
    #should be ten years at a time to prevent the API request from timing out
    start_date=str(startYear)+'-01-01' 
    end_date=str(endYear)+'-12-31'
    
    #establish parameters to feed to the api
    params = {
        "dataset": "local-climatological-data",
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "format": "csv",
        "units": "standard", # Use 'metric' if preferred
        "includeAttributes": "true"
    }
    
    print('Requesting data for station %s (%s - %s)...'%(station_id,startYear,endYear))
    response = requests.get(base_url, params=params) #send request to NOAA servers
    
    if response.status_code == 200:#if returned a proper response
        #record response as pandas dataframe
        df = pd.read_csv(StringIO(response.text), low_memory=False)
        return df
    else: #otherwise, print response code and text
        print(f'Error: {response.status_code}')
        print(response.text)
        logger.info(f'Error: {response.status_code}')
        logger.info(response.text)
        return None

def date_segmenter(startYear,endYear): #breaks the year range requested by the user into ten year segments so as to not overwhelm the api
    #confirm that years are in integer form
    startInt,endInt=float(startYear),float(endYear)
    if (startInt.is_integer==False) or (endInt.is_integer==False):
        print('Error, Years should be in integer form')
        return False,0
    #confirm the years are not a ridiculous range (between 1900 and 2100)
    if (int(startYear)<1900) or (int(endYear)<1900):
        print('Error, Records should not begin before 20th century')
        return False,0
    if (int(startYear)>2100) or (int(endYear)>2100):
        print('Error, Records should not go past 21th century')
        return False,0
    #confirm that end year is after start year
    if int(startYear)>int(endYear):
        print('Error, Start Year should be before End Year')
        return False,0
    
    #establish first decade to download
    if type(startYear)!=str:startYear=str(startYear)
    if type(endYear)!=str:endYear=str(endYear)
    begin,end=startYear[0:3]+'0',startYear[0:3]+'9' #first decade begins with a XXX0 and ends with XXX9
    years=[[begin,end]] #record decade in the full list of all decade ranges
    finish=0 #while loop end trigger
    while finish==0: 
        if years[-1][1]>=endYear:finish=1 #end loop if the end year was contained within the last recorded decade
        else: years.append([str(int(years[-1][0])+10),str(int(years[-1][1])+10)]) #otherwise record the next decade
    return True,years #return a confirmation for the year range and the list of all decades
            
def lcd_user_interface(): #user interface for retrieving API download info
    guard=False
    while guard==False:
        print('\n \n Please input the 11-digit API ID for the station you want to pull data for')
        print('View the read me on the github if you need help finding this ID')
        stationID=input()
        if len(stationID)!=11:
            print('Station ID should be 11 digits long')
        else:
            print('Is %s the correct station ID (y/n)'%stationID)
            response=input()
            if (response=='Y') or (response=='y'):guard=True
    
    guard=False
    while guard==False:
        print('\n \n Please input the city,state format for this station')
        print('e.g. Atlanta, GA or Austin, TX; mind the capitilizaiton and comma')
        city=input()
        if len(city)==0:
            print('Please give an input')
        else:
            print('Is %s the correct city,state (y/n)'%city)
            response=input()
            if (response=='Y') or (response=='y'):guard=True
    
    guard=False
    while guard==False:
        print('\n \n Please input the 3 letter designator for this station')
        print('Note this is not an official designator and one you create for your records')
        print('e.g. Miami international airport would be MIA, mind the capitilzation')
        ID=input()
        if len(ID)!=3:
            print('Please give a 3 letter input')
        else:
            print('Is %s the correct 3 letter designator (y/n)'%ID)
            response=input()
            if (response=='Y') or (response=='y'):guard=True
    
    guard=False
    while guard==False:
        print('\n \n Please input a start year for analysis')
        startYear=input()
        print('Please input a end year for analysis')
        endYear=input()
        
        print('Is %s - %s correct (y/n)'%(startYear,endYear))
        print('Note that for every decade, it will take 3-5 minutes to pull and save the data')
        response=input()
        if (response=='Y') or (response=='y'):
            guard,years=date_segmenter(startYear,endYear)
    return stationID, city, ID, years

def LCD_csv_saver(cwd,df,stationID,city,ID,years): #records downloaded API information in the correct folders
    os.makedirs(cwd+'\\NOAA_LCD_CSVs\\',exist_ok=True) #creates housing folder for all LCD info
    os.makedirs(cwd+'\\NOAA_LCD_CSVs\\'+city+'\\',exist_ok=True)#creates folder for the specific city, state
    os.makedirs(cwd+'\\NOAA_LCD_CSVs\\'+city+'\\'+ID+' LCD\\',exist_ok=True) #creates folder for the specific station
    
    df.to_csv(cwd+'\\NOAA_LCD_CSVs\\'+city+'\\'+ID+' LCD\\'+ID+'_LCD_'+str(years[0])+'-'+str(years[1])+'.csv') #records the dataframe
    return

def station_text_file(cwd,stationID,city,ID):
    with open("Station Info.txt", "w") as f:
        f.write('%s LCD'%ID)
        f.write("ID number %s"%stationID)
        f.write("City: %s"%city)
    return
def LCD_API_Pull(cwd):#overall code for this module
    logger.info('Beginning LCD API Pull')
    stationID,city,ID,years=lcd_user_interface() #retrieve api download information from user
    print('\n \n Pulling data, estimated time: %i-%i minutes'%(len(years)*3,len(years)*5)) #provide estimate for total download time
    logger.info('Requesting LCD Data')
    for i in years: #for each decade range
        logger.info('Requesting Data for %s - %s'%(i[0],i[1]))
        data=get_lcd_data(stationID,i[0],i[1]) #download information using the api
        logger.info('Received Request Results for %s - %s'%(i[0],i[1]))
        if data is not None: #if dataframe is not empty
            if not data.empty: #and actually contains rows
                print('Successfully retrieved %i rows' %len(data))
                logger.info('Successfully retrieved %i rows' %len(data))
                
                logger.info('Attempting to save csv for %s - %s'%(i[0],i[1]))
                LCD_csv_saver(cwd,data,stationID,city,ID,i) #record dates
                print('Successfully recorded csv for %s - %s'%(i[0],i[1]))
                logger.info('Successfully recorded csv for %s - %s'%(i[0],i[1]))
            else: #otherwise if it doesn't contain rows, noaa has no data for the requested decade
                print('The request worked, but NOAA has no records for those dates')
                logger.info('The request worked, but NOAA has no records for those dates')
                
        else: #if the response failed, record it in the logs and report to the user
           print('The request failed entirely (Server error or Timeout)')
           logger.info('The request failed entirely (Server error or Timeout)')
    
    #recording station text file
    logger.info('Recording station text')
    station_text_file(cwd,stationID,city,ID)
    logger.info('API data pull complete')
    return






