#!/usr/bin/env python3
months=[] #month range to analyze
years=[] #year range to analyze
sql_database='LCD Analysis' #name for sql databases

import os
import sys
import checkpoint_maker
import LCD_hourly_daily_max
import PDF_plotter
import log_maker
import sql_databaser
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("LCD to PDF.log"), # Saves to a file
        logging.StreamHandler()              # Also prints to your terminal
    ]
)

def main(months,years):
    current_directory = os.getcwd()
    logging.info("Making Checkpoint....")
    checkpoint_maker('new',current_directory+'\\NOAA_LCD_CSVs\\')
    logging.info('Beginning LCD Analysis....')
    LCD_hourly_daily_max(current_directory+'\\NOAA_LCD_CSVs\\')
    logging.info('Creating Overall City Log....')
    log_maker(current_directory+'\\NOAA_LCD_CSVs\\City_logs\\',months=months,years=years)
    logging.info('Creating PDFs....')
    PDF_plotter(current_directory+'\\NOAA_LCD_CSVs\\',months=months,years=years)
    logging.info('Creating SQL Database...')
    sql_databaser(current_directory+'\\NOAA_LCD_CSVs\\',sql_database)
    logging.info('Program Complete')
    return

if __name__ == "__main__":
    main(months,years,sql_database)
    
