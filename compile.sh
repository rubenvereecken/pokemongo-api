#!/bin/bash

mkdir -p pogo/proto
rm -rf pogo/proto/*
cd ./proto/
./compile.py -l python -o ../pogo/proto
cd ../
find ./pogo/proto/ -type d -exec touch {}/__init__.py \;
echo "'Generated'; import os; import sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))" > ./pogo/proto/__init__.py
