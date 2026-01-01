import os
import pandas as pd
import logging
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

def load_dailymax_csv(file,station,city):#load and prepare dailymax csv
    df=pd.read_csv(file)
    for i in df.columns:#purge relic columns
        if 'Unnamed' in i: df=df.drop(i,axis=1)
    
    df['City']=[city]*len(df)
    df['Station ID']=[station]*len(df)
    return df

def daily_max_combiner(base,sql_database):#combine all daily max files
    checkpoint=pd.read_csv(base+'checkpoint.csv')#load master file
    
    #create overall database
    logger.info('Creating overall database')
    column_names=['City','Station ID','Date','Tmax','Tavg','HImax','HIavg','WBTmax','WBTavg','RHavg','RHmax','RHavgOverall']
    dailymax_df=pd.DataFrame(columns=column_names)

    
    for i in range(len(checkpoint['dirNames'])):#for each city
        #check that the daily max file is there
        exists=False
        city,station=checkpoint['dirNames'].iloc[i],checkpoint['stationIDs'].iloc[i]
        logger.info('Observing daily max file for %s: %s'%(city,station))
        for root,dirs,files in os.walk(base+city+'\\'+station+'\\'):
            for i in files:
                if 'daily maxes' in i: 
                    exists=True
                    csv=i
        if exists==False:
            logger.info('Error: daily max for %s: %s not present'%(city,station))

        
        else:
            #load and prepare daily max file
            logger.info('Loading file %s for %s:%s'%(csv,city,station))
            df=load_dailymax_csv(base+city+'\\'+station+'\\'+csv,station,city)
    
            #combine it to overall database
            logger.info('Concating Data for %s:%s'%(city,station))
            dailymax_df=pd.concat([df,dailymax_df],ignore_index=True)
        
    #export final database
    logger.info('Finishing Daily-max database')
    engine = create_engine("sqlite:///"+sql_database+"-daily.db")
    dailymax_df.to_sql(sql_database+'-daily', con=engine, if_exists='replace', index=False)
    logger.info('Daily-max database complete')
    return

def load_citylog_csv(file,months,years):#load and prepare dailymax csv
    df=pd.read_csv(file)
    for i in df.columns:#purge relic columns
        if 'Unnamed' in i: df=df.drop(i,axis=1)
    
    df['Month Range']=[months]*len(df)
    df['Years Range']=[years]*len(df)
    return df

def city_log_combiner(base,sql_database):
    #record list of logs
    csv=[]
    for root,dirs,files in os.walk(base):
        for i in files:
            if 'city logs' in i:csv.append(i)
    
    logger.info('Creating Overall database')
    column_names=['city','station','category','avg','std','skew','n','min','max99','True_max','median','mode','AAOMM','AAO90','95Q','ACDO80','ACDO90','ACDOMM','Urange','Delta','RHavgOverall','Pcau','POcau','Pexcau','POexcau','Pdan','POdan','Pexdan']
    citylog_df=pd.DataFrame(columns=column_names)
    
    for i in range(len(csv)):
        spaces=0
        for j in range(len(csv[i])):
            if csv[i][j]==' ':spaces+=1
            if spaces==2:monthsbegin=j+2
            if spaces==3:
                monthsend=j+2
                yearsbegin=j+2
            if csv[i][j]=='.':yearsend=j
            
        #labels for months and years
        months=csv[i][monthsbegin:monthsend]
        years=csv[i][yearsbegin:yearsend]
        
        #pull database
        logger.info('Pulling Data from %s'%csv[i])
        df=load_citylog_csv(base+csv[i],months,years)
        
        #combine into main database
        logger.info('Concating Data for %s'%csv[i])
        citylog_df=pd.concat([df,citylog_df],ignore_index=True)
    
    #export final database
    logger.info('Finishing City-log database')
    engine = create_engine("sqlite:///"+sql_database+"-citylog.db")
    citylog_df.to_sql(sql_database+'-citylog', con=engine, if_exists='replace', index=False)
    logger.info('Citylog database complete')
    return

def sql_databaser(root,sql_database):
    logger.info('Creating Daily-max database')
    daily_max_combiner(root,sql_database)
    
    logger.info('Creating City log database')
    city_log_combiner(root+"City_logs\\",sql_database)
    
    return
