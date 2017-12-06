# -*- coding: utf-8 -*-
"""
Created on 02.11.2016 17:52:18

@author: Frederik.Schaff@FernUni-Hagen.de

A "simple" Python script to create a Design of Experiment (DOE) Design Point 
Matrix (DPM), potentially mixed from latin hyper cube, simple randomisation 
(appropriate for seeds, e.g.) and factorial designs + fixed values.

For the latin hyper cube, if a small sample size is given, the maximum pair-
wise correlation is minised. If a larger sample is given, the distribution is
such that the minimum distance between points is maximised AND the points are
centered within intervals
"""
USAGE = """ \
    
    All the information regarding parameters for the DOE design is provided as
    optional arguments with the command line. Default in []
    -n: [10] LHD Sample Size (total, integer). Alternatively:
    -N: [1] LHD Sample Size equal to multiple of factors (rounded)
             Note: Sample Size is n*{} {Size of Factorial Design}
    -l: The kind of optimisation for the lhs (default: corr). 
        Alternatives: c,m,cm or none
    -i: [10] Number of iterations for the LHD 
    -s: [42] initial seed for the DOE generation within python
    -C: ["Config"] The name of the config. If an aggregate Config is created, 
        it is saved as "\Config_full.tsv", single ones are saved as 
        "\Config_id.tsv" each. The folder is provided via -o/O
    -f: Input Design Matrix file, see below (tab separeted file) - Full Path
    -F: Input Design Matrix file, alternatively as relative path (to script loc)
    -o: Output Design Matrix dir - Full Path
    -O: ["DOE"]Output Design Matrix dir, alternatively as relative path (to script loc)
    -r: [Yes] Yes / No, specify if the factorial configurations shall be 
        randomly ordered in the output design matrix (a continuous config ID is
        preserved). Useful if computiational effort of factorials varies.
    -x: [0] Offest for the unique config ID. If, e.g., the set of configs shall
        be appended later on. NOTE: Generating the complete set at once yealds
        different results!
....-I: [off] Print info of configuration only, instead of creating it. (any argument)
....-A: ["Yes"] Provide aggregate (default) or individual ("any other input") 
        configuration file(s) instead of a big one.
    -t: [off] For testing, you may want to create only a small fraction of the 
        full set-up. Select a number (positive) of configurations randomly 
        taken. In single file mode, these will be randomly fetched. In 
        aggregate mode these will be consequtive.
   
All the information regarding the factors ("Parameters") is provided in a
    tab separeted file, the Input Design Matrix. 
    An example is given with "ExampleIDM.tsv"
    
The file follows the following structure (headers needed):
+-----------+---------+------------+-----------+--------------+--------------+
| Parameter | Minimum |  Maximum   | Increment |   Type       | Comment      |
+-----------+---------+------------+-----------+--------------+--------------+
| n_Agents  |      10 |      10000 |         1 | LHD          | [1]          |
| p_crowded |    0.01 |        .99 |       0.2 | Factorial    | [2]          |
| seed      |       1 | 2147483647 |         1 | Random       | [3]          |
| Lambda    |     0.1 |        0.9 |       0.4 | Fixed        | [4]          |
| beta      |      10 |      10000 |        10 | FactPower    | [5]          |
+-----------+---------+------------+-----------+--------------+--------------+

Comments:
    [1] A random integer value in [10,10000], selected via Latin Hyper Cube D.
    [2] Factorial design, {0.01,0.21,0.41,...,0.91}                           
    [3] A random integer value in [1,2147483647], selected randomly (not LHD)
    [4] Fixed to min, here: 0.5
    [5] Factorial design, increment by powers of "Increment". In example:
        10*10^0,10*10^1,...,10*10^3.
    
Output: A tab separeted (tsv) file holding a (M+1)x(N+1) matrix of the design of experiment, where: 
- M (rows) is the number of Configurations + a header line
- N (columns) Is the number of parameters + a unique ConfigID

The Outputfile is always of format:
- [Single Files] "DOE\DPM_Config_1.tsv"
- [Aggregate]	"DOE\DPM_Config.tsv"

Example:
+----------------+------+-------+------+
| ABMAT_ConfigID | Par1 | Par2  | Par3 |
+----------------+------+-------+------+
|              1 |   .3 | .3    | 10.0 |
|              2 |   .2 | .2e-3 |  0.1 |
|              3 |   .4 | .2    |  9.9 |
+----------------+------+-------+------+            

Workings:
Random Values are drawn new each time for each configuration.
LHD Factors are drawn once at the beginning, using the pyDOE library.
If additional Factorial Design is used, the LHD Matrix is multiplied as needed
for the factorial design.  

Potential "upgrades":
Provide opportunity to use specific distributions for the LHD. See pyDOE page
for information on this.
      
"""

"""Import Libraries"""
import numpy as np
import random as random
import os
import getopt
#dir_path = os.path.dirname(os.path.realpath(__file__)) #get dir of file
dir_path =os.getcwd() #get dir of file, if __file__ makes problems
#from tabulate import tabulate #https://pypi.python.org/pypi/tabulate - to make nice tables
import pyDOE #http://pythonhosted.org/pyDOE/randomized.html
import csv as csv # to load the input file.


def DOE(DOE_Seed,LHD_SampleSize,LHD_SamplingStrategy,IDM_path,DPM_path,LHD_iterations,RandomiseCFGs,Offset,InfoOnly,make_single_files,DPM_base_name,test_mode):
    np.random.seed(DOE_Seed) #fix

    print("STARTING\n")

    #Load the Import Design Matrix       
    IDM_f = open(IDM_path, encoding='utf-8')
    IDM = []
    csvReader = csv.reader(IDM_f, delimiter = "\t")
    i=0
    for row in csvReader:
        if (i>=1):
            IDM.append(row)  
        i+=1
    IDM_f.close()
    
    #Conv numerics to numerics
    for row in range(0,len(IDM)):
        IDM[row][1]=float(IDM[row][1])
        IDM[row][2]=float(IDM[row][2])
        IDM[row][3]=float(IDM[row][3])
                
    #Calculate the size of the full-factorial and the number of LHD parameters
    Indicator_DPM = [] #Hold information on the kind of the parameter in the final DPM
    Factorials = [] #Hold Factorial series, also that of FactPower
    LHD_factors = 0
    for row in range(0,len(IDM)):
        Indicator_DPM.append(IDM[row][4])
        if IDM[row][4]=="LHD":
            LHD_factors+=1        
        elif IDM[row][4]=="Factorial" or IDM[row][4]=="Fact" :
            val = IDM[row][1]
            tmp = [val]
            while (val + IDM[row][3] <= IDM[row][2]):
                val += IDM[row][3]
                tmp.append(val)
            tmp = np.asarray(tmp)
            #tmp = np.arange(IDM[row][1],IDM[row][2],IDM[row][3])            
            Factorials.append( [ IDM[row][0] , tmp ] ) #parname, #items            
        elif IDM[row][4]=="FactPower":
            tmp = []
            pw = int (0)
            while (IDM[row][1]*IDM[row][3]**pw <=IDM[row][2]):
                tmp.append(IDM[row][1]*IDM[row][3]**pw)
                pw+=1
            Factorials.append( [IDM[row][0], np.asarray(tmp)] ) #parname, #items                

    #Calculate the size of the LHD sample part
    if LHD_SampleSize < 0:
        LHD_SampleSize*=-LHD_factors
        LHD_SampleSize = round(LHD_SampleSize)
        
    #Calculate the size of the overal sample
    FactSampleSize=1    
    for item in range(len(Factorials)):
        FactSampleSize*=Factorials[item][1].size
    SampleSize =  int(max(1,LHD_SampleSize)*FactSampleSize)   
    print ("Factorial design with ",len(Factorials), " factors and ", \
            FactSampleSize, "configurations.\n")
    print ("Latin Hyper Cube design with ", LHD_factors, " Factors and ",\
           LHD_SampleSize, " distinct design points for each\n")
    print("Overal sample size is: ", SampleSize)
    if test_mode>0 and test_mode < SampleSize:            
        print("\nTest mode selected. Sample Size is now:",test_mode)

    
    if (InfoOnly!=0):
        print("\nExit. Info only mode.\n")
        return "Done"

    #Create a reduced form design point matrix of the factorial factors.
    Fact_DPM = np.empty([FactSampleSize,len(Factorials)],"float64")
    loops=1
    for col in range(0,len(Factorials)):
        row=0
        while row < FactSampleSize:            
            for item in range(Factorials[col][1].size):
                loop_count=0
                while loop_count < loops:
                    Fact_DPM[row][col]=Factorials[col][1][item]
                    loop_count+=1
                    row+=1
        loops*=Factorials[col][1].size #increase the number of repeated vals
                
    #select sampling method for LHD part
    if LHD_SampleSize > 0:
        print ("Using strategy " + LHD_SamplingStrategy + " for the LHS")
        if (LHD_SamplingStrategy == "corr" or LHD_SamplingStrategy == "correlation"):
            print ("with " + str(LHD_iterations) + " iterations \n")
        
        #Provide the LHD Matrix as raw
        if LHD_SamplingStrategy == "none" :
            LHD_raw=pyDOE.lhs(LHD_factors, samples=LHD_SampleSize,iterations=LHD_iterations)
        else:
            LHD_raw=pyDOE.lhs(LHD_factors, samples=LHD_SampleSize,criterion=LHD_SamplingStrategy,iterations=LHD_iterations)                      
    
        #Print correlation matrix
        a = np.corrcoef(LHD_raw)
        print ("Correlation Matrix:")
        print(a)
            
            #Normalise to values
        LHD_DPM=np.copy(LHD_raw)
        for row in range(LHD_SampleSize):
            LHD_col = 0
            for col in range(len(Indicator_DPM)):
                if Indicator_DPM[col]=="LHD":
                    LHD_DPM[row][LHD_col]*=(IDM[col][2]-IDM[col][1]) #spannwidth
                    LHD_DPM[row][LHD_col]+=IDM[col][1] #add minimum
                    #Now, correct to step-size
                    LHD_DPM[row][LHD_col]=round(LHD_DPM[row][LHD_col]/IDM[col][3])
                    LHD_DPM[row][LHD_col]*=IDM[col][3]
                    LHD_col+=1                          
    
    #Provide a "Header" for the DPM with Parameter Names and ConfigID    
    DPM_header = [] #header
    for row in range(len(IDM)):
        DPM_header.insert(row,IDM[row][0])
    DPM_header.insert(0,"ABMAT_ConfigID")
    Indicator_DPM.insert(0,"ID")
    
    #Define the complete Design Point Matrix, un-normalised, samples*(Pars+1)
    DPM=np.empty([SampleSize,len(DPM_header)],"float64")
    row=0
    for LHD_row in range(max(LHD_SampleSize,1)):
        #loop through LHD and for each design-vector add the complete factorial 
        #sub-space
        for Fact_row in range(FactSampleSize):
            LHD_item=0            
            Fact_item=0
            for col in range(len(Indicator_DPM)):
                if Indicator_DPM[col]=="ID":
                    DPM[row][col]=row+1 #Set the ConfigID, starting with 1#
                elif Indicator_DPM[col]=="LHD":
                    DPM[row][col]=LHD_DPM[LHD_row][LHD_item]
                    LHD_item+=1
                elif Indicator_DPM[col]=="Factorial" or Indicator_DPM[col]=="FactPower":
                    DPM[row][col]=Fact_DPM[Fact_row][Fact_item]
                    Fact_item+=1
                elif Indicator_DPM[col]=="Fixed":
                    DPM[row][col]=IDM[col-1][1] #Minimum
                elif Indicator_DPM[col]=="Random":
                    DPM[row][col]=IDM[col-1][2]-IDM[col-1][1] #Span
                    DPM[row][col]*=np.random.uniform() #randomise
                    DPM[row][col]+=IDM[col-1][1] #add minimum
                    #Now, correct to step-size
                    DPM[row][col]=round(DPM[row][col]*IDM[col-1][3])
                    DPM[row][col]/=IDM[col-1][3]
                else:
                    print("Error! Unknown Type of Variable: ", \
                          Indicator_DPM[col] )
            row+=1
    
    #mix the order? Is espescially important in case of distributed "packages"
    #of simulations and factorial designs, where the simulation time may vary 
    #with the factorial's values. E.g. scale parameters.
    if (RandomiseCFGs == "Yes"):
        np.random.shuffle(DPM)
        for row in range(SampleSize):
            DPM[row][0]=row+1+Offset #Assign the unique configuration ids
            
    """
    Save the DPM to a tab-separated file
    """
    
    os.makedirs(os.path.dirname(DPM_path+"\\"), exist_ok=True) #Create dir if necessary
    sample = range(SampleSize)
    if (not make_single_files):
        #Save everything to a tsv file.
        out_file = DPM_path + "\\DPM_" + DPM_base_name + ".tsv"         
        DPM_f = open(out_file, 'w',encoding='utf-8',newline='')    
        csvWriter = csv.writer(DPM_f, delimiter = "\t")
        csvWriter.writerow(DPM_header)
        if test_mode>0 and test_mode < SampleSize:            
            sample = range(test_mode)
        for row in sample:
            csvWriter.writerow(DPM[row])
        DPM_f.close()
    else:
        #create single tsv files        for row in range(SampleSize):        
        if test_mode>0 and test_mode < SampleSize:
            sample = random.sample(sample, test_mode)
            print(sample)
        for row in sample:
            out_file = DPM_path + "\\DPM_" + DPM_base_name + "_" + str(int(DPM[row][0])) + ".tsv"         
            DPM_f = open(out_file, 'w',encoding='utf-8',newline='')    
            csvWriter = csv.writer(DPM_f, delimiter = "\t")
            csvWriter.writerow(DPM_header)    
            csvWriter.writerow(DPM[row])
            DPM_f.close()
   
    return "DoneA" 

""" The main program"""
def main(argv):
    usage = USAGE#"Some information on usage\n"

    #Default Parameters
    DOE_Seed=42
    LHD_SampleSize=100
    LHD_SamplingStrategy="corr"
    IDM_path = "input\\ExampleIDM.tsv"    #windows format..
    DPM_path = "DOE" #The Output matrix folder
    DPM_base_name ="Config"
    LHD_iterations=10
    RandomiseCFGs = "Yes"
    Offset = 0
    InfoOnly = 0 #Only information on proposed Set. Not generation.
    make_single_files = False
    test_mode = 0 #off

    #Get the arguments    
    try:
        opts, args = getopt.getopt(argv,"f:F:h:i:l:n:N:o:O:r:s:x:I:A:C:t:")
    except getopt.GetoptError:
        print("\nERROR ERROR ERROR\n \t check arguments.\n")
        print(USAGE)
        print("\n\n")
        #print(usage)
        os.sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h"):
            print(usage)
            os.sys.exit(2)
        if opt in ("-s"):
            DOE_Seed = int(arg)
        elif opt in ("-n"):
            LHD_SampleSize = int(arg)
        elif opt in ("-N"):
            LHD_SampleSize = -float(arg)
        elif opt in ("-f"):
            IDM_path = str(arg)
        elif opt in ("-o"):
            DPM_path = str(arg)        
        elif opt in ("-F"):
            IDM_path = dir_path + "\\" + str(arg)
        elif opt in ("-O"):
            DPM_path = dir_path + "\\" + str(arg)
        elif opt in ("-l"):
            LHD_SamplingStrategy = str(arg)
        elif opt in ("-i"):
            LHD_iterations = int(arg)
        elif opt in ("-r"):
            RandomiseCFGs = str(arg)
        elif opt in ("-x"):
            Offset = int(arg)
        elif opt in ("-t"):
            test_mode = int(arg)
        elif opt in ("-I"):
            InfoOnly = 1#int(arg)
        elif opt in ("-A"):
            if str(arg) != "Yes":
                make_single_files = True
        elif opt in ("-C"):
            DPM_base_name = str(arg)
      
    DOE(DOE_Seed,LHD_SampleSize,LHD_SamplingStrategy,IDM_path,DPM_path,LHD_iterations,RandomiseCFGs,Offset,InfoOnly,make_single_files,DPM_base_name,test_mode)    
    return "Done"     
    
    

if __name__ == "__main__":
    main(os.sys.argv[1:])         