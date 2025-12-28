#!/usr/bin/env python3
months=[]
years=[]


import os
import sys
import checkpoint_maker
import LCD_hourly_daily_max
import PDF_plotter
import log_maker

def main(months,years):
    current_directory = os.getcwd()
    checkpoint_maker('new',current_directory+'\\NOAA_LCD_CSVs\\')
    LCD_hourly_daily_max(current_directory+'\\NOAA_LCD_CSVs\\')
    log_maker(current_directory+'\\NOAA_LCD_CSVs\\City_logs\\',months=months,years=years)
    PDF_plotter(current_directory+'\\NOAA_LCD_CSVs\\',months=months,years=years)
    return

if __name__ == "__main__":
    main(months,years)
    
