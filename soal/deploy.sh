#!/bin/bash

set -e

FUNCTION_NAME="flint-spark-on-aws-lambda"
IMAGE_URI="924196221507.dkr.ecr.us-west-2.amazonaws.com/flint-spark-on-aws-lambda:0.5"

echo "Building Docker image..."
docker build --platform linux/amd64 -t flint-spark-on-aws-lambda:0.5 .

echo "Tagging Docker image..."
docker tag flint-spark-on-aws-lambda:0.5 $IMAGE_URI

echo "Pushing Docker image to ECR..."
docker push $IMAGE_URI

echo "Updating Lambda function code..."
aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri $IMAGE_URI

echo "Waiting for function update to complete..."
while true; do
    STATUS=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.LastUpdateStatus' --output text)
    if [ "$STATUS" = "Successful" ]; then
        echo "Function update completed successfully."
        break
    elif [ "$STATUS" = "Failed" ]; then
        echo "Function update failed. Please check the Lambda function logs for more information."
        exit 1
    else
        echo "Function update in progress. Current status: $STATUS"
        sleep 10
    fi
done

echo "Deployment completed successfully."