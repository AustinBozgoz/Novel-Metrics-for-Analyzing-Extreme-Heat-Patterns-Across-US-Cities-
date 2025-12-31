Title: Automated Daily Maximum Transformation Pipeline for the National Oceananic and Atmospheric Administration's Local Climatological Database

Developed a robust ETL (extract, transform, load) pipeline for converting the National Oceaning and Atmospheric Administration's Local Climatological Database (LCD) into daily maximum quantities useful for atmospheric and public health inquries. The program imports hourly readings of temperature and relative humidity, makes corrections for or ignores erroneous entries, and outputs daily maximum readings for Temperature, Heat index, Wet-bulb temperature, and Relative Humidity for every city given to it. It also creates probability distribution plots for those values for each city, and consolidates statistical information for each one of those cities into one large database, allowing for easy comparisons of extreme heat behavior for cities across the United States or even the world.

Technical Information:
Language: Python 3.11+
Libraries: Pandas (Dataframes), NumPy (Matrix Math), MetPy (Atmospheric calcs), Scipy (Stats), Matplotlib (Visualization).
Infrastructure: Logging (System monitoring).
