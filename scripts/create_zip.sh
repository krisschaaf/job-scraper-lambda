#!/bin/bash

rm -rf ../build/
mkdir ../build
mkdir ../build/package
pip install -r ../requirements.txt -t ../build/package/
cp ../src/*.py ../build/package/
cp ../config.yaml ../build/package/
cd ../build/package
zip -r ../lambda_package.zip .
cd ../../scripts