## Backgound
We explore the solution to leverage [SoAL](https://aws.amazon.com/blogs/big-data/spark-on-aws-lambda-an-apache-spark-runtime-for-aws-lambda/) to run Spark SQL query.

## Build
* Build the jar file
```
sbt assembly
```

* Build the docker image
```
docker build -t flint-spark-on-aws-lambda:0.1 .
```

## Run
```
docker run flint-spark-on-aws-lambda:0.1 "select 1"
```

