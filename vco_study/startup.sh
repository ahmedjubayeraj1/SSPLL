#!/bin/bash
# startup.sh N SC I : symmetric power-up and forced common-mode + 10 mV kick at 5 corners
N=$1; SC=$2; I=$3
for spec in "tt 27 5f" "ss 110 10f" "ff -40 0" "fs 27 5f" "sf 27 5f"; do
  set -- $spec
  for mode in pwrup cm; do
    f=su_${N}_${SC}_$1_$mode.sp
    python3 ringgen.py $N $SC $1 $2 $I 0.9 $3 $mode $f
    echo "$N $SC $1 $2 $mode $(timeout 900 ngspice -b $f 2>&1 | grep -E '^(f|ppd) = ' | awk '{printf "%s=%s ", $1, $3}')" &
  done
  wait
done
