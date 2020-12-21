# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import urllib
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
#import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from io import StringIO
from dash.dependencies import Input, Output, State
#from dash_extensions.snippets import send_data_frame
#from dash_extensions import Download
from datetime import timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import date
from utility import getMobilityData,getMobilityDataGoogle, generaData,createTable,merge_dicts,CreateOutput
from epiModel import getFore,getObs,getRKI,getPopICU
import base64
import sys,os,getopt
from CONF import couList,iso2,dire0
#cou0='Belgium'
cou0='Belgium'
pop,maxICU,dummy=getPopICU(cou0)
#print (cou0,maxICU)

outputCSV=''

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


def moving_average(x0, w):
    w2=int(w/2)
    x=np.array(x0)
    vv=np.convolve(x, np.ones(w), 'valid') / w
    vv=vv.tolist()
    vv=[0]*int(w/2)+vv+[vv[-1]]*w2
    #  qui posso proseguire con la derivata a -int(w/2)
    der=(vv[-w2]-vv[-w2-1])
    for j in range(-w2,-1):
        vv[j]=vv[-w2]+der*(j-w2)
    return vv

def interpData(values,vmin=-1e10,vmax=1e10,vmin1=-1e10,vmax1=1e10):
	d0=np.min(pd.array(values.index))
	x0=pd.array(values.index)
	dd=[];vv=[]
	for k in range(len(x0)):
#		print(x0[k],values[k])
		dd.append((x0[k]-d0).days)
		vv.append(values[k])
	x=np.linspace(0,np.max(dd),1+np.max(dd))
	y=np.interp(x,dd,vv)
	dnew=[];ynew=[0]
	#print('===============================')
	for k in range(len(x)):
		dnew.append(d0+timedelta(days=x[k]))
		if k>0:
			dv=y[k]-y[k-1]
			if dv<0: dv=0
			ynew.append(dv)
#		print(dnew[k],y[k],ynew[k])

	return dnew, y,ynew
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = dash_app.server

url = 'https://github.com/ec-jrc/COVID-19/raw/master/data-by-country/jrc-covid-19-all-days-by-country.csv'
cases = pd.read_csv(url, usecols=['Date', 'CountryName', 'CumulativePositive','CumulativeDeceased','IntensiveCare'], parse_dates=['Date'], index_col=['CountryName','Date'])
#cf = pd.read_csv(url, usecols=['Date', 'CountryName', 'CumulativeDeceased'], parse_dates=['Date'], index_col=['CountryName','Date'])



optList=[]
for cou in couList:
    elem={'label':cou,'value':cou}
    optList.append(elem)

tip = { 'always_visible': False , 'placement': 'bottom'}

cellStyle={'width': '300px','font-size':'12px', 'background-color':'white', 'vertical-align':'Top'}
explStyle={'font-size':'11px','font-style':'italic', 'font-color':'navy'}
tdStyle={'vertical-align':'Top','background-color':'white'}
desc=html.Div(['The epidemiological situation presentation below is based on a SIRV (Susceptible, Infected, Recovered, Vaccinated) model initialized with values calibrated with the countries epidemiological data of the last 2 weeks.',
        html.Br(),
        'The model is intended to provide a quick overvire of the effect of the control and vaccination strategies in the various countries. It is not intended to represent the real situation and should not be used to provide estimates of future trends.',
        html.Hr()])


rowLoading=dcc.Loading(id="loading-2",children=[html.Div([html.Div(id="loading-output-2",style={'background-color':'Gainsboro','font-style':'italic', 'font-size':'10px'})])],type="default",)

rowcontrols = html.Table([
      html.Tr([
        html.Td([dcc.Checklist(id='ckControl',options=[{'label': 'Control Strategy', 'value': 'C'}],),
                 html.Div('By activating this checkbox the control strategy is applied with the parameters defined on the right. '+
                          'Please note that ICU max capacity is related to 2019 data but you can change it by varying the value in the box below.',style=explStyle),
                 '# ICU available:',dcc.Input(id='maxICU',type='text',value=maxICU)
                 ],style=cellStyle),
        html.Td([html.Label('Max ICU lock (%):'),
                        dcc.Slider(id='lockICU',disabled=True, min=0,max=100,step=5,value=75,tooltip = tip ,marks={i: '{}%'.format(i) for i in range(0,101,20)}),
                  html.Div('It indicates the percentage of ICU occupancy at which the implementation of NPI policies is started. ',style=explStyle)      
                  ],style=cellStyle),
         html.Td([html.Label('Min ICU release (%):'),
                        dcc.Slider(id='unlockICU',disabled=True, min=0,max=100,step=5,tooltip = tip ,value=25,marks={i: '{}%'.format(i) for i in range(0,101,20)}),
                        html.Div('It indicates the percentage of ICU occupancy at which the NPI policies are lifted.',style=explStyle)
                        ],style=cellStyle),
         html.Td([html.Label('Waiting Time between lock/unclok (days)'),
                        dcc.Slider(id='waitTime',disabled=True, min=0,max=60,step=1,value=30,tooltip = tip ,marks={i: '{}'.format(i) for i in range(0,61,10)}), 
                        html.Div('It indicates the number of days that will pass after a policy implementation or after a release of policy',style=explStyle)                        
                        ],style=cellStyle),
         html.Td([html.Label('Target Rt'),
                        dcc.Slider(id='RtTarget',disabled=True, min=0,max=3.5,step=0.05,value=0.95,tooltip = tip ,marks={r: f'{r:.1f}' for r in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5,3.0, 3.5]}), 
                        html.Div('It represents the Rt that is aimed during the implementation of NPI measures. It may be obtained with cocktail of different NPI measures',style=explStyle)                        
                        ],style=cellStyle),
         html.Td([html.Label('Release Rt'),
                        dcc.Slider(id='RtRelease',disabled=True, min=0,max=3.5,step=0.05,value=1.5,tooltip = tip ,marks={r: f'{r:.1f}' for r in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5,3.0, 3.5]}), 
                        html.Div('It is the Rt when the NPI measures are lifted. It cannot overpass the initial R0 value of 3.5',style=explStyle)                        
                        ],style=cellStyle),
         #html.Td('Summary table>'),
         #html.Td( summary,rowSpan=2)

      ]),
     html.Tr([
                html.Td([dcc.Checklist(id='ckVaccination',options=[{'label': 'Vaccination', 'value': 'V'}],),
                         html.Div('By activating this checkbox, the Vaccination strategy is implemented with the parameters defined on the right.'+
                                  ' If this is not activated the parameters on the right cannot be changed and are ignored',style=explStyle)
                         ],style=tdStyle),
                html.Td(['Max Population Vaccinated (%):',
                          dcc.Slider(id='vaccMaxFraction',disabled=True, min=0,max=100,step=5,value=75,tooltip = tip ,marks={i: '{}%'.format(i) for i in range(0,101,20)}),
                         html.Div('It indicates the percentage of population of the overall country population that will receive the vaccine',style=explStyle)
                        ],style=tdStyle),
                 html.Td(['Vaccination efficiency (%)',
                          dcc.Slider(id='vaccEff',disabled=True, min=0,max=100,step=5,value=95,tooltip = tip ,marks={i: '{}%'.format(i) for i in range(0,101,20)}),
                          html.Div('It indicates the efficiency of the vaccination in percentage. Only a fraction of population will be successful.',style=explStyle)
                         ],style=tdStyle),
                html.Td(['Overall Vaccination Period (months)',
                         dcc.Slider(id='VaccinationMonths',disabled=True, min=0,max=48,step=3,tooltip = tip ,value=12,marks={i: '{}m'.format(i) for i in range(0,49,12)}),
                         html.Div('It indicates the overall vaccination period. The vaccination is considered at a constant rate in the population until the maximum number of population is reached',style=explStyle)
                        ],style=tdStyle),
                         
                html.Td(['Start day of vaccination',html.Br(),
                         dcc.DatePickerSingle(id='vaccStartDate',disabled=True, min_date_allowed=date(2020, 12, 10),max_date_allowed=date(2022, 12, 31),date=date(2021,1,10)),
                         html.Div('It indicates the starting day of the vaccination ',style=explStyle)
                         ],style=tdStyle),

                html.Td(['Fraction of immunized that don’t transmit (%)',
                         dcc.Slider(id='vaccFractImm',disabled=True, min=0,max=100,step=5,value=50,tooltip = tip ,marks={i: '{}%'.format(i) for i in range(0,101,20)}),
                         html.Div('It is unknown whether the vaccine is effective to limit transmission. The parameter “Fraction of immunized that don’t transmit” allows to make assumptions. We further assume a homogeneous population',style=explStyle)                
                         ],style=tdStyle)

             ]) 

   ])


#image_filename = '/home/croma/covid/header.png' # replace with your own image
image_filename = dire0+'header.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

#dash_app.layout = html.Div(
testata=html.A([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),],href='https://covid-statistics.jrc.ec.europa.eu/')
#        html.H1('SIRV Model')
#        desc,
#        html.Label('Select the country to update the plots'),
#        dcc.Dropdown(id='CouSel',
#        options=optList,value='Belgium')
#        ]
grafici=html.Div([
    dcc.Graph(id='Cum'),
    dcc.Graph(id='Fat'),
    dcc.Graph(id='Icus'),
    
    dcc.Graph(id='Rt_Mob')
     ],style={'columnCount': 2})

tableInputs =createTable({'Country':cou},'Data','Value','TB_INPUT')
tableSummary=createTable({'Country':cou},'Data','Value','TB_SUMMARY')
#downloadButton=html.Div([html.Button("Download", id="btn"), Download(id="download"),dcc.Textarea(id='textCSV',style={'visivbility_state':'off'})])
downloadLink=html.Div([html.A('Download Results',id='download-link',download="webAppJRC_data.csv",href="",target="_blank"),dcc.Textarea(id='textCSV',style={'display': 'none'})])
countrySelect= html.Div([html.Label('Select the country to update the plots'),
        dcc.Dropdown(id='CouSel',
        options=optList,value='Belgium')])

app.layout = html.Div(
    [ testata,html.H1('SIRV Model'), desc,rowLoading,

         html.Table(
             html.Tr([
                 
                 html.Td([html.H4('Input Data'),tableInputs,html.H4('Summary Output'),tableSummary, downloadLink],style={'width':'10%','vertical-align':'Top'}),
                 html.Td([countrySelect,rowcontrols,grafici],style={'width':'90%'}),
                 

                 
                 ]),style={'width':'100%'}
             ),
     
  ], style={'columnCount': 1})



def createPlotRt0(cou,cap1,cap2,titlePlot,timefore,rtfore=[],fore=False):
    cp1=cases['CumulativePositive'].xs(cou);
    dd,CumCases,newCases=interpData(cp1)
    rtcases=getRKI(CumCases,7)

    cp1=cases['CumulativeDeceased'].xs(cou);
    dd,CumFata,newFata=interpData(cp1)
    rtfata=getRKI(CumFata,7)

    fig=make_subplots() #specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(go.Scatter(x=dd, y=rtcases, name=cap1, line=dict(width=3)))
    fig.add_trace(go.Scatter(x=dd, y=rtfata, name=cap2, line=dict(width=3)))

    if fore:
        fig.add_trace(go.Scatter(x=timefore, y=rtfore, name=cap1+' forecast',line=dict(width=2,color='navy',dash='dash')))

    fig.update_layout(
        legend=dict(x=0.,y=-.1,orientation='h', traceorder="normal",font=dict(family="sans-serif",size=12,color="black"),))

    fig.update_layout(title={'text': titlePlot,'xanchor': 'center','yanchor': 'top'},title_x=0.5)
    fig.update_yaxes(title_text="Reporoduction Number [-]", secondary_y=False)
    return fig

def createPlotRt(cou,cap1,cap2,titlePlot,timefore,rtfore=[],fore=False,mobi=False):
    dd,CumCases,newCases,newCasesSmooth,rtcases=getObs(cases,"CumulativePositive",cou)
    dd,CumFata,newFata,newFataSmooth,rtfata=getObs(cases,"CumulativeDeceased",cou)
    ddUno0=[dd[0],dd[-1]]
    ddUno=[dd[0],timefore[-1]]
    rtUno=[1,1]
    #if mobi: dmob,vmob=getMobilityData(cou)
    if mobi: dmob,vmob=getMobilityDataGoogle(cou)

    fig=make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(go.Scatter(x=dd, y=rtcases, name=cap1, line=dict(width=3)))

    if not mobi:
        fig.add_trace(go.Scatter(x=ddUno, y=rtUno, name='1', line=dict(width=1, dash='dash')))
        fig.add_trace(go.Scatter(x=dd, y=rtfata, name=cap2, line=dict(width=3)))
    if mobi:
        if len(dmob)>0:
            fig.add_trace(go.Scatter(x=ddUno0, y=rtUno, name='1', line=dict(width=1, dash='dash')))
            fig.add_trace(go.Scatter(x=dmob, y=vmob, name='Mobility Indicator', line=dict(width=2,color='red',dash='solid')),secondary_y=True)

    if fore:
        fig.add_trace(go.Scatter(x=timefore, y=rtfore, name=cap1+' forecast',line=dict(width=1,color='navy',dash='dash')))

    fig.update_layout(
        legend=dict(x=0.,y=-.1,orientation='h', traceorder="normal",font=dict(family="sans-serif",size=12,color="black"),))

    fig.update_layout(title={'text': titlePlot,'xanchor': 'center','yanchor': 'top'},title_x=0.5)
    fig.update_yaxes(title_text="Reproduction Number [-]", secondary_y=False, range=[0,4])
    fig.update_yaxes(title_text="Mobility Indicator [-]", secondary_y=True, range=[0,4])
    #if mobi:
    #    fig.update_xaxes(range=[dd[0],dd[-1]])
    return fig
def createPlot(params, column, cap1,cap2,titlePlot,timefore=[],NPfore=[], Fore=False):
    cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm, RtTarget,RtRelease,maxICU    =params

    cp1=cases[column].xs(cou);
    dd,CumCases,newCases=interpData(cp1)
    newCasesSmooth=moving_average(newCases,7)

    fig=make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(go.Scatter(x=dd, y=CumCases, name=cap1, line=dict(width=3)),secondary_y=True)
    fig.add_trace(go.Bar(x=dd, y=newCases, name=cap2),secondary_y=False)
    fig.add_trace(go.Scatter(x=dd, y=newCasesSmooth, name=cap2+' smooth',line=dict(width=3,color='red')),secondary_y=False)
    if Fore:
        fig.add_trace(go.Scatter(x=timefore, y=NPfore, name=cap2+' forecast',line=dict(width=2,color='navy',dash='dash')),secondary_y=False)

    fig.update_layout(
        legend=dict(x=0.,y=-.1,orientation='h', traceorder="normal",font=dict(family="sans-serif",size=12,color="black"),))
    #    title={'text': titlePlot,'side': 'center','yanchor': 'top'}
    #    ))
#        yaxis=dict(title='Cumulative Quantity [-]'),
#        yaxis2=dict(title='Daily Quantity [1/day]'),

    fig.update_layout(title={'text': titlePlot,'xanchor': 'center','yanchor': 'top'},title_x=0.5,
                      yaxis_title=cap1

                      )
    fig.update_yaxes(title_text="Cumulative Quantity [-]", secondary_y=True)
    fig.update_yaxes(title_text="Daily Quantity [1/day]", secondary_y=False)
    return fig

def createPlotICU(params, column, cap1,titlePlot,timefore=[],NPfore=[], Fore=False):
    cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm, RtTarget,RtRelease,maxICU    =params
    cp1=cases[column].xs(cou);
    dd,CumCases,newCases=interpData(cp1)
    newCasesSmooth=moving_average(newCases,7)

    fig=make_subplots(specs=[[{"secondary_y": False}]])
    # Add traces
    fig.add_trace(go.Scatter(x=dd, y=CumCases, name=cap1, line=dict(width=3)),secondary_y=False)
    ddUno0=[dd[0],dd[-1]]
    ddUno=[dd[0],timefore[-1]]
    ddUno1=[timefore[0],timefore[-1]]

    icumaxCurve=[maxICU,maxICU]
    fig.add_trace(go.Scatter(x=ddUno, y=icumaxCurve, name='Max # ICU', line=dict(color='red', width=1,dash='dash')),secondary_y=False)
    if ckControl:
        icumaxCurve=[maxICU*lockICU/100,maxICU*lockICU/100]
        fig.add_trace(go.Scatter(x=ddUno1, y=icumaxCurve, name='Max # ICU', line=dict(color='orange', width=1,dash='dash')),secondary_y=False)
        icumaxCurve=[maxICU*unlockICU/100,maxICU*unlockICU/100]
        fig.add_trace(go.Scatter(x=ddUno1, y=icumaxCurve, name='Max # ICU', line=dict(color='green', width=1,dash='dash')),secondary_y=False)

    if Fore:
        ddUno=[dd[0],timefore[-1]]
        vmin=np.array(NPfore)*0.05
        fig.add_trace(go.Scatter(x=timefore, y=vmin, name=cap1+' forecast min (0.05)',line=dict(width=2)),secondary_y=False)
        vmin=np.array(NPfore)*0.1
        fig.add_trace(go.Scatter(x=timefore, y=vmin, name=cap1+' forecast avg (0.1)',line=dict(width=2)),secondary_y=False)
        vmin=np.array(NPfore)*0.2
        fig.add_trace(go.Scatter(x=timefore, y=vmin, name=cap1+' forecast max (0.2)',line=dict(width=2)),secondary_y=False)

    fig.update_layout(
        legend=dict(x=0.,y=-.1,orientation='h', traceorder="normal",font=dict(family="sans-serif",size=12,color="black"),))
    #    title={'text': titlePlot,'side': 'center','yanchor': 'top'}
    #    ))
#        yaxis=dict(title='Cumulative Quantity [-]'),
#        yaxis2=dict(title='Daily Quantity [1/day]'),

    fig.update_layout(title={'text': titlePlot,'xanchor': 'center','yanchor': 'top'},title_x=0.5,
                      yaxis_title=cap1              )
    
    fig.update_yaxes(title_text="Daily Occupancy [-]", secondary_y=False)
    return fig
@app.callback(Output('download-link', 'href'),Input('textCSV','value'))
def update_download_link(csv_string):
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(Output('maxICU','value'),Input('CouSel','value'),)
#@app.callback(Output('intermediate-value', 'children'), [Input('dropdown', 'value')])
def updatemaxICU(cou):
    pop,maxICU,dummy=getPopICU(cou)
    return maxICU


#@dash_app.callback(
@app.callback(
    Output("loading-output-2", "children"),
    Output('Cum', 'figure'),
    Output('Fat', 'figure'),
    Output('Icus', 'figure'),
    Output('Rt_Mob', 'figure'),

    Output('lockICU','disabled'),
    Output('unlockICU','disabled'),
    Output('waitTime','disabled'),
    Output('RtTarget','disabled'),
    Output('RtRelease','disabled'),
    Output('vaccMaxFraction','disabled'),
    Output('vaccEff','disabled'),
    Output('VaccinationMonths','disabled'),
    Output('vaccStartDate','disabled'),
    Output('vaccFractImm','disabled'),
    Output('TB_INPUT','data'),
    Output('TB_SUMMARY','data'),
    Output('textCSV','value'),

    Input('CouSel', 'value'),
    Input('lockICU', 'value'),
    Input('unlockICU', 'value'),
    Input('waitTime', 'value'),
    Input('ckControl','value'),
    Input('ckVaccination','value'),
    Input('vaccMaxFraction','value'),
    Input('vaccEff','value'),
    Input('VaccinationMonths','value'),
    Input('vaccStartDate','date'),
    Input('vaccFractImm','value'),
    Input('RtTarget','value'),
    Input('RtRelease','value'),
    Input('maxICU','value'),
    )

def update_graph(cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm, RtTarget,RtRelease,maxICU):
    #print(cou)
   # if cou==None:
   #     cou='Belgium'
   #     cou0=''
   # print('cou,cou0 ',cou,cou0)
   # if cou !=cou0:
   #     cou0=cou
   #     pop,maxICU,icupop,dummy=getPopICU(cou)
   # 
    #print(cou,ckControl,maxICU)


    params=cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm, RtTarget,RtRelease,int(maxICU)
    #print (VaccinationMonhts)

    print(params)
    
    dd,CumCases,newCases,newCasesSmooth,rtcases=getObs(cases,"CumulativePositive",cou)
    dd,CumFata,newFata,newFataSmooth,rtfata=getObs(cases,"CumulativeDeceased",cou)
    if newCasesSmooth[-1] != 0.0:
        cfr=newFataSmooth[-1]/newCasesSmooth[-1]
        #print(newFataSmooth[-1],newCasesSmooth[-1],cfr)
    else:
        cfr=0.015
    print('cfr=',cfr)

    timefore,NPfore,rtfore,fatafore,cumpos,cumfata,icus,lock=getFore(params,12*30,cfr)
    #print(np.argmax(np.array(NPfore), axis=0),'maxICU=',maxICU)
    
    pop,dummy,dummy=getPopICU(cou)
    dlist={'Country':cou,'Population ':f'{int(pop):,}','# ICUs avail.':maxICU}
    if ckControl:
        dlist=merge_dicts(dlist,{'Control': 'Active',
                                'Max ICUs': maxICU,
                               'ICU Lock %': lockICU,
                               'ICU Unlock %': unlockICU,
                               'wait time (d)': waitTime,
                               'Target Rt': RtTarget,
                               'Release Rt': RtRelease})
    else:
        dlist=merge_dicts(dlist,{'Control': str(ckControl)})
    if ckVaccination:
        dlist=merge_dicts(dlist,{'Vaccination': 'Active',
                               'Max Pop %': vaccMaxFraction,
                               'Effectiveness %':vaccEff,
                               'Vaccination Months': VaccinationMonhts,
                               'Start Date': vaxxStartDate,
                               'Fraction Immune': vaccFractImm})
    else:
        dlist=merge_dicts(dlist,{'Vaccination': str(ckVaccination)})
    dataInput,df=generaData(dlist,'Data','Value')
    #print('maxICU=',maxICU)
    #print(np.array(icus).max()/int(maxICU))
    if ckControl:
        lockLabel= int(np.array(lock).sum()/len(lock)*100)
    else:
        lockLabel='n.a.'
    dataSummary,df=generaData({
                               'Max New Positive': f'{np.array(NPfore).max():,}',
                               'Date of Max': timefore[np.argmax(np.array(NPfore), axis=0)].strftime("%d %b %Y"),
                               'Posit. increase': f'{int(cumpos[-1]-cumpos[0]):,}',
                               'Max ICU occ.': f'{int(np.array(icus).max()):,}',
                               'ICU occ%':int(np.array(icus).max()/int(maxICU)*100),
                               'Lockdown period %': lockLabel,
                               'Max New Deaths': f'{int(np.array(fatafore).max()):,}',
                               'Deaths increase':f'{int(cumfata[-1]-cumfata[0]):,}'
                               },'Data','Value')


    #timelines=Dates,CumPos,NewPos,CumFat,NewFata,ICU,Rt
    timelines=timefore,cumpos,NPfore,cumfata,fatafore,icus,rtfore,lock
    outputCSV=CreateOutput(dataInput, dataSummary,timelines)

    fig1=createPlot(params,"CumulativePositive","Cumulative Positive Cases", "Daily Cases" , '<b>'+cou+"</b>: Positive Cases",timefore,NPfore,True)
    fig2=createPlot(params,"CumulativeDeceased","Cumulative Fatalities", "Daily Fatalities", '<b>'+cou+"</b>: Fatalities",timefore,fatafore,True)
    fig3=createPlotICU(params,"IntensiveCare","Intensive Care",'<b>'+cou+"</b>: Intensive Care Occupancy",timefore,NPfore,True)
    #fig4=createPlotRt(cou,"Rt cases","Rt fatalities"                                       ,'<b>'+cou+"</b>: Reproduction Number",timefore,rtfore,True,False)
    fig5=createPlotRt(cou,"Rt cases","Rt fatalities"                                       ,'<b>'+cou+"</b>: Reproduction Number and Google Mobility indicator",timefore,rtfore,True,True)
    return 'System x ready',fig1,fig2,fig3,fig5,not ckControl,not ckControl,not ckControl,not ckControl,not ckControl, not ckVaccination, not ckVaccination, not ckVaccination, not ckVaccination, not ckVaccination, dataInput,dataSummary,outputCSV


if __name__ == '__main__':
    if len(sys.argv[1:])>0:
        dmob,vmob=getMobilityDataGoogle('Italy')
        params=('Belgium', 75, 25, 30, 'C', 'V', 80, 95, 12, '2021-01-10', 0.5, 0.95, 1.5)
        params=('Italy', 75, 25, 30, None, 'V', 75, 95, 12, '2021-01-10', 0, 0.95, 1.5, 4750)
        cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm, RtTarget,RtRelease,maxICU    =params
        dd,CumCases,newCases,newCasesSmooth,rtcases=getObs(cases,"CumulativePositive",cou)
        dd,CumFata,newFata,newFataSmooth,rtfata=getObs(cases,"CumulativeDeceased",cou)
        if newCasesSmooth[-1] != 0.0:
            cfr=newFataSmooth[-1]/newCasesSmooth[-1]
            #print(newFataSmooth[-1],newCasesSmooth[-1],cfr)
        else:
            cfr=0.015
        #print('cfr=',cfr)
        timefore,NPfore,rtfore,fatafore=getFore(params,12*30,cfr)
    
        fig1=createPlot(params,"CumulativePositive","Cumulative Positive Cases", "Daily Cases" , '<b>'+cou+"</b>: Positive Cases",timefore,NPfore,True)
 
        #fig1.show()
#    cp1=cp['CumulativePositive'].xs(cou)
#    print('A')
#    dnew,y,ynew=interpData(cp1)

    app.run_server(debug=True)
    #dash_app.run_server(debug=True)