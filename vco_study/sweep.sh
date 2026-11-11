#!/bin/bash
# sweep.sh N SC corner temp cpar vtune "I list"  -> prints I f vdd ppd
N=$1; SC=$2; C=$3; T=$4; CP=$5; VT=$6; IL=$7
for I in $IL; do
 (f=r_${N}_${SC}_${C}_${T}_${CP}_${VT}_${I}; python3 ringgen.py $N $SC $C $T $I $VT $CP run $f.sp
  out=$(timeout 600 ngspice -b $f.sp 2>&1); 
  echo "$N $SC $C $T $CP $VT $I $(echo "$out" | grep -E '^f = ' | awk '{print $3}') $(echo "$out" | grep -E '^vdd_avg = ' | awk '{print $3}') $(echo "$out" | grep -E '^ppd = ' | awk '{print $3}')"
  rm -f $f.sp) &
done; wait
