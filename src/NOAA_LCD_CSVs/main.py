import os

#for the sake of the atmospheric scientists not that versed in python
cwd=os.path.dirname(os.path.abspath(__file__))#locate directory with scripts
os.chdir(cwd) #change directory to where scripts are located

import sys
import checkpoint_maker
import LCD_hourly_daily_max
import PDF_plotter
import log_maker
import sql_databaser
import LCD_API_download
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True,
    handlers=[
        logging.FileHandler("LCD to PDF.log",mode='a',encoding='utf-8',delay=False), # Saves to a file
        #logging.StreamHandler()              # Also prints to your terminal
    ]
)

def main(cwd):
    print('Working in path %s \n \n'%cwd)
    finish=0
    
    while finish==0:
        print('This code runs in a 3 step sequence')
        print('(1) Download hourly weather data from a particular station')
        print('(2) Analyze hourly weather data and convert it into daily max/avgs')
        print('(3) Create Probability Distribution Plots and SQL Databases of daily max/avgs')
        print('Please select a step using a number')
    
        selection=input()
    
        if '1' in selection:
            logging.info('Beginning API Data Pull...')
            LCD_API_download.LCD_API_Pull(cwd)
            logging.info('Successfully pulled data from API')
            finish=1
        
        elif '2' in selection:
            logging.info('Beginning Daily Max/Avg conversion...')
            print('\n \n Please select a function')
            print('(1) Convert daily max/avg for one city within \\NOAA_LCD_CSVs\\')
            print('(2) Convert daily max/avg for all cities within \\NOAA_LCD_CSVs\\')
            selection=input()
            
            if '1' in selection:
                guard=0
                while guard==0:
                    print('\n \n Input the city, state exactly as its listed in the \\NOAA_LCD_CSVs\\ folder')
                    print('e.g. Austin, TX or Atlanta, GA; mind the capitalization and space')
                    city=input()
                    if os.path.exists(cwd+'\\NOAA_LCD_CSVs\\'+city)==True:guard=1
                    else: 
                        print('Error no directory %s'%(cwd+'\\NOAA_LCD_CSVs\\'+city))
                        print('Check capitalization and syntax')
                
                guard=0
                while guard==0:
                    print('\n \n Input the 3 letter designator exactly as its listed in the \\NOAA_LCD_CSVs\\ %s folder'%city)
                    print('Only the 3 letter designator, do not include the LCD')
                    ID=input()
                    if os.path.exists(cwd+'\\NOAA_LCD_CSVs\\'+city+'\\'+ID+' LCD')==True:guard=1
                    else: 
                        print('Error no directory %s'%(cwd+'\\NOAA_LCD_CSVs\\'+city+'\\'+ID+' LCD'))
                        print('Check capitalization and syntax')
                logging.info('Converting daily max/avg for one city %s %s LCD ...'%(city,ID))
                LCD_hourly_daily_max.LCD_hourly_daily_max(cwd+'\\NOAA_LCD_CSVs\\',oneCity=city,oneStation=ID)
                logging.info('Completed conversion for %s %s LCD'%(city,ID))
                finish=1
                
            elif '2' in selection:
                guard=0
                while guard==0:
                    print('\n \n Please select a function')
                    print('(1) Start a new conversion for all cities within \\NOAA_LCD_CSVs\\')
                    print('(2) Continue an interrupted conversion for all cities within \\NOAA_LCD_CSVs\\')
                    selection=input()
                
                    if '1' in selection:
                        guard=1
                        logging.info("Making Checkpoint....")  
                        checkpoint_maker.checkpoint_maker('new',current_directory+'\\NOAA_LCD_CSVs\\')
                        logging.info('Beginning LCD Analysis....')
                        LCD_hourly_daily_max.LCD_hourly_daily_max(cwd+'\\NOAA_LCD_CSVs\\')
                        logging.info('Completed LCD Analysis for all cities')
                        finish=1
                    
                    elif ('2' in selection) and (os.path.isfile(cwd+'\\NOAA_LCD_CSVs\\checkpoint.csv')==False):
                        print('Error, missing checkpoint file within \\NOAA_LCD_CSVs\\, please choose 1 as your selection')
                    else:
                        logging.info('Beginning LCD Analysis....')
                        LCD_hourly_daily_max.LCD_hourly_daily_max(cwd+'\\NOAA_LCD_CSVs\\')
                        logging.info('Completed LCD Analysis for all cities')
                        finish=1
                        
            elif '3' in selection:
                guard=0
                while guard==0:
                    print('\n \n Are we analyzing for a specific month range (y/n)?')
                    selection=input()
                    if (selection=='y') or (selection=='Y'):
                        guard1=0
                        while guard1==0:
                            print('Enter the number of the starting month (e.g. April would be 4)')
                            startMonth=input()
                            if (startMonth.isnumeric()==True) and (startMonth.is_integer==True):
                                if (int(startMonth)>0) and (int(startMonth)<13):
                                    guard1=1
                                else: print('Starting Month should be between 1 and 12 for the months of the year')
                            else: print('Starting month should be an integer')
                        guard1=0
                        while guard1=0:
                            print('Enter the number of the ending month (e.g. April would be 4)')
                            endMonth=input()
                            if (endMonth.isnumeric()==True) and (endMonth.is_integer==True):
                                if (int(endMonth)>0) and (int(endMonth)<13):
                                    guard1=1
                                else: print('Ending Month should be between 1 and 12 for the months of the year')
                            else: print('Ending month should be an integer')
                        guard=1
                        months=[startMonth,endMonth]
                    elif (selection=='n') or (selection=='N'):months=[]
                    else: print('Please respond y or n')
                guard=0
                while guard==0:
                    print('\n \n Are we analyzing for a specific year range (y/n)?')
                    selection=input()
                    if (selection=='y') or (selection=='Y'):
                        guard1=0
                        guard2=0
                        while guard2==0
                            while guard1==0:
                                print('Enter the starting year')
                                startYear=input()
                                if (startYear.isnumeric()==True) and (startYear.is_integer==True):
                                    if (int(startYear)>1900) and (int(startYear)<2100):
                                        guard1=1
                                    else: print('Starting Year should be between 1900 and 2100')
                                else: print('Starting Year should be an integer')
                            guard1=0
                            while guard1=0:
                                print('Enter the ending year')
                                endYear=input()
                                if (endYear.isnumeric()==True) and (endYear.is_integer==True):
                                    if (int(endYear)>1900) and (int(endYear)<2100):
                                        guard1=1
                                    else: print('Ending Year should be between 1900 and 2100')
                                else: print('Ending month should be an integer')
                            guard=1
                            if endYear<startYear:print('End year should be after start year')
                            else:guard2=1
                        years=[startYear,endYear]
                    elif (selection=='n') or (selection=='N'):years=[]
                    else: print('Please respond y or n')
                    
                    guard=0
                    while guard==0:
                        print('\n \n Should an SQL database be created (y/n)?')
                        selection=input()
                    
                        if (selection=='y') or (selection=='Y'):
                            SQL=true
                            guard1=0
                            while guard1==0:
                                print('\n \n Record a name for the database')
                                SQLtitle=input()
                                print('Is %s correct?'%SQLtitle)
                                selection=input()
                                if (selection=='y') or (selection=='Y'):guard1=1
                                
                                    
                    
                    
        else:
            print('Please make a selection 1-3 \n \n')
    #logging.info("Making Checkpoint....")
    #checkpoint_maker.checkpoint_maker('new',current_directory+'\\NOAA_LCD_CSVs\\')
    #logging.info('Beginning LCD Analysis....')
    #LCD_hourly_daily_max.LCD_hourly_daily_max(current_directory+'\\NOAA_LCD_CSVs\\')
    #logging.info('Creating Overall City Log....')
    #log_maker.log_maker(current_directory+'\\NOAA_LCD_CSVs\\City_logs\\',months=months,years=years)
    #logging.info('Creating PDFs....')
    #PDF_plotter.PDF_plotter(current_directory+'\\NOAA_LCD_CSVs\\',months=months,years=years)
    #logging.info('Creating SQL Database...')
    #sql_databaser.sql_databaser(current_directory+'\\NOAA_LCD_CSVs\\',sql_database)
    #logging.info('Program Complete')
    return

if __name__ == "__main__":
    main(cwd)
