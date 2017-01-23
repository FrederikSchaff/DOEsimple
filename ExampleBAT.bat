@echo off
echo This is a windows example .bat file for DOEsimple python 3 script.
python DOEsimple.py -help
PAUSE
@echo on
python DOEsimple.py -i 1000 -l "corr" -N 2 -F "input/ExampleIDM.tsv" -O "DPM_Example.tsv"
PAUSE