import socket

#couList = "Austria, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden".split(', ')
iso2={'Austria':'AT', 'Belgium':'BE', 'Bulgaria':'BG', 'Croatia':'HR', 'Cyprus':'CY', 'Czech Republic':'CZ', 'Denmark':'DK', 'Estonia':'EE', 
      'Finland':'FI', 'France':'FR', 'Germany':'DE', 'Greece':'GR', 'Hungary':'HU', 'Ireland':'IE', 'Italy':'IT', 'Latvia':'LV', 
      'Lithuania':'LT', 'Luxembourg':'LU', 'Malta':'MT', 'Netherlands':'NL', 'Poland':'PL', 'Portugal':'PT', 'Romania':'RO', 
      'Slovakia':'SK', 'Slovenia':'SI', 'Spain':'ES', 'Sweden':'SE', 
      'Iceland':'IS', 'Montenegro':'ME', 'North_Macedonia':'NM', 'Norway':'NO','Serbia':'RS', 'Turkey':'TR', 'United_Kingdom':'GB','Switzerland':'CH'} #,'Albania','Kosovo','Bosnia_and_Herzegovina'
      
couList=[]
for c in iso2:
    couList.append(c)

urlbase='https://webcritech.jrc.ec.europa.eu/modellingOutput/CVForeData/'

machine=socket.gethostname()
print(machine)
if machine=='HV-Covid_local':
    system='LINUX_LOCAL'
    dire0='/mnt/diske/CV/Modelling_Activity/python/webapp/'
elif machine=='HV-Covid':
    system='LINUX_JRC'
elif machine=='ECMLAA-NB01':
    system='WINDOWS'
    dire0=''
elif 'blue' in machine:
    system='PYTHON-ANYWHERE'
    dire0='/home/croma/covid/'
else:
    print('system not found')
    end
