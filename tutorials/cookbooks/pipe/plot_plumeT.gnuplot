# set terminal qt size 800,450
# set terminal pdf size 10,6
# set output "sales_data.pdf"

set multiplot layout 1, 1 
# set bmargin 20
set yrange [0:410]
set ytics 0, 50
set tics font ",20" 
set ytics textcolor "red"
set ytics nomirror
set title font ",20"
set ylabel "Temperature (℃)" offset -2.5 font ",20" textcolor "red"
unset key

# subfigure (A)
set lmargin 10
# unset xlabel
# unset xtics
set title "Pipe model"
# set label "(A)" at graph 0.02, 0.9 font ",20"
# set label "250 years" at graph 0.7, 0.9 font ",20"
plot  "<grep -r \"Plume Temperature\"  log.HydrothermalSinglePhaseDarcyFoam | awk '{print $3, $4}' " with lines lw 2 lc "red" axis x1y1 

pause 10
reread