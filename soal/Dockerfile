# Dockerfile
FROM public.ecr.aws/emr-serverless/spark/emr-7.2.0:latest

# Add your JAR file to the container
COPY target/scala-2.12/SQLJob-1.0.jar /app/SQLJob-1.0.jar

# Set entrypoint to the jar
ENTRYPOINT ["spark-submit", "--class", "org.apache.spark.SQLJob", "/app/SQLJob-1.0.jar"]