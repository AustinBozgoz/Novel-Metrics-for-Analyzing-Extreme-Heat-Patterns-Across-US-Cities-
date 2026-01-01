# Automated Daily Maximum Transformation Pipeline for the National Oceananic and Atmospheric Administration's Local Climatological Database

Developed a robust ETL (extract, transform, load) pipeline for converting long-term hourly weather data the National Oceaning and Atmospheric Administration's Local Climatological Database (LCD) into daily maximum/average quantities useful for atmospheric and public health inquries. The program imports hourly readings of temperature and relative humidity, makes corrections for or ignores erroneous entries, and outputs daily maximum/average readings for Temperature, Heat index, Wet-bulb temperature, and Relative Humidity for every city given to it. It also creates probability distribution plots for those values for each city, and consolidates statistical information for each one of those cities into one large database, allowing for easy comparisons of extreme heat behavior for cities across the United States or even the world.

# Technical Information:

Language: Python 3.11+

Libraries: Pandas, SQLalchemy (Dataframes), NumPy (Matrix Math), MetPy (Atmospheric calcs), Scipy (Stats), Matplotlib (Visualization).

Infrastructure: Logging (System monitoring).

# Project Architecture:

Data Input: Reads raw csv's from NOAA's LCD database (https://www.ncdc.noaa.gov/cdo-web/datatools/lcd). The database only permits data downloading one decade at a time, and as such you must download the information each decade starting at January 1st at the beginning of the decade (or whenever the sation first started collecting information) to the last day in the decade (as in December 31st, the 9th year of the decade). E.g. for the 1980s of a particular station, the csv should be dated from January 1st, 1980 to December 31st, 1989. If the station started in 1985, it is also acceptable to use a csv of [Any month] [Any day], 1985 to December 31st, 1989. Manual Adjustments to the code will need to be made in order to include csv's of more recent years (i.e. past 2019)

Error Correction: Checks hourly readings and removes letters from entries, ignores blank entries, checks that values are reasonable (e.g. temperature is not in the thousands of degrees)

Processing: Uses MetPy for unit-aware calculations (e.g. Heat Index) and Scipy for probability distribution plot analysis as well as outlier detection.

Output: Generates cleaned data, hourly readings of daily maximum/average temperature, heat index, wet-bulb temperature, relative humidity; generates probability distribution plots of those variables for each city; generates a log of quantitative descriptors for those probability distribution plots for comparing extreme values between cities. Also generates 2 large SQL databases: one for all the daily maxes searchable by city/station, another for all the probability distribution descriptors searchable by month range, year range, and heat descriptor.

# Key Features:

Modular Design: Every major Step of the ETL pipeline is seperated into a different script and outputs its transformation into a seperate and meticulously labelled database. This allows for versatility of use for this project not only to find extreme heat values but to also utilize daily maximum values from any city within the LCD database. The error correction function is also cleanly seperated as a standalone function, allowing for any future programmer to easily clean and utilize the LCD database for any project.

Unit Based Calculations: Incorporated metpy in order to ensure consistent use of fahrenheit for all heat-index related calculations

Versatility: Utilized directory packages and organization to permit for a theoretically unlimited number of cities within the analysis. Also included simple controls for the sake of limiting the analysis timeframe to any month or year range as specified by the user.

Resilence: Implemeneted a global logging system in order to track which csv's or cities are corrupted.

Performance: Implemeneted a combination of numpy vectorization and standard python loops in order to optimize performance of high-volume datasets and ensure accuracy of calculations.



# Clone the repo
git clone https://github.com/AustinBozgoz/Novel-Metrics-for-Analyzing-Extreme-Heat-Patterns-Across-US-Cities-

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python src/main.py

