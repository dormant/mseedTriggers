# mseedTriggers

Runs STA/LTA trigger on miniseed files.

makeMontages.sh

## mseedTriggers, mseedTriggers.py

* Runs an STA/LTA trigger algorithm on daily miniseed files.
* Creates helicorder plot showing triggers.
* Creates *doit\*.sh* shell script to run *getnPlot* for each trigger. 
* Runs once a day as a cron job on *opsproc3*.
* Stores results in */homne/seisan/tmp--DONT_USE/mseedTriggers*.

### Usage

*mseedTriggers.py \<--test\> \<--date\> \<--mseed_dir\>*

## mseedTriggersDoit

* Runs *doit\*.sh* shell scripts created by *mseedTriggers.py*.
* Runs once a day as a cron job on *opsproc3*.
* Stores results in */homne/seisan/tmp--DONT_USE/mseedTriggers*.

## plotTriggers.m

* MATLAB scrip to plot trigger counts

## purge.sh

* Shell script to clean up directories in */homne/seisan/tmp--DONT_USE/mseedTriggers*.

## triggerList2DoIt.pl

* Create commands to run getnPlot for each event listed in */home/seisan/tmp--DONT_USE/mseedTriggers/triggerLists/mseed_trigger_list-MSS1.txt*.
* Pipe output to *doit.sh* and make it runnagle.

## Author

Roderick Stewart, Dormant Services Ltd

rod@dormant.org

https://services.dormant.org/

## Version History

* 1.0-dev
    * Working version

## License

This project is the property of Montserrat Volcano Observatory.
