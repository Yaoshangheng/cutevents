#!/Applications/anaconda/bin/python
#
#Life is short, you need Python!
#Written by Mijian Xu
#
#2015-1-4
#

from os.path import exists,basename
import datetime
import os
import glob
import sys,getopt


#In_path="/Volumes/DATA.Tibet/Ordos" #Input path of serial data
#Out_path="/Volumes/DATA.Tibet/DATA.Ordos"#Output path of event data

def Usage():
    print 'usage: python cutevent.py [options]'
    print '-h, --help: print help message.'
    print '-I, --Input dirctory.'
    print '-O, --Output dirctory.'
    print '-Y, --Date range as: year1/month1/day1/year2/month2/day2.'
    print '-S, --Station name.'
    print '-P, --Station longitude and latitude as: lon/lat.'

opts, args = getopt.getopt(sys.argv[1:], "hI:O:Y:S:P:")
for op,value in opts:
    if op == "-I":
        In_path = value
    elif op == "-O":
        Out_path = value
    elif op == "-Y":
        yrange = value
    elif op == "-S":
        staname = value
    elif op == "-P":
        latlon = value
    elif op == "-h":
        Usage()
        sys.exit(1)

lalo_split=latlon.split("/")
slon=lalo_split[0]
slat=lalo_split[1]

y_split=yrange.split("/")
year1=int(y_split[0])
month1=int(y_split[1])
day1=int(y_split[2])
year2=int(y_split[3])
month2=int(y_split[4])
day2=int(y_split[5])


#Set date range of data record
#year1=2006
#month1=8
#day1=4
#year2=2007
#month2=7
#day2=31

daterange1=datetime.date(year1,month1,day1)
daterange2=datetime.date(year2,month2,day2)

#Open sattion list (3 column:station name, lat, lon)
#stafile=open(In_path+'/stalist.dat',"r+")
#Open event list
listfile=open("EventCMT.dat","r")

#######################################
#>>>>>>>>>>1<<<<<<<<<<<<<
#  Read each event from event list
#######################################
#for sta in stafile:
# sta_split=sta.split()
# staname=sta_split[0]
# slat=sta_split[2]
# slon=sta_split[1]
# refnum=sta_split[3]
if not exists(Out_path+'/'+staname):
    os.makedirs(Out_path+'/'+staname)
 
for event in listfile:
   event_split=event.split()
   if daterange1<=datetime.date(int(event_split[0]),int(event_split[1]),int(event_split[2]))<=daterange2:
      year=int(event_split[0])
      mon=int(event_split[1])
      day=int(event_split[2])
      jjj=int(event_split[3])
      hour=int(event_split[4])
      min=int(event_split[5])
      sec=int(event_split[6])
      lat=float(event_split[7])
      lon=float(event_split[8])
      dep=float(event_split[9])
      mw=float(event_split[10])
      yearstr=str(event_split[0])
      eventtime=datetime.datetime(year,mon,day,hour,min,sec)
      
      for sac in glob.glob(In_path+"/"+staname+"/*1.sac"):
            sac=basename(sac)
            sac_split=sac.split('.')
            year_sac=int('20'+sac_split[0])
            julian_sac=int(sac_split[1])
            date_sac=datetime.datetime(year_sac, 1, 1) + datetime.timedelta(julian_sac-1)
            mon_sac=int(date_sac.strftime('%m'))
            day_sac=int(date_sac.strftime('%d'))
            sactime=datetime.datetime(year_sac,mon_sac,day_sac,int(sac_split[2]),int(sac_split[3]),int(sac_split[4]))
            dt=eventtime-sactime
            if datetime.timedelta(0,0)<dt<=datetime.timedelta(0,3600):
                sactime2=sactime + datetime.timedelta(0,3600)
                sac_1_1=In_path+"/"+staname+"/"+sac
                sac_2_1=glob.glob(In_path+"/"+staname+"/"+sac_split[0]+'.'+sac_split[1]+'.'+sac_split[2]+'.'+sac_split[3]+'.'+sac_split[4]+'.*.2.sac')
                sac_3_1=glob.glob(In_path+"/"+staname+"/"+sac_split[0]+'.'+sac_split[1]+'.'+sac_split[2]+'.'+sac_split[3]+'.'+sac_split[4]+'.*.3.sac')
                sac_1_2=glob.glob(In_path+"/"+staname+"/"+sactime2.strftime('%y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H')+"*.1.sac")
                sac_2_2=glob.glob(In_path+"/"+staname+"/"+sactime2.strftime('%y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H')+"*.2.sac")
                sac_3_2=glob.glob(In_path+"/"+staname+"/"+sactime2.strftime('%y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H')+"*.3.sac")
                if sac_1_2==[] or sac_2_2==[] or sac_3_2==[]:
                    continue
                else:
                    print(sac_3_1[0])
                    print(sac_3_2[0])

##############################
#>>>>>>>>>>>2<<<<<<<<<<<<<<<<
#  cut data 
##############################
                begin_t=dt.seconds
                end_t=begin_t+3600
                begin_t=str(begin_t)
                end_t=str(end_t)

                sacfile=open("run_sac.sh","w")
                sacfile.write('sac <<END\n')
                sacfile.write('merge '+sac_1_1+' '+sac_1_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM 1 nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y')+'.'+eventtime.strftime('%j')+'.'+eventtime.strftime('%H')+'.'+eventtime.strftime('%M')+'.'+eventtime.strftime('%S')+'.1.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('merge '+sac_2_1[0]+' '+sac_2_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM 2 nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y')+'.'+eventtime.strftime('%j')+'.'+eventtime.strftime('%H')+'.'+eventtime.strftime('%M')+'.'+eventtime.strftime('%S')+'.2.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('merge '+sac_3_1[0]+' '+sac_3_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM 3 nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y')+'.'+eventtime.strftime('%j')+'.'+eventtime.strftime('%H')+'.'+eventtime.strftime('%M')+'.'+eventtime.strftime('%S')+'.3.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('q\n')
                sacfile.write('END')
                sacfile.close()

                os.system('bash run_sac.sh')
