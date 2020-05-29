#!/bin/sh

# function path.
funcPath=E:/lab/openssl/functions/Bad
linePath=E:/lab/openssl/functions/BadDpd

dir=$(ls -l $funcPath |awk '/^-/ {print $NF}')
for i in $dir
do
    #echo $funcPath'/'$i
	./joern-parse $funcPath'/'$i --out cpg.bin
	./joern --script E:/joern/joern-cli/graph/f-pdg.sc --params cpgFile=cpg.bin,inFile=$funcPath'/'$i,outFile=$linePath,flag=vul
done 
