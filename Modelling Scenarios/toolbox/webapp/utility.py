import pandas as pd
import numpy as np
from CONF import couList,iso2,urlbase
import dash_html_components as html
import dash_table
import datetime
mobData={}
mobDataGoogle={}


def getMobilityDataGoogle1(cou):
    if not cou in mobDataGoogle:
        Fname=urlbase+'mobCouGoogle/2020_'+iso2[cou]+'_Region_Mobility_Report.csv'
        mb=pd.read_csv(Fname,parse_dates=['date'], index_col=['country_region_code','sub_region_1','date'])
        try:
            nan=mb.xs(iso2[cou]).index[0][0]
            index=mb.xs(iso2[cou]).index
            mbData=mb.xs(iso2[cou])
            vv=[]
            dd=[]
            rt=np.array(mbData['retail_and_recreation_percent_change_from_baseline'])
            gr=np.array(mbData['grocery_and_pharmacy_percent_change_from_baseline'])
            pa=np.array(mbData['parks_percent_change_from_baseline'])
            tr=np.array(mbData['transit_stations_percent_change_from_baseline'])
            wp=np.array(mbData['workplaces_percent_change_from_baseline'])
            re=np.array(mbData['residential_percent_change_from_baseline'])

            vPar=rt*0.25+gr*0.2+pa*0.1+tr*0.2+wp*0.2-re*0.05
            dd=[]
            vv=[]
            for j in range(len(index)):
                if str(index[j][0])=='nan':
                    dd.append(index[j][1])
                    vv.append(vPar[j])

        except Exception as e:
            print(e)
            dd=[]
            vPar=[]
        mobDataGoogle[cou]=[dd,vPar]
    dd,vv0=mobDataGoogle[cou]
    if len(dd)>0:
        vmax=-1e9;vmin=1e9
        for j in range(len(vv0)):
            if vv0[j]>vmax:vmax=vv0[j]
            if vv0[j]<vmin:vmin=vv0[j]
            #print(dd[j],vv0[j])
        if vmax-vmin!=0:
            vv=(vv0-vmin)/(vmax-vmin)*6.0
    else:
        dd=[];vv=[]
    # print(dd,vv)
    return dd,vv

def getMobilityDataGoogle(cou):
    if not cou in mobDataGoogle:
        
        Fname=urlbase+'mobCouGoogle/2020_'+iso2[cou]+'_Region_Mobility_Report.csv'
        #mb=pd.read_csv(Fname,parse_dates=['date'], index_col=['country_region_code','sub_region_1','date'])
        print(Fname)
        try:
            mb=pd.read_csv(Fname)
        except:
            return [[],[]]
        try:
            mbData=mb[mb.sub_region_1.isna()]
            vv=[]
            dd=[]
            rt=np.array(mbData['retail_and_recreation_percent_change_from_baseline'])
            gr=np.array(mbData['grocery_and_pharmacy_percent_change_from_baseline'])
            pa=np.array(mbData['parks_percent_change_from_baseline'])
            tr=np.array(mbData['transit_stations_percent_change_from_baseline'])
            wp=np.array(mbData['workplaces_percent_change_from_baseline'])
            re=np.array(mbData['residential_percent_change_from_baseline'])
#
            vPar=rt*0.25+gr*0.2+pa*0.1+tr*0.2+wp*0.2-re*0.05
            dd=mbData['date']
        except Exception as e:
            print(e)
            dd=[]
            vPar=[]
        mobDataGoogle[cou]=[dd,vPar]
    dd,vv0=mobDataGoogle[cou]
    if len(dd)>0:
        #vmax=-1e9;vmin=1e9
        #for j in range(len(vv0)):
        #    if vv0[j]>vmax:vmax=vv0[j]
        #    if vv0[j]<vmin:vmin=vv0[j]
        #    #print(dd[j],vv0[j])
        vmax=vv0.max()
        vmin=vv0.min()
        if vmax-vmin!=0:
            vv=(vv0-vmin)/(vmax-vmin)*4.0
    else:
        dd=[];vv=[]
    # print(dd,vv)
    return dd,vv

def extractMobility():
    fnameIn='E:/CV\Mobility data/mobility-indicators-NUTS0123.csv'
    dirOut='E:/CV/Mobility data/countries/'
    import pandas as pd
    fnameIn='mobility-indicators-NUTS0123.csv'
    dirOut='./countries/'

    md=pd.read_csv(fnameIn, usecols=['date','country_code','area_type','operator','indicator_name','indicator_value'], 
                parse_dates=['date'], index_col=['country_code','area_type','operator','indicator_name','date'])
    countryMob =['Austria','Belgium','Bulgaria','Czech Republic','Germany','Denmark','Estonia','Greece',
                    'Spain','Finland','France','Croatia','Hungary','Ireland','Italy','Latvia','Norway','Portugal','Romania','Sweden','Slovenia','Slovakia']
    countryIso=['AT','BE','BG','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LV','NO','PT','RO','SE','SI','SK']

    for j in range(len(countryIso)):
        cou=countryMob[j]
        iso2=countryIso[j]
        try:
            mobData=md.xs(iso2).xs('NUTS0_ID').xs(1)['indicator_value'].sort_index()
            mobData.to_csv(dirOut+cou+'.csv')
            print(cou,mobData.index[-1],mobData[-1])
        except:
            print('data not found for ',cou)
            continue
        
def getMobilityData(cou):
    countryMob =['Austria','Belgium','Bulgaria','Czech Republic','Germany','Denmark','Estonia','Greece','Spain','Finland','France','Croatia','Hungary','Italy','Latvia','Norway','Portugal','Romania','Sweden','Slovenia','Slovakia']
    if not cou in countryMob:
        return [],[]
    if not cou in mobData:
        
        url=urlbase+'mobCou/'+cou+'.csv'
        print(url)
        mob = pd.read_csv(url, usecols=['date', 'indicator_value'], parse_dates=['date'], index_col=['date'])
        mobData[cou]=mob
    vv=[]
    dd=[]
    for j in range(len(mobData[cou].index)):
        dd.append(mobData[cou].index[j])
        vv.append(mobData[cou].values[j][0])
    vv0=np.array(vv)
    vv=(vv-np.min(vv0))/(np.max(vv0)-np.min(vv0))*4.0
    # print(dd,vv)
    return dd,vv


#extractMobility()

def tabrow(data,st1,value,st2):
      return html.Tr([
          html.Td(data,style=st1),
          html.Td(value,style=st2) ],style={'height':'5px','background-color':'red'})

def generaResults0(mdp,mdf,tnp,tnf,micu,lockPerc):
    tabHeaderLab={'width': '200px','background-color':'white','color': 'navy'}
    tabHeaderVal={'width': '50px','background-color':'white','color': 'navy'}
    cellStyle={'width': '300px','font-size':'12px', 'background-color':'white', 'vertical-align':'Top'}
    explStyle={'font-size':'11px','font-Italic':'True', 'font-color':'navy'}
    resultStyle={'font-size':'14px','font-bold':'True', 'fhont-color':'navy'}
    tdLabStyle={'vertical-align':'Top','background-color':'white','height':'5px'}
    tdResStyle={'vertical-align':'Top','background-color':'yellow','height':'5px'}
    res = html.Table([
                tabrow('Data',tabHeaderLab,'Value',tabHeaderVal),
                tabrow('Max daily positive',tdLabStyle,mdp,tdResStyle),
                tabrow('Total New Positive',tdLabStyle,tnp,tdResStyle),
                tabrow('Max daily fatalities',tdLabStyle,mdf,tdResStyle),
                tabrow('Total New Fatalities',tdLabStyle,tnf,tdResStyle),
                tabrow('Max ICUs',tdLabStyle,micu,tdResStyle),
                tabrow('Lock Period (%)',tdLabStyle,lockPerc,tdResStyle),
            ])
    return res



def generaData(dictList, lab1, lab2):
    listlab=[]
    listvals=[]
    for c in dictList:
        listlab.append(c)
        listvals.append(dictList[c])
    data={lab1: listlab, lab2: listvals}
    print(data)
    df = pd.DataFrame (data, columns = [lab1,lab2])
    print (df.to_dict('records'))
    data=df.to_dict('records')
    print (data)
    return data,df

def createTable(dictList, lab1, lab2,idTable):
    dataTab,df=generaData(dictList,lab1,lab2)

    tab= dash_table.DataTable(id=idTable,
        data=dataTab,
        columns=[{'id': c, 'name': c} for c in df.columns],

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'right','font-weight':'bold','font-style':'italic'

            } for c in [lab2]
        ],

        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )

    dtab=html.Div(tab,style={'width':'200px'})

    return dtab

def merge_dicts(*dict_args):
    """
    Given any number of dictionaries, shallow copy and merge into a new dict,
    precedence goes to key-value pairs in latter dictionaries.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def CreateOutput(dataInput, dataOutput, timelines):
    testo='JRC COVID webapp,,'
    testo +='\n'+'================================,,'
    testo +='\n'+'Input quantities,,'
    for rec in dataInput:
        testo +='\n,'+rec['Data']+','+str(rec['Value']).replace(',','').replace(',','')
    testo +='\n'+'-------------------------------,,'
    testo +='\n'+'Output quantities,,'
    for rec in dataOutput:
        testo +='\n,'+rec['Data']+','+str(rec['Value']).replace(',','').replace(',','')
    
    testo0=testo
    #print (timelines)
    dates,CumPos,NewPos,CumFat,NewFata,ICU,Rt,lock=timelines
    print(len(dates),len(CumPos),len(lock))
    testo +='\n\nDate,CumPos,NewPos,CumFat,NewFata,ICU,Rt,lock'
    
    j0=0
    for y in range(2021,2023):
        for mo in range(1,13):
            for dd in [1,15]:
                da=datetime.datetime(y,mo,dd)
                for j in range(j0,len(dates)):
                    if dates[j]>da:
                       testo +='\n'+','.join([format(da),format(int(CumPos[j])),format(int(NewPos[j])),format(int(CumFat[j])),format(int(NewFata[j])),format(int(ICU[j])),format(round(Rt[j],2)),format(lock[j])])
                       print(','.join([format(da),format(int(CumPos[j])),format(int(NewPos[j])),format(int(CumFat[j])),format(int(NewFata[j])),format(int(ICU[j])),format(round(Rt[j],2)),format(lock[j])]))
                       break

    #print(testo)
    return testo
