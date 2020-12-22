
# COVID-19 Scenario modelling toolbox 


[![GitHub license](https://img.shields.io/badge/License-Creative%20Commons%20Attribution%204.0%20International-blue)](https://github.com/ec-jrc/COVID-19/blob/master/LICENSE)
[![GitHub commit](https://img.shields.io/github/last-commit/ec-jrc/COVID-19)](https://github.com/ec-jrc/COVID-19/commits/master)

## Introduction
The objective of this section is to illustrate the various elements of the scenario modelling that have been provided in the report:  'Scenarios for targeted and local COVID-19 Non Pharmaceutical Intervention Measures' , developed by JRC and provided in this folder. 

## Toobox application
The epidemiological situation presentation below is based on a SIRV (Susceptible, Infected, Recovered, Vaccinated) model initialized with values calibrated with the countries epidemiological data of the last 2 weeks.

The model is intended to provide a quick overvire of the effect of the control and vaccination strategies in the various countries. It is not intended to represent the real situation and should not be used to provide estimates of future trends.

The application can be run here:  http://croma.pythonanywhere.com/


## Model description
The SIRC model is composed of a number of partial differential equations that represent the variation for each compartment.  In particular

  - dS/dt=-r<sub>0</sub>/T<sub>recov</sub> S/N (I+I<sub>v</sub>) + dVdt &mu;
  
  - dS<sub>v</sub>/dt=-r<sub>0</sub>/T<sub>recov</sub> S<sub>v</sub>/N (I+I<sub>v</sub>) + dVdt &mu; (1- &eta;)
  
  - dI/dt=r<sub>0</sub>/T<sub>recov</sub> S/N (I+I<sub>v</sub>) - 1/T<sub>recov</sub> I
  
  - dI<sub>v</sub>/dt=r<sub>0</sub>/T<sub>recov</sub> S<sub>v</sub>/N (I+I<sub>v</sub>) - 1/T<sub>recov</sub> I<sub>v</sub>
  
  - dR/dt=1/T<sub>recov</sub> (I+I<sub>v</sub>) + dV/dt &mu; &eta;
  
  - dF/dt=cfr dI/dt

where:

  - S are the susceptiple people

  - S<sub>v</sub> are the susceptible people that has been vaccinated and that can be infected with mild symptoms

  - I are the infected people

  - I<sub>v</sub> are the infected people, vaccinated, with mild symptoms

  - R are the recovede people

  - F are the fatalities

The various parameters of the interface are used to intialize and to control the implementation of lockdown or the release.

## Application Controls
### Control Strategy
It is possible to activate the <b>Control Strategy</b> by clicking on the dedicated checkbox.  The control is based on the estimated number of ICU occupancy.

Considering the increase of the number of cases the introduction of NPI measures is considered when the estimated percentage of ICU occupied reaches the value of <b>Lock percentage</b>; as a consequence of the imposed NPIs the number of cases, and thus the ICU occupancy, after a while starts to decrease. When the percentage drops below the <b>Unlock percentage</b>, the NPI measures are lifted. Again, when the value overpasses the Lock percentage a new lockdown should start but this is not done if a minimum number of days is not yet passed (<b>Minter</b>). The idea is that during very frequently lockdown and releases, it is not possible to lock again only few days after the unlock has been achieved (minimum interval Minter), for economy and social considerations.

![Control strategy](https://github.com/annunal/COVID-19/blob/master/Modelling%20Scenarios/toolbox/controlCurve.PNG)

By activating this checkbox the control strategy is applied with the parameters defined on the right. Please note that ICU max capacity is related to 2019 data but you can change it by varying the value in the box below.

The following controls are available:

- Max ICU lock (%):It indicates the percentage of ICU occupancy at which the implementation of NPI policies is started.
- Min ICU release (%): It indicates the percentage of ICU occupancy at which the NPI policies are lifted.
- Waiting Time between lock/unclok (days): It indicates the number of days that will pass after a policy implementation or after a release of policy
- Target Rt: It represents the Rt that is aimed during the implementation of NPI measures. It may be obtained with cocktail of different NPI measures
- Release Rt: It is the Rt when the NPI measures are lifted. It cannot overpass the initial R0 value of 3.5

### Vaccination controls
It is possible to activate the <b>vaccination</b> by clicking on the dedicated checkbox.  The following controls can be modified:

By activating this checkbox, the Vaccination strategy is implemented with the parameters defined on the right. If this is not activated the parameters on the right cannot be changed and are ignored:

- Max Population Vaccinated (%): It indicates the percentage of population of the overall country population that will receive the vaccine
- Vaccination efficiency (%): It indicates the efficiency of the vaccination in percentage. Only a fraction of population will be successful.
- Overall Vaccination Period (months): It indicates the overall vaccination period. The vaccination is considered at a constant rate in the population until the maximum number of population is reached
- Start day of vaccination: Press the down arrow key to interact with the calendar and select a date. Press the question mark key to get the keyboard shortcuts for changing dates. It indicates the starting day of the vaccination
- Fraction of immunized that don’t transmit (%): It is unknown whether the vaccine is effective to limit transmission. The parameter “Fraction of immunized that don’t transmit” allows to make assumptions. We further assume a homogeneous population

## Mobility data and Rt
One of the plots in the page is related to the comparison between the reproduction number and the mobility indicator. 

The indicator chosen for the mobility <b>GMI</b>is a combination of the [Google mobility indicators](https://www.google.com/covid19/mobility/) to take into account the various contributions: In particular, Google provides the following parameters:
- retail_and_recreation
- grocery_and_pharmacy
- parks
- transit_stations
- workplaces
- residential
and are combiled as follows

GMI= 0.25 * (retail_and_recreation)+ 0.2* (grocery_and_pharmacy) + 0.1*(parks) + 0.2* (transit_stations)+0.2*(workplaces)-0.05*(residential)


