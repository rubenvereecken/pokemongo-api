#!/bin/bash

rm -rf pogo/proto
cd ./proto/
./compile.py -l python -o ../pogo/
cd ../
