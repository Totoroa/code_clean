#!/bin/sh

# function path.
#sameFuncPath=E:/lab/SARD/functions/Bad/same
#diffFuncPath=E:/lab/SARD/functions/Bad/diff
sameFuncPath=C:/Users/admin/Desktop/workspace-python/cleancode/openssl-1.0.0a/functions/same
diffFuncPath=C:/Users/admin/Desktop/workspace-python/cleancode/openssl-1.0.0a/functions/diff
linePath=C:/Users/admin/Desktop/workspace-python/cleancode/openssl-1.0.0a/func_dpd
Flag=src

#start=$(date +%s)

# process same name functions
#dir=$(ls -l $sameFuncPath |awk '/^-/ {print $NF}')
#for i in $dir
#do
    #echo $sameFuncPath'/'$i
#	./joern-parse $sameFuncPath'/'$i --out samecpg.bin
#	./joern --script E:/joern/joern-cli/graph/f-pdg.sc --params cpgFile=samecpg.bin,inFile=$sameFuncPath'/'$i,outFile=$linePath,flag=$Flag
#done 

# process diff name funcions
dir1=$(ls -l $diffFuncPath |awk '/^d/ {print $NF}')
for j in $dir1
do
    #echo $diffFuncPath'/'$j
	./joern-parse $diffFuncPath'/'$j --out diffcpg.bin
	./joern --script E:/joern/joern-cli/graph/total-pdg.sc --params cpgFile=diffcpg.bin,inFile=$diffFuncPath'/'$j,outFile=$linePath,flag=$Flag
done

end=$(date +%s)
take=$(( end - start ))
echo Time taken to generate CPG is ${take} seconds.