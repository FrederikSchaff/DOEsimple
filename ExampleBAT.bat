@echo off
echo This is a windows example .bat file for DOEsimple python 3 script.
python DOEsimple.py -i 1000 -l "corr" -N 2 -F "IDM_Example.tsv" -O "out" -C "Example" -t "10" -I "blub"
PAUSE
@echo on
python DOEsimple.py -i 1000 -l "corr" -N 2 -F "IDM_Example.tsv" -O "out" -C "Example" -t "10"
PAUSE