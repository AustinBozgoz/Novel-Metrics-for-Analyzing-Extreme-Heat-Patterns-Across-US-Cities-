import os
import pandas as pd
function='new' #choices include new (new checkpoint spreadsheet),clear/fill status/graph/both (reset/fill status or graph columns or both)
root='C:\\Users\\bozgo\\OneDrive - University of Miami\\research projects\\Tmax pdfs'


if function=='new':
    dirNames=os.listdir(root)
    dirNames=[item for item in dirNames if (item[-3:]!='.py') and (item[-3:]!='csv') and (item[-3:]!='png') and (item!='City logs') and (item[0:5]!='maryb') and (item[0:5]!='MIA t')]

    stationIDs=[]

    for item in dirNames:
        if item=='MIA second try': stationIDs.append('')
        else: 
            for root,dirs,files in os.walk(item):
                for labels in dirs:
                    if len(labels)!=0:
                        if labels[-3:]=='LCD':stationIDs.append(labels)

    productDict={'dirNames':dirNames,'stationIDs':stationIDs,'status':[0]*62,'graphs':[0]*62}
    product=pd.DataFrame(productDict)
else:
    if 'clear' in function:
        if 'both' in function:
            instructions=[0,0]
        elif 'status' in function:
            instructions=[0,'null']
        elif 'graphs' in function:
            instructions=['null',0]
    elif 'fill' in function:
        if 'both' in function:
            instructions=[1,1]
        elif 'status' in function:
            instructions=[1,'null']
        elif 'graphs' in function:
            instructions=['null',1]
    product=pd.read_csv('checkpoint.csv')
    for i in range(len(product)):
        if instructions[0]!='null':
            product.loc[i,'status']=instructions[0]
        if instructions[1]!='null':
            product.loc[i,'graphs']=instructions[1]
product.to_csv('checkpoint.csv')
