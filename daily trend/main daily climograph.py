#!/usr/bin/env python3
#controls
LCD_analyze=False #should the LCD folders in the NOAA_LCD_CSVs directory be analyzed or have they already been analyzed (True/False)


quantity='all' #daily max quantity to be used. options are:'all','Tmax','Tavg','HImax','WBTmax','WBTavg','RHavg','RHmax'
city='all' #give the exact name of the city as the folder is written within the NOAA_LCD_CSVs directory, or list 'all' to analyze all the cities in that folder
stationID='' #the 3 letter id code for the chosen station of the selected city, can leave it blank if using all cities
date='annual' #what day to analyze the climatography for, written in the format [MO,DA] (so january first is [1,1]), or write 'annual' to analyze every day of the year excluding february 29th
year_range='all' #year range to include in the climograph analysis (written in format [start,end]), or choose 'all' to use all available years

save_plots=True #save plots (True/False)
display_plots=False #display the plots in python (True/False) note: if you're doing a lot of cities or a lot of dates this will seriously slow down your system

##################################################################################

import os
import sys
import checkpoint_maker
import LCD_hourly_daily_max
import logging
import daily_climograph_trend_analysis


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Daily Climograph.log"), # Saves to a file
        logging.StreamHandler()              # Also prints to your terminal
    ]
)

def main(LCD_analyze,quantity,city,stationID,date,year_range,save_plots,display_plots):
    current_directory = os.getcwd()
    if (LCD_analyze==True) or (city=='all'):
        logging.info('Making Checkpoint...')
        checkpoint_maker.checkpoint_maker('new',current_directory+'\\NOAA_LCD_CSVs\\')
    if LCD_analyze==True:
        logging.info('Beginning LCD Analysis')
        LCD_hourly_daily_max.LCD_hourly_daily_max(current_directory+'\\NOAA_LCD_CSVs\\')
    logging.info('Beginning Analysis')
    daily_climograph_trend_analysis.daily_climograph_trend_analysis(date,city,stationID+' LCD',year_range,quantity,current_directory+'\\NOAA_LCD_CSVs\\',save_plots,display_plots)
    logging.info('Script Complete')
    return


if __name__ == "__main__":
    main(LCD_analyze,quantity,city,stationID,date,year_range,save_plots,display_plots)    
    
