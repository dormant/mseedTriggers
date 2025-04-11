#!/usr/bin/perl

my $fileTriggerList = "/home/seisan/tmp--DONT_USE/mseedTriggers/triggerLists/mseed_trigger_list-MSS1.txt";

open(IF, $fileTriggerList) or die("Could not open  file.");

foreach $line (<IF>)  {
    chomp $line;
    my @bits = split /\s/, $line;
    print "getnPlotSpecial --tag MSS1_trigger --source mseed --date $bits[0] --time $bits[1]\n";
}
close(IF);

