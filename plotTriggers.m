% plot single station hourly trigger id counts
% 
% RCS, 2023-10-13

clear;
setup = setupGlobals();

% User input
[datesBeg, datesEnd] = askDates('now-7','now');
binWidthHours = inputd( 'Bin width (hours)', 'i', 4 );

tLimits = [datesBeg datesEnd];

fileTriggers = '/home/seisan/tmp--DONT_USE/mseedTriggers/triggerLists/mseed_trigger_list-MSS1.txt';
T = readtable( fileTriggers );

trigDatetime = T.Var1 + T.Var2;
trigDatetime.Format = 'yyyy-MM-dd HH:mm:ss';

trigDatenum = datenum( trigDatetime );

datenumBeg = floor( trigDatenum(1) );
datenumEnd = ceil( trigDatenum(end) );

binWidthHours = 4;
bins = datenumBeg:binWidthHours/24:datenumEnd;

switch binWidthHours
    case 1
        tit = "MSS1 automatic triggers per hour";
    case 24
        tit = "MSS1 automatic triggers per day";
    otherwise
        tit = sprintf( "MSS1 automatic triggers per %d hours", binWidthHours );
end


figure_size( 'l' );
tiledlayout( 'vertical' );

nexttile;
histogram( trigDatenum, bins );
xlim( tLimits );
datetick( 'x', 'keeplimits' );
xlabel( 'UTC' );
ylabel( 'Count' );
grid on;
title( 'All triggers' );




plotOverTitle( tit );

fileSave = 'fig--MSS1_triggers.png';
saveas( gcf, fileSave );
