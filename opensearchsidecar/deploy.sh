#!/bin/bash
REPO="spark-os-snapshot:0.2"
IMAGE_URI="924196221507.dkr.ecr.us-west-2.amazonaws.com/$REPO"

echo "Building Docker image..."
docker build --platform linux/amd64 -t $REPO .

echo "Tagging Docker image..."
docker tag $REPO $IMAGE_URI

echo "Pushing Docker image..."
docker push $IMAGE_URI

# Stop EMR Serverless application
echo "Stopping EMR Serverless application..."
APPLICATION_ID="00fmguhj59pa5a0l"
aws emr-serverless stop-application --application-id $APPLICATION_ID

# Update image
echo "Updating EMR Serverless application image..."
aws emr-serverless update-application \
    --application-id $APPLICATION_ID \
    --image-configuration "{\"imageUri\":\"$IMAGE_URI\"}"

# Start EMR Serverless application
echo "Starting EMR Serverless application..."
aws emr-serverless start-application --application-id $APPLICATION_ID

echo "Deployment complete."
