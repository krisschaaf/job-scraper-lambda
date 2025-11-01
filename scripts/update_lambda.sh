#!/bin/bash

./create_zip.sh

aws lambda update-function-code \
    --profile job-scraper-lambda \
    --region eu-north-1 \
    --function-name job-scraper \
    --zip-file fileb://../build/lambda_package.zip