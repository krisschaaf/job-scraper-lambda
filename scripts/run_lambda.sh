#!/bin/bash

aws lambda invoke \
    --profile job-scraper-lambda \
    --function-name job-scraper \
    --region eu-north-1 \
    --payload '{}' \
    /outputs/output.json
