#!/usr/bin/bash

cd /home/seisan/tmp--DONT_USE/mseedTriggers/tmp

d=2024-10-02
while [ "$d" != 2024-10-09 ]
do

  d2=${d//-/''}
  echo -n "${d2}   "

  mv ../triggerPlots/MSS1/$d2*special3*.png .
  nfiles=`ls *.png | wc -l`
  echo $nfiles

  if [[ "$nfiles" -ge 100 ]]
  then
    magick montage *special3*.png -tile 100x1 -geometry +0+0 "${d2}-MSS1-special3montage.png"
  else
    magick montage *special3*.png -tile x1 -geometry +0+0 "${d2}-MSS1-special3montage.png"
  fi

  mv *special3montage*.png ../triggerPlotMontages/
  rm *.png

  d=$(date -I -d "$d + 1 day")

done

cd -
