set key at 300, 300
set key font ",15"
set tics font ",15"
set title font ",15"
set ylabel "Temperature (C)" offset -2 font ",15"
set xlabel "Time (year)" font ",15"


plot "postProcessing/probes/0/T" using ($1/86400/365):($2-273.15) with lines lw 4 title "Probe" , \
    "postProcessing/plumeTemperature/plumtTemperature.txt" using ($1/86400/365):($2-273.15) with lines lw 4 title "Plume"