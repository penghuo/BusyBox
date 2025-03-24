## EMR SPARK
* create table
```
CREATE TABLE sparkhits
USING PARQUET
LOCATION 's3://flint-data-dp-us-west-2-beta/benchmark/clickbench/parquet/';
```
* query
```
SELECT 
    UserID, 
    extract(minute FROM TIMESTAMP(EventTime)) AS m, 
    SearchPhrase, 
    COUNT(*) 
FROM sparkhits 
GROUP BY UserID, extract(minute FROM TIMESTAMP(EventTime)), SearchPhrase 
ORDER BY COUNT(*) DESC 
LIMIT 10;
```
* EMR-S configuration
```
sudo -u hdfs hdfs dfs -mkdir /user/
sudo -u hdfs hdfs dfs -chmod 777 /user
sudo -u hdfs hdfs dfs -mkdir /user/ec2-user
sudo -u hdfs hdfs dfs -chown ec2-user:ec2-user /user/ec2-user
pip install numpy
```