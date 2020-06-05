#!/bin/sh

# function path.
sameFuncPath=E:/lab/SARD/functions/Bad/same
diffFuncPath=E:/lab/SARD/functions/Bad/diff
linePath=E:/lab/SARD/functions/BadDpd
Flag=vul

start=$(date +%s)

# process same name functions
dir=$(ls -l $sameFuncPath |awk '/^-/ {print $NF}')
for i in $dir
do
    #echo $sameFuncPath'/'$i
	./joern-parse $sameFuncPath'/'$i --out samecpg.bin
	./joern --script E:/joern/joern-cli/graph/f-pdg.sc --params cpgFile=samecpg.bin,inFile=$sameFuncPath'/'$i,outFile=$linePath,flag=$Flag
done 

# process diff name funcions
dir1=$(ls -l $sameFuncPath |awk '/^d/ {print $NF}')
for j in $dir1
do
    #echo $diffFuncPath'/'$j
	./joern-parse $diffFuncPath'/'$j --out diffcpg.bin
	./joern --script E:/joern/joern-cli/graph/total-pdg.sc --params cpgFile=diffcpg.bin,inFile=$diffFuncPath,outFile=$linePath,flag=$Flag
done

end=$(date +%s)
take=$(( end - start ))
echo Time taken to generate CPG is ${take} seconds.