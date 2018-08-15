#DOEsimple
A "simple" Python 3 file to create a Design of Experiment (DOE) Design Point 
Matrix (DPM), potentially mixed from latin hyper cube, simple randomisation 
(appropriate for seeds, e.g.), factorial designs (including power) and also 
fixed values. For latin hyper cube designs the [PyDOE](https://github.com/tisimst/pyDOE) library
is used.

For the latin hyper cube, the optimisation approach can be specified (deault: correlation), 
alongside with the number of iterations. See [PyDOE](https://github.com/tisimst/pyDOE) for more information.

(to install pydoe with conda: `conda install -c conda-forge pydoe ` )

##Usage
You can call the program via command line, using the following arguments, the 
defaults are specified in [].

-n: [10] LHD Sample Size (total). Sample Size is n*{} {Size of Factorial Design}

-N: LHD Sample Size, alternatively provided as a multiple of LHD factors (rounded

-l: The kind of optimisation for the lhs (default: corr). Alternatives: c,m,cm or none 

-i: [10] Number of iterations for the LHD optimisation 

-s: [42] initial seed for the DOE generation within python

-f: Input Design Matrix, see below (tab separeted file) - Full Path

-F: Input Design Matrix, alternatively as relative path (to script loc)

-o: Output Design Matrix directory - Full Path

-O: Output Design Matrix directory, alternatively as relative path (to script loc)

-r: [Yes] Yes / No, specify if the factorial configurations shall be randomly ordered  in the output design matrix (a continuous config ID is preserved). Useful if  computiational time of factorials varies.

-x: [0] Offest for the unique config ID. If, e.g., the set of configs shall be appended later on. NOTE: Generating the complete set at once yields different results!

-I: [off] Print info of configuration only, instead of creating it. (any argument)

-A: ["Yes"] Provide single (default) or aggregate ("any other input")  configuration files instead of a big one. Folder is "/Configs/" and files are "CID_1.tsv" for the first CID, etc.

-t: [off] For testing, you may want to create only a small fraction of the  full set-up. Select a number (positive) of configurations randomly taken. In single file mode, these will be randomly fetched. In aggregate mode these will be consequtive.

##Input File   
All the information regarding the factors ("Parameters") is provided in a tab separeted file, the Input Design Matrix. An example is given with "input/ExampleIDM.tsv"
    
The file follows the following structure (headers needed, without comments):

 Parameter | Minimum |  Maximum   | Increment |   Type | Comment  
---|---|---|---|---|---
 n_Agents  |  10 |  10000 | 1 | LHD  | [1]   
 p_crowded |0.01 |.99 |   0.2 | Factorial| [2]
 seed  |   1 | 2147483647 | 1 | Random   | [3]
 Lambda| 0.1 |0.9 |   0.4 | Fixed| [4]
 beta  |  10 |  10000 |10 | FactPower| [5]


Comments:
    [1] A random integer value in [10,10000], selected via Latin Hyper Cube D.
    [2] Factorial design, {0.01,0.21,0.41,...,0.91}                                
    [3] A random integer value in [1,2147483647], selected randomly (not LHD)
    [4] Fixed to min, here: 0.1
    [5] Factorial design, increment by powers of "Increment". In the example:

`10*10^0 , 10*10^1 , ... , 10*10^3`
    
Output: A tab separeted (tsv) file holding a (M+1)x(N+1) matrix of the design of experiment, where: 
- M (rows) is the number of Configurations + a header line
- N (columns) Is the number of parameters + a unique ConfigID

The Outputfile is always of format:
- [Single Files] "Out\DPM_Config_1.tsv"
	 [Aggregate]	"Out\DPM_Config.tsv"
###Example:

ABMAT_ConfigID | Par1 | Par2  | Par3
---|---|---|---
1 |   .3 | .3    | 10.0
2 |   .2 | .2e-3 |  0.1
3 |   .4 | .2    |  9.9

**An example *.batch file for Windows clients (python 3 installed) is attached.**

##Workings:
Simple Random Values are drawn new each time for each configuration.
LHD Factors are drawn once at the beginning, using the pyDOE library. The 
default strategy is to use "corr" option, which minimises the maximum absolute
correlation between vectors. Alternatively, if LHD_SampleSize/LHD_factors > 30,
"centermaximin" is chosen. See the [PyDOE](https://github.com/tisimst/pyDOE) description for more information.
If additional Factorial Design is used, the LHD Matrix is multiplied as needed
for the factorial design.

##Advancements and NO warranty
If someone uses the file and has a good idea regarding and advancement, etc., feel free to do so! 
I intended it for personal use but thought I might as well share it, therefore it is provided "as-is"
without any warranty or whatsoever.
