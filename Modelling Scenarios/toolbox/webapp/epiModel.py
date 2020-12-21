try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
import datetime
import json
import numpy as np
import pandas as pd
from datetime import timedelta
from CONF import couList,iso2,urlbase


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

def interpData(values,x=[]):
	d0=np.min(pd.array(values.index))
	x0=pd.array(values.index)
	dd=[];vv=[]
	for k in range(len(x0)):
#		print(x0[k],values[k])
		dd.append((x0[k]-d0).days)
		vv.append(values[k])
	if len(x)==0:
		x=np.linspace(0,np.max(dd),1+np.max(dd))

	y=np.interp(x,dd,vv)
	print (len(x),len(y))
	dnew=[];ynew=[0]
	#print('===============================')
	for k in range(len(x)):
		dnew.append(d0+timedelta(days=x[k]))
		if k>0:
			dv=y[k]-y[k-1]
			if dv<0: dv=0
			ynew.append(dv)
#		print(dnew[k],y[k],ynew[k])

	return dnew, y,ynew,x


def getObs(cases,column, cou):
    
    if cou=='EU27':
        dd=[]
        cp10=cases[column].xs('Italy')
        dd0,CumCases0,newCases0,xln=interpData(cp10)

        for c in couList:
            print (cou)
            cp10=cases[column].xs(c);
            if len(dd)==0:
                dd0,CumCases0,newCases0,xln=interpData(cp10,xln)
                newCasesSmooth0=moving_average(newCases0,7)
                dd=dd0
                print('1',c,len(xln),len(CumCases0))
                CumCases=np.array(CumCases0)
                newCases=np.array(newCases0)
                newCasesSmooth=np.array(newCasesSmooth0)
            else:

                dd0,CumCases0,newCases0,xln=interpData(cp10,xln)
                print('2',c,len(xln),len(dd0),len(CumCases))
                newCasesSmooth0=moving_average(newCases0,7)
                CumCases+=np.array(CumCases0)
                newCases+=np.array(newCases0)
                newCasesSmooth+=np.array(newCasesSmooth0)
        rt=getRKI(CumCases,7)
    else:
        cp1=cases[column].xs(cou);
        dd,CumCases,newCases,dummy=interpData(cp1)
        newCasesSmooth=moving_average(newCases,7)
        rt=getRKI(CumCases,7)

    return dd,CumCases,newCases,newCasesSmooth,rt

def getRKI(cumInterp,ndays):
    r0=[0]*2*ndays
    for k in range(2*ndays,len(cumInterp)):
        week1 = cumInterp[k-ndays]-cumInterp[k-2*ndays+1]
        week2 = cumInterp[k]-cumInterp[k-ndays+1]
        if week1 !=0:
            rrki=week2/week1
        else:
            rrki=0.0
        if rrki<0:
            rrki=0.0
        if rrki>4:
                rrki=4
        r0.append(rrki)
    return(r0)

def getPopICU(country, rows=[]):
    if rows==[]:
        urlpopICU=urlbase+'Pop_ICUs.csv'
        response=urlopen(urlpopICU)
        rows=response.read().decode("utf-8").split('\n')

    for row in rows:
        if row.split('\t')[0]==country:
            pop=float(row.split('\t')[1])
            icu=float(row.split('\t')[2])
            if pop==0: pop=1
            return pop,icu,rows
    return 0,0,rows
def calcSIR(params,S,I,R,N,r0,Trecov,cfr,time0,period,StartTimeControl=15):

    cou,lockICUPerc,unlockICUPerc,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonths,vaccStartDate,vaccFractImm, RtTarget,RtRelease,icumax    =params
    print(VaccinationMonths)
    TIME=[]
    II=[]
    RR=[]
    SS=[]
    CUMPOS=[]
    NEWPOS=[]
    LOCK=[]
    REPR=[]
    CUM_14days=[]
    V=0
    II.append(I)
    RR.append(R)
    SS.append(S)
    REPR.append(r0)
    CUMPOS.append(N-S)
    #NEWPOS.append(0)   # it is only to have the same number of data
    CP0=N-S
    LOCK.append(0)
    if ckVaccination==None or ckVaccination==[]:
        VaccinationMonths=0
        vaccEff=0
        vaccMaxFraction=0
        vaccStartDate='2040-01-01'

    vaccStartDate=datetime.datetime.strptime(vaccStartDate,'%Y-%m-%d')
    date0=datetime.datetime.strptime(time0,'%Y/%m/%d')
    vaccStartDateN=(vaccStartDate-date0).days
    try:
        vaccPerDay=1/(VaccinationMonths*30)
    except:
        vaccPerDay=1e8
    #print(cou,reg,r0,Trecov,N)

    dt=0.1
    r00=r0
    R0Lock=r00
    R0UnLock=r00

    #StartTimeControl=1e6  #parameter

    'get ICU max by country'

    iculockMax=icumax*lockICUPerc/100
    iculockMin=icumax*unlockICUPerc/100
    lockMax=1e9
    lockMin=-1

    firstLock=True
    tlock=0
    tunlock=-1e6
    lock=False
    unlocking=False
    unlocked=False
    lockImplementation=20  # time for implemenattion of measures

    icu0=r0/Trecov*S*I/N*0.09
    if icu0<iculockMax:
        lock=True
    #    tlock=-1e6
    else:
        lock=False
    #if r0<0.95:
    #    R0Target=r0
    #else:
    R0Target=RtTarget
    #if r0>1.5:
     #   R0Release=r0
    #else:
    R0Release=RtRelease

    xdata=np.linspace(0,period*int(1/dt),period*int(1/dt))*dt  # 6 months forecast
    first=True
    for i in range(len(xdata)):
        ti=datetime.datetime.strptime(time0,'%Y/%m/%d')+timedelta(days=xdata[i])
        TIME.append(ti)
        if xdata[i]>vaccStartDateN:
            dVdt=vaccPerDay*N*vaccEff/100. * vaccFractImm/100.
            if V>vaccMaxFraction/100.*N:
                dVdt=0
        else:
            dVdt=0
        dSdt=-r0/Trecov*(S+(1-vaccFractImm/100.))*I/N -dVdt
        dIdt=r0/Trecov*S*I/N - 1/Trecov*I
        dRdt=1/Trecov*I

        V +=dVdt*dt
        S +=dSdt*dt
        I +=dIdt*dt
        R +=dRdt*dt
        CP =N-S-V

        II.append(I)
        RR.append(R)
        SS.append(S)
        CUMPOS.append(CP)
        npo=int((CP-CP0)/dt)
        NEWPOS.append(npo)
        CP0=CP
        #print(format(xdata[i])+','+format(S)+','+format(I)+','+format(R)+','+format(CP)+','+format(r0)+','+format(npo))

        #  I     =  CURRENT POSITIVE !!!
        #  -dSdt =  NEW POSITIVE
        #  N-S   =  CUMULATIVE POSITIVE
        if first:
            cumIncidence_14days=(CP-CUMPOS[0])/0.1*14*100000.0/N
            first=False
        else:
            if len(CUMPOS)>15/dt:
                cumIncidence_14days=(CP-CUMPOS[len(CUMPOS)-int(14/dt)])*100000.0/N

        CUM_14days.append(cumIncidence_14days)
        ICUEstimate=npo*0.09
        if xdata[i]>StartTimeControl:
            if (cumIncidence_14days>lockMax or
                (ICUEstimate>iculockMax and xdata[i]-tunlock>waitTime)
                ) and not lock :  # and (I0<lockMax):

                tlock=xdata[i]
                lock=True
                R0Lock=r0
            if (cumIncidence_14days<lockMin or (ICUEstimate<iculockMin and xdata[i]-tlock>waitTime)) and lock :
                tunlock=xdata[i]
                lock=False
                R0UnLock=r0

            def transF(t,tlock,delta,R_0_start,R_0_end):
                if t<tlock:
                    return R_0_start
                elif t>tlock+delta*2:
                    return R_0_end
                else:
                    ff=10/delta
                    return (R_0_start-R_0_end)/(1+np.exp(-ff*(-t+tlock+delta/2)))+R_0_end

            if lock: # and xdata[i]>daysAfterLock+tlock:
                #r0=min(0.7,r00)
                deltaDelay=7
                if r0>R0Target:
                    r0=transF(xdata[i],tlock+deltaDelay,lockImplementation,R0Lock,R0Target)
            else:
                deltaDelay=2   # immediate releasing of people
                #if len(FILTERCOUNTRY)>0:
                r0=transF(xdata[i],tunlock+deltaDelay,lockImplementation,R0UnLock,R0Release)
                #else:
                #    r0=transF(xdata[i],tunlock+deltaDelay,lockImplementation,R0UnLock,r00)


        REPR.append(r0)
        if lock:
            LOCK.append(1)
        NEWFATA=cfr*np.array(NEWPOS)*(1-vaccFractImm/100.)
        #print('NEWFATA=',NEWFATA)
    return TIME,NEWPOS,REPR,NEWFATA

def calcSIRVF(params,S,I,R,N,r0,Trecov,cfr,time0,period,StartTimeControl=15):

    cou,lockICUPerc,unlockICUPerc,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonths,vaccStartDate,vaccFractImm, RtTarget,RtRelease,icumax    =params
    print(VaccinationMonths)
    TIME=[]
    II=[]
    RR=[]
    SS=[]
    #VV=[]
    FF=[]
    CUMPOS=[]
    NEWPOS=[]
    NEWFATA=[]
    LOCK=[]
    REPR=[]
    CUM_14days=[]
    ICUS=[]
    
    II.append(I)
    RR.append(R)
    SS.append(S)

    Sv=0
    Iv=0
    F=0
    V=0
    
    FF.append(F)

    REPR.append(r0)
    CUMPOS.append(N-S)
    #NEWPOS.append(0)   # it is only to have the same number of data
    CP0=N-S
    LOCK.append(0)
    ti=datetime.datetime.strptime(time0,'%Y/%m/%d')+timedelta(days=0)
    TIME.append(ti)
    if ckVaccination==None or ckVaccination==[]:
        VaccinationMonths=0
        vaccEff=0
        vaccMaxFraction=0
        vaccStartDate='2040-01-01'

    vaccStartDate=datetime.datetime.strptime(vaccStartDate,'%Y-%m-%d')
    date0=datetime.datetime.strptime(time0,'%Y/%m/%d')
    vaccStartDateN=(vaccStartDate-date0).days
    eta=vaccFractImm/100.
    try:
        vaccPerDay=1/(VaccinationMonths*30)
    except:
        vaccPerDay=1e8
    #print(cou,reg,r0,Trecov,N)

    dt=0.1
    r00=r0
    R0Lock=r00
    R0UnLock=r00

    #StartTimeControl=1e6  #parameter

    'get ICU max by country'

    iculockMax=icumax*lockICUPerc/100
    iculockMin=icumax*unlockICUPerc/100
    lockMax=1e9
    lockMin=-1

    firstLock=True
    tlock=0
    tunlock=-1e6
    lock=False
    unlocking=False
    unlocked=False
    lockImplementation=20  # time for implemenattion of measures

    icu0=r0/Trecov*S*I/N*0.09
    ICUS.append(icu0)
    if icu0<iculockMax:
        lock=True
    #    tlock=-1e6
    else:
        lock=False
    #if r0<0.95:
    #    R0Target=r0
    #else:
    R0Target=RtTarget
    #if r0>1.5:
     #   R0Release=r0
    #else:
    R0Release=RtRelease

    xdata=np.linspace(0,period*int(1/dt),period*int(1/dt))*dt  # 6 months forecast
    first=True
    for i in range(len(xdata)):
        ti=datetime.datetime.strptime(time0,'%Y/%m/%d')+timedelta(days=xdata[i])
        TIME.append(ti)
        if xdata[i]>vaccStartDateN:
            dVdt=vaccPerDay*N*vaccEff/100. # * vaccFractImm/100.
            if V>vaccMaxFraction/100.*N:
                dVdt=0
        else:
            dVdt=0
        dSdt=-r0/Trecov*(S)*(I+Iv)/N -dVdt               # Susceptible
        dSvdt=-r0/Trecov*(Sv)*(I+Iv)/N + dVdt*(1-eta)    # Susceptible vaccinated
        dIdt=r0/Trecov*S*I/N - 1/Trecov*I                # Infected
        dIvdt=r0/Trecov*Sv*(I+Iv)/N - 1/Trecov*Iv        # Infected vaccinated
        dRdt=1/Trecov*I + 1/Trecov*Iv +dVdt*eta          # Recovered
        dFdt=cfr*r0/Trecov*(S)*(I+Iv)/N                  # Fatalities

        V +=dVdt*dt
        S +=dSdt*dt
        Sv+=dSvdt*dt
        I +=dIdt*dt
        Iv+=dIvdt*dt
        R +=dRdt*dt
        F +=dFdt*dt

        CP =N-S-V

        II.append(I+Iv)
        RR.append(R)
        SS.append(S+Sv)
       # FF.append(F)

        CUMPOS.append(CP)
        npo=int((CP-CP0)/dt)
        NEWPOS.append(npo)
        NEWFATA.append(dFdt)
        FF.append(F)

        CP0=CP
        #print(format(xdata[i])+','+format(S)+','+format(I)+','+format(R)+','+format(CP)+','+format(r0)+','+format(npo))

        #  I     =  CURRENT POSITIVE !!!
        #  -dSdt =  NEW POSITIVE
        #  N-S   =  CUMULATIVE POSITIVE
        if first:
            cumIncidence_14days=(CP-CUMPOS[0])/0.1*14*100000.0/N
            first=False
        else:
            if len(CUMPOS)>15/dt:
                cumIncidence_14days=(CP-CUMPOS[len(CUMPOS)-int(14/dt)])*100000.0/N

        CUM_14days.append(cumIncidence_14days)
        ICUEstimate=npo*0.09
        ICUS.append(ICUEstimate)
        if xdata[i]>StartTimeControl:
            if (cumIncidence_14days>lockMax or
                (ICUEstimate>iculockMax and xdata[i]-tunlock>waitTime)
                ) and not lock :  # and (I0<lockMax):

                tlock=xdata[i]
                lock=True
                R0Lock=r0
            if (cumIncidence_14days<lockMin or (ICUEstimate<iculockMin and xdata[i]-tlock>waitTime)) and lock :
                tunlock=xdata[i]
                lock=False
                R0UnLock=r0

            def transF(t,tlock,delta,R_0_start,R_0_end):
                if t<tlock:
                    return R_0_start
                elif t>tlock+delta*2:
                    return R_0_end
                else:
                    ff=10/delta
                    return (R_0_start-R_0_end)/(1+np.exp(-ff*(-t+tlock+delta/2)))+R_0_end

            if lock: # and xdata[i]>daysAfterLock+tlock:
                #r0=min(0.7,r00)
                deltaDelay=7
                if r0>R0Target:
                    r0=transF(xdata[i],tlock+deltaDelay,lockImplementation,R0Lock,R0Target)
            else:
                deltaDelay=2   # immediate releasing of people
                #if len(FILTERCOUNTRY)>0:
                r0=transF(xdata[i],tunlock+deltaDelay,lockImplementation,R0UnLock,R0Release)
                #else:
                #    r0=transF(xdata[i],tunlock+deltaDelay,lockImplementation,R0UnLock,r00)


        REPR.append(r0)
        if lock:
            LOCK.append(1)
        else:
            LOCK.append(0)
        #print('NEWFATA=',NEWFATA)
    return TIME,NEWPOS,REPR,NEWFATA,CUMPOS,FF,ICUS,LOCK


def getFore(params, period,cfr, DAYFORE=''):
    cou,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm , RtTarget,RtRelease,maxICU   =params
    #1 get the daily parameters
    if DAYFORE=='':
        DAYFORE=datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    urlRegion=urlbase+DAYFORE+'/FITTING_ALLREGIONS/data/FITTING_ALLREGIONS_SIR_(-15%20-1).json'
    urlCountry=urlbase+DAYFORE+'/FITTING_ALLCOUNTRIES/data/FITTING_ALLCOUNTRIES_SIR_(-15%20-1).json'
    #  in realta'prima di una certa data e' -30
    try:
        response=urlopen(urlCountry)
    except:
        DAYFORE='2020-12-12'
        urlCountry=urlbase+DAYFORE+'/FITTING_ALLCOUNTRIES/data/FITTING_ALLCOUNTRIES_SIR_(-15%20-1).json'
        response=urlopen(urlCountry)
    dataJson = response.read().decode("utf-8")
    data=json.loads(dataJson)

    urlpopICU=urlbase+'Pop_ICUs.csv'
    response=urlopen(urlpopICU)
    popicu=response.read().decode("utf-8").split('\n')
    print('cou=',cou)
    
    if cou=='EU27':
        TIME=[]
        for c in ecList:
            print (c)
            if c=='EU27':
                continue
            TIME0,NEWPOS0,Rt0,NEWFATA,CUMPOS,FF,ICUS,LOCK=calcCountry(params,data,c,12*30,cfr)
            if len(TIME)==0:
                TIME=TIME0
                NEWPOS=np.array(NEWPOS0)
                Rt=np.array(Rt0)
            else:
                NEWPOS+=np.array(NEWPOS0)
                Rt+=np.array(Rt0)
            Rt/=27.0
    else:
        TIME,NEWPOS,Rt,NEWFATA,CUMPOS,FF,ICUS,LOCK=calcCountry(params,data,cou,12*30,cfr)

    return TIME,NEWPOS,Rt,NEWFATA,CUMPOS,FF,ICUS,LOCK

def calcCountry(params,data,cou,period,cfr):
    c,lockICU,unlockICU,waitTime,ckControl,ckVaccination,vaccMaxFraction,vaccEff,VaccinationMonhts,vaxxStartDate,vaccFractImm , RtTarget,RtRelease,maxICU   =params
    pop,icu,dummy=getPopICU(cou)

    r0=     data[cou]['r0']
    Trecov= data[cou]['Trecov']
    I=     data[cou]['_ivp']['I']
    R=     data[cou]['_ivp']['R']
    N=      data[cou]['population']
    
    
    S=N-I-R
    print(r0,Trecov,S,I,R,N)
    time0=data[cou]['time'][0]
    if ckControl==None or ckControl==[]:
        StartControl=1e6
    else:
        StartControl=15
    #TIME,NEWPOS,Rt,NEWFATA=calcSIR(params,S,I,R,N,r0,Trecov,cfr,time0,period,StartControl)
    TIME,NEWPOS,Rt,NEWFATA,CUMPOS,FF,ICUS,LOCK=calcSIRVF(params,S,I,R,N,r0,Trecov,cfr,time0,period,StartControl)
    return TIME,NEWPOS,Rt,NEWFATA,CUMPOS,FF,ICUS,LOCK
