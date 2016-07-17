#!/bin/bash

mkdir -p pogo/proto
rm -rf pogo/proto/*
protoc --proto_path=proto --python_out=pogo/proto `find proto -name "*proto"`
touch pogo/proto/__init__.py
