#!/usr/bin/env python3
# mseedTriggers.py
#
# Runs STA/LTA triggers for 24-hour mseed files 
#
# R.C. Stewart, 2023-10-27
#
#
import os
import sys
import stat
import glob
import argparse
import re
import obspy
from datetime import datetime, date, timedelta
from dateutil import parser as dparser
from dateutil.rrule import rrule, DAILY
from obspy.core import UTCDateTime, Stream
from obspy.signal.trigger import classic_sta_lta
from obspy.signal.trigger import plot_trigger
from obspy.signal.trigger import trigger_onset
from pprint import pprint
import numpy as np

secInDay = 60*60*24
filenameSeparator = "."
filenameSeparator2 = "-"
dirnameSeparator = "/"
today = datetime.utcnow().date()

# Arguments
parser = argparse.ArgumentParser(description='Run STA/LTA trigger on daily mseed files')
parser.add_argument('--test', action='store_true', default=False,
                        help="If set, read all mseed files in current directory.")
parser.add_argument("--date", default="yesterday", help="Start date")
parser.add_argument("--mseed_dir", default="/mnt/mvohvs3/MVOSeisD6/mseed/MV", help="Miniseed base directory")
args = parser.parse_args()

# Try and sort out dates
if args.date == 'yesterday':
    msDate = UTCDateTime(today.year, today.month, today.day) - secInDay
elif args.date == 'today':
    msDate = UTCDateTime(today.year, today.month, today.day)
else:
    msDate = dparser.parse(args.date)

dateBeg = UTCDateTime(msDate)
print(' Data begin: ' + dateBeg.strftime("%Y-%m-%d") + " (" + dateBeg.strftime("%Y-%j") + ")" )

filesWantFrom = dateBeg.strftime("%Y.%j")

# STA/LTA values
staSeconds= 1.0
ltaSeconds= 4.0
thresOn = 3.0
thresOf = 2.5

dirResults = "/home/seisan/tmp--DONT_USE/mseedTriggers"

nowString = today.strftime("-%Y%m%d")
fileDoIt = "".join( ["doit", nowString,".sh"] )
fileDoIt = "/".join( [dirResults, fileDoIt] )
fileDo = open(fileDoIt, "w" )
fileDo.write( '#!/usr/bin/bash' )
fileDo.write( "\n" )

# Loop round stations to process
#for sta in ["MBFR","MBLY","MBLG"]:
for sta in ["MSS1"]:
#for sta in ["MSS1","DSLB"]:

    if sta == "MSS1":
        stacha = '.'.join( [sta, "", "SHZ"] )
    elif sta == "MBRY":
        stacha = '.'.join( [sta, "", "BHZ"] )
    elif sta == "GRSS":
        stacha = '.'.join( [sta, "--", "HHZ"] )
    elif sta == "DSLB":
        stacha = '.'.join( [sta, "", "HHZ"] )
    else:
        stacha = '.'.join( [sta, "00", "HHZ"] )

    # Get files to process
    if args.test:
        filesMseed = sorted( filter( os.path.isfile, glob.glob(''.join(['*',stacha,'*.mseed'])) ) ) 
        dir_name = '.'
    else:
        dir_name = args.mseed_dir
        #filesMseed = sorted( filter( os.path.isfile, glob.glob('/'.join([dir_name,sta]) + '/**/*', recursive=True) ) )
        filesMseed = sorted( filter( os.path.isfile, glob.glob('/'.join([dir_name,sta]) + '/*' + stacha + '.mseed' ) ) )


    fileTriggerCounts = ''.join([dirResults,"/triggerCounts/mseed_trigger_counts-",sta,".txt"])
    fileTriggerLists = ''.join([dirResults,"/triggerLists/mseed_trigger_list-",sta,".txt"])

    # Loop round all mseed files
    #
    for filename in filesMseed:

        basename = os.path.basename(filename)
        mseedDate = datetime.strptime(basename[0:8], '%Y.%j')
        if filename.endswith(".msd") or filename.endswith(".mseed"): 

            if basename[0:8] >= filesWantFrom:
            #if basename[0:8] != filesWantFrom:     ###### HACK FOR TEST MODE

                dirTriggerListsStaYear = '/'.join( [ dirResults, "triggerLists", sta, mseedDate.strftime('%Y') ] )
                isExist = os.path.exists(dirTriggerListsStaYear)
                if not isExist:
                    os.makedirs(dirTriggerListsStaYear)
                fileTriggerList = dirTriggerListsStaYear + "/triggers-" + sta + "-" + mseedDate.strftime('%Y%m%d') + ".txt"
                fileOut = open(fileTriggerList, "w")

                dirTriggerCountsStaYear = '/'.join( [ dirResults, "triggerCounts", sta, mseedDate.strftime('%Y') ] )
                isExist = os.path.exists(dirTriggerCountsStaYear)
                if not isExist:
                    os.makedirs(dirTriggerCountsStaYear)
                fileTriggerCount = dirTriggerCountsStaYear + "/triggerCount-" + sta + "-" + mseedDate.strftime('%Y%m%d') + ".txt"
                fileOut2 = open(fileTriggerCount, "w")

                # Read file and merge into a single trace
                st = obspy.read( filename )
                st.merge(method=0, fill_value='interpolate')
                st.slice( starttime=dateBeg, endtime=dateBeg+secInDay )
                tr = st[0]

                tr.detrend("demean")
                if sta != "MSS1":
                    tr.filter( "highpass", freq=2.0 )
        
                # Sampling rate
                df = tr.stats.sampling_rate
        

                # Calulate trigger function
                cft = classic_sta_lta(tr.data, int(staSeconds*df), int(ltaSeconds*df))
                # Get trigger list
                trigList = trigger_onset(cft, thresOn, thresOf, max_len=9e+99, max_len_delete=False)
                nTriggers = len( trigList) 


                # Plot helicorder with triggers
                st = Stream()
                st.append( tr )
                dirTriggerHelisStaYear = '/'.join( [ dirResults, "triggerHelis", sta, mseedDate.strftime('%Y') ] )
                isExist = os.path.exists(dirTriggerHelisStaYear)
                if not isExist:
                    os.makedirs(dirTriggerHelisStaYear)
                fileHeliPlot= dirTriggerHelisStaYear + "/" + mseedDate.strftime('%Y%m%d') + "--" + stacha + "-heli_trigs.png"
                title = stacha + " " + mseedDate.strftime('%Y-%m-%d') + " automatic triggers"
                if sta == "MSS1":
                    vsr = 3000
                else:
                    vsr = 10000    
                events = []
                for on, off in trigList:
                    tev = tr.stats.starttime + tr.stats.delta * on
                    events.append({'time': tev, 'text': ''})
                trTime = tr.stats.starttime
                trigTimeUTC = np.empty([nTriggers, 1], dtype=object)
                st.plot( type='dayplot',
                    events=events,
                    interval=15,
                    right_vertical_labels=False,
                    one_tick_per_line=False,
                    size=(1278,1500),
                    title=title,
                    vertical_scaling_range=vsr,
                    tick_format='%H:%M',
                    outfile=fileHeliPlot,
                    #color=['k', 'r', 'b', 'g'],
                    color='k',
                    linewidth=0.3)

                if nTriggers > 0:

                    trigTimesOn = trigList[:,0]
                    trigTimesOf = trigList[:,1]

                    trTime = tr.stats.starttime

                    # Loop round triggers
                    for iTrig in range(0,nTriggers):
                        trigTimeUTC = trTime + trigTimesOn[iTrig]/df
                        trigOnUTC = trigTimeUTC - timedelta( seconds=2 )
                        trigOffUTC = trTime + trigTimesOf[iTrig]/df
                        trigDurationSeconds = (trigTimesOf[iTrig] - trigTimesOn[iTrig]) / df

                        # Extract trace between trigger times and calculate max signal and RMS signal
                        tr2 = tr.copy()
                        tr2.trim( trigOnUTC, trigOffUTC )
                        data2 = tr2.data
                        data2Max = max( abs( data2 ) )
                        data2Rms = np.sqrt(np.mean(data2**2))


                        fileOut.write( trigTimeUTC.strftime("%Y-%m-%d %H:%M:%S") )
                        fileOut.write( "  %5.1f" % trigDurationSeconds )
                        fileOut.write( "  sta/lta %4.1f %4.1f %4.1f %4.1f" % (staSeconds, ltaSeconds, thresOn, thresOf ) )
                        fileOut.write( "  max %9.1f rms %9.1f   id: " % (data2Max, data2Rms ) )
                        fileOut.write( "\n" )

                        #fileOut2.write( trigTimeUTC.strftime("%Y-%m-%d %H:%M:%S") )
                        #fileOut2.write( "  %12.3f %12.3f" % (data2Max, data2Rms ) )
                        #fileOut2.write( " \n" )

                        fileDo.write( "/home/seisan/bin/getnPlotSpecial --quiet --tag " + sta + "_trigger" )
                        fileDo.write( " --date " + trigTimeUTC.strftime("%Y-%m-%d" + " --time " + trigTimeUTC.strftime("%H:%M:%S") ) )
                        fileDo.write( " --source mseed\n" )

                        fileDo.write( "/home/seisan/bin/getnPlotSpecial3 --quiet --tag " + sta + "_trigger" )
                        fileDo.write( " --date " + trigTimeUTC.strftime("%Y-%m-%d" + " --time " + trigTimeUTC.strftime("%H:%M:%S") ) )
                        fileDo.write( " --source mseed\n" )

                fileOut.close()
                fileOut2.write( "%s %s %4d\n" %(mseedDate.strftime('%Y%m%d'), filename, nTriggers) )
                fileOut2.close()

                #fileOutCount.write( "%s %s %4d\n" %(mseedDate.strftime('%Y%m%d'), filename, nTriggers) )
                print( mseedDate.strftime('%Y%m%d'), " ", filename, " ", nTriggers, " triggers" )

    cmd = 'cat ' + dirResults + '/triggerCounts/' + sta + '/*/triggerCount-' + sta + '*.txt' + ' | sort > ' + fileTriggerCounts
    os.system( cmd )
    
    cmd = 'cat ' + dirResults + '/triggerLists/' + sta + '/*/triggers-' + sta + '*.txt' + ' | sort > ' + fileTriggerLists
    os.system( cmd )

    
#cmd = "/usr/bin/rsync -uarq --exclude 'doit.sh' /home/seisan/tmp--DONT_USE/mseedTriggers/ /mnt/mvofls2/Seismic_Data/monitoring_data/triggers/mseedTriggers/"
#os.system( cmd )

fileDo.write( "mv *MSS1*.png triggerPlots/MSS1/\n" )
#fileDo.write( "mv *MBLY*.png triggerPlots/MBLY/\n" )
#fileDo.write( "mv *MBFR*.png triggerPlots/MBFR/\n" )
#fileDo.write( "/home/seisan/STUFF/src/mvo/mseedTriggers/purge.sh\n" )

# Shred thyself
fileDo.write( "shred -u \"$0\"" )

fileDo.close()

st = os.stat(fileDoIt)
os.chmod(fileDoIt, st.st_mode | stat.S_IEXEC)
