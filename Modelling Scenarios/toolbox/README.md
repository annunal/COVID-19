
# Toolbox of modelling COVID-19 tools 


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







