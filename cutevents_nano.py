#!/usr/bin/env python
#
#Life is short, you need Python!
#Written by Mijian Xu
#
# 2015-1-4
# 2016-4-1
# 2016-4-8
#

from os.path import exists,basename
import datetime
import os
import glob
import sys,getopt


def Usage():
    print('usage: python cutevent.py -Iinpath -Ooutpath -Yyear1/month1/day1/year2/month2/day2 -Sstaname -Plat/lon [-Tprefix]')
    print('-h, --help: print help message.')
    print('-I, --Input directory.')
    print('-O, --Output directory.')
    print('-Y, --Date range as: year1/month1/day1/year2/month2/day2.')
    print('-S, --Station name.')
    print('-P, --Station latitude and longitude as: lat/lon.')
    print('-T, --Add "20" before file name while the files name are same as "06.112.23.02.34.1.sac".')
    print('-E, --catalog path')

trans = 0
opts, args = getopt.getopt(sys.argv[1:], "hI:O:Y:S:P:T:E:")
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
    elif op == "-T":
        trans = 1
        head = value
    elif op == '-E':
        evt_lst_path = value
    elif op == "-h":
        Usage()
        sys.exit(1)

print(evt_lst_path)

lalo_split = latlon.split("/")
slon = lalo_split[1]
slat = lalo_split[0]

y_split = yrange.split("/")
year1 = int(y_split[0])
month1 = int(y_split[1])
day1 = int(y_split[2])
year2 = int(y_split[3])
month2 = int(y_split[4])
day2 = int(y_split[5])

daterange1 = datetime.date(year1,month1,day1)
daterange2 = datetime.date(year2,month2,day2)


#Open event list
listfile=open(evt_lst_path,"r")

#######################################
#>>>>>>>>>>1<<<<<<<<<<<<<
#  Read each event from event list
#######################################
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
      
      for sac in glob.glob(In_path+"/"+staname+'/*%s.*.BHZ.*.SAC' % staname):
            sac=basename(sac)
#            print(sac)
            sac_split=sac.split('.')
            if trans:
                year_sac=int(head+sac_split[5])
            else:
                year_sac=int(sac_split[5])
            julian_sac=int(sac_split[6]) 
            date_sac=datetime.datetime(year_sac, 1, 1) + datetime.timedelta(julian_sac-1)
            mon_sac=int(date_sac.strftime('%m'))
            day_sac=int(date_sac.strftime('%d'))
            hour_sac = int(sac_split[7][0:2])
            min_sac = int(sac_split[7][2:4])
            sec_sac = int(sac_split[7][4:6])
            sactime=datetime.datetime(year_sac,mon_sac,day_sac,hour_sac,min_sac,sec_sac)
            dt=eventtime-sactime
            if datetime.timedelta(0,0)<dt<=datetime.timedelta(0,3600):
                print(sactime,eventtime)
                sactime2=sactime + datetime.timedelta(0,3600)
                sac_1_1=glob.glob(In_path+"/"+staname+"/"+sac)
                sac_2_1=glob.glob(In_path+"/"+staname+"/*.BHN.*"+sac_split[5]+'.'+sac_split[6]+'.'+sac_split[7]+'.SAC')
                sac_3_1=glob.glob(In_path+"/"+staname+"/*.BHE.*"+sac_split[5]+'.'+sac_split[6]+'.'+sac_split[7]+'.SAC')
                sac_1_2=glob.glob(In_path+"/"+staname+"/*.BHZ.*"+sactime2.strftime('%Y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H%M%S')+".SAC")
                sac_2_2=glob.glob(In_path+"/"+staname+"/*.BHN.*"+sactime2.strftime('%Y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H%M%S')+".SAC")
                sac_3_2=glob.glob(In_path+"/"+staname+"/*.BHE.*"+sactime2.strftime('%Y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H%M%S')+".SAC")
                if sac_1_2==[] or sac_2_2==[] or sac_3_2==[] or sac_1_1==[] or sac_2_1==[] or sac_3_1==[]:
                    print(In_path+"/"+staname+"/*.BHN.*"+sac_split[5]+'.'+sac_split[6]+'.'+sac_split[7]+'.*.SAC')
                    print(In_path+"/"+staname+"/*.BHE.*"+sactime2.strftime('%Y')+'.'+sactime2.strftime('%j')+'.'+sactime2.strftime('%H%M%S')+".*.SAC")
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
                sacfile.write('echo on\n')
                sacfile.write('merge GAP INTERP  OVERLAP AVERAGE '+sac_1_1[0]+' '+sac_1_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM BHZ nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y.%j.%H.%M.%S')+'.Z.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('merge GAP INTERP  OVERLAP AVERAGE '+sac_2_1[0]+' '+sac_2_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM BHN nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y.%j.%H.%M.%S')+'.N.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('merge GAP INTERP  OVERLAP AVERAGE '+sac_3_1[0]+' '+sac_3_2[0]+'\n')
                sacfile.write('cutim '+begin_t+' '+end_t+'\n')
                sacfile.write('ch evla '+str(lat)+' evlo '+str(lon)+' KCMPNM BHE nzyear '+str(year)+' nzjday '+str(jjj)+' nzhour '+str(hour)+' nzmin '+str(min)+' nzsec '+str(sec)+' stla '+slat+' stlo '+slon+' kstnm '+staname+' b 0 e 3600 o 0\n')
                sacfile.write('w '+Out_path+'/'+staname+'/'+eventtime.strftime('%Y.%j.%H.%M.%S')+'.E.sac\n')
                sacfile.write('cut off\ndc all\n')
                sacfile.write('q\n')
                sacfile.write('END')
                sacfile.close()

                os.system('bash run_sac.sh')
os.system('rm run_sac.sh')
