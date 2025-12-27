#run to create a blank log book
#will overwrite whatever is in the same folder, so be careful before you run
dtype='all' #T/RH/HI/WBT of max/avg, or all
months=[6,10]
years=[]

def month_translator(months):#given start and end months, return 3 letter abrieviations, otherwise return the word annual
    if months:
        product=[0,0]    
        for i in range(2):
            if months[i]==1:product[i]='jan'
            if months[i]==2:product[i]='feb'
            if months[i]==3:product[i]='mar'
            if months[i]==4:product[i]='apr'
            if months[i]==5:product[i]='may'
            if months[i]==6:product[i]='jun'
            if months[i]==7:product[i]='jul'
            if months[i]==8:product[i]='aug'
            if months[i]==9:product[i]='sep'
            if months[i]==10:product[i]='oct'
            if months[i]==11:product[i]='nov'
            if months[i]==12:product[i]='dec'
        return product[0]+'-'+product[1]
    else:
        return 'annual'
    
import pandas as pd
types=['Tmax','Tavg','RHmax','RHavg','HImax','HIavg','WBTmax','WBTavg']
if dtype=='all':
    taskList=types
else:
    taskList=[dtype]
for dtype in taskList:
    if 'WBT' in dtype:
        data={'city':[0],'station':[0],'category':[0],'avg':[0],'std':[0],'skew':[0],'n':[0],'min':[0],'max99':[0],'True_max':[0],'median':[0],'mode':[0],'AAOMM':[0],'AAO80':[0],'95Q':[0],'ACDO80':[0],'ACDOMM':[0],'Urange':[0],'Delta':[0],'RHavgOverall':[0]}
    elif 'HI' in dtype:
        data={'city':[0],'station':[0],'category':[0],'avg':[0],'std':[0],'skew':[0],'n':[0],'min':[0],'max99':[0],'True_max':[0],'median':[0],'mode':[0],'AAOMM':[0],'AAO90':[0],'95Q':[0],'ACDO90':[0],'ACDOMM':[0],'Urange':[0],'Delta':[0],'RHavgOverall':[0],
              'Pcau':[0],'POcau':[0],'Pexcau':[0],'POexcau':[0],'Pdan':[0],'POdan':[0],'Pexdan':[0]}
    else:
        data={'city':[0],'station':[0],'category':[0],'avg':[0],'std':[0],'skew':[0],'n':[0],'min':[0],'max99':[0],'True_max':[0],'median':[0],'mode':[0],'AAOMM':[0],'AAO90':[0],'95Q':[0],'ACDO90':[0],'ACDOMM':[0],'Urange':[0],'Delta':[0],'RHavgOverall':[0]}
    log=pd.DataFrame(data)
    monthNames=month_translator(months)
    if not years:
        yearNames='all time'
    else: yearNames=str(years[0])+'-'+str(years[1])
    log.to_csv('city logs %s %s %s.csv'%(dtype,monthNames,yearNames))

