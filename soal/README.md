## Backgound
We explore the solution to leverage [SoAL](https://aws.amazon.com/blogs/big-data/spark-on-aws-lambda-an-apache-spark-runtime-for-aws-lambda/) to run EMR-S Spark image on Lambda

## Deployment
```
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 924196221507.dkr.ecr.us-west-2.amazonaws.com
./deploy.sh
```

### Test
```
aws lambda invoke --function-name flint-spark-on-aws-lambda --payload '{"query": "select * from soal.http_logs limit 19"}' output.txt
```
