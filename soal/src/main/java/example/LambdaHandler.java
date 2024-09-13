package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

import java.util.Map;

public class LambdaHandler implements RequestHandler<Map<String, String>, String> {

    @Override
    public String handleRequest(Map<String, String> event, Context context) {
        LambdaLogger logger = context.getLogger();
        // Extract the 'query' parameter from the input
        String query = event.getOrDefault("query", "SELECT 1");

        logger.log(new java.text.SimpleDateFormat("yy/MM/dd HH:mm:ss.SSS").format(new java.util.Date()) + " Received event: " + event.toString() + "\n");
        logger.log(new java.text.SimpleDateFormat("yy/MM/dd HH:mm:ss.SSS").format(new java.util.Date()) + " Extracted query: " + query + "\n");

        StringBuilder result = new StringBuilder();

        SparkSession spark = SparkSession.builder()
                .appName("Spark SQL Job")
                .master("local[*]")
                .config("spark.driver.memory", "5g")
                .config("spark.executor.memory", "5g")
                .config("spark.hadoop.hive.metastore.client.factory.class",
                        "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory")
                .config("spark.driver.bindAddress", "127.0.0.1")
                .config("spark.driver.extraClassPath", "/usr/lib/livy/rsc-jars/*:/usr/lib/livy/repl_2.12-jars/*:/usr/lib/hadoop-lzo/lib/*:/usr/lib/hadoop/hadoop-aws.jar:/usr/share/aws/aws-java-sdk/*:/usr/share/aws/emr/emrfs/conf:/usr/share/aws/emr/emrfs/lib/*:/usr/share/aws/emr/emrfs/auxlib/*:/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/usr/share/aws/emr/goodies/lib/emr-serverless-spark-goodies.jar:/usr/share/aws/emr/security/conf:/usr/share/aws/emr/security/lib/*:/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/docker/usr/lib/hadoop-lzo/lib/*:/docker/usr/lib/hadoop/hadoop-aws.jar:/docker/usr/share/aws/aws-java-sdk/*:/docker/usr/share/aws/emr/emrfs/conf:/docker/usr/share/aws/emr/emrfs/lib/*:/docker/usr/share/aws/emr/emrfs/auxlib/*:/docker/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/docker/usr/share/aws/emr/security/conf:/docker/usr/share/aws/emr/security/lib/*:/docker/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/docker/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/docker/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/docker/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/usr/share/aws/redshift/jdbc/RedshiftJDBC.jar:/usr/share/aws/redshift/spark-redshift/lib/*:/usr/share/aws/iceberg/lib/iceberg-emr-common.jar:/usr/share/aws/iceberg/lib/iceberg-spark3-runtime.jar")
                .config("spark.driver.extraJavaOptions", "-Djava.net.preferIPv6Addresses=false -XX:OnOutOfMemoryError='kill -9 %p' -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false -XX:OnOutOfMemoryError='kill -9 %p' -XX:UseAVX=2")
                .config("spark.executor.extraClassPath", "/usr/lib/hadoop-lzo/lib/*:/usr/lib/hadoop/hadoop-aws.jar:/usr/share/aws/aws-java-sdk/*:/usr/share/aws/emr/emrfs/conf:/usr/share/aws/emr/emrfs/lib/*:/usr/share/aws/emr/emrfs/auxlib/*:/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/usr/share/aws/emr/goodies/lib/emr-serverless-spark-goodies.jar:/usr/share/aws/emr/security/conf:/usr/share/aws/emr/security/lib/*:/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/docker/usr/lib/hadoop-lzo/lib/*:/docker/usr/lib/hadoop/hadoop-aws.jar:/docker/usr/share/aws/aws-java-sdk/*:/docker/usr/share/aws/emr/emrfs/conf:/docker/usr/share/aws/emr/emrfs/lib/*:/docker/usr/share/aws/emr/emrfs/auxlib/*:/docker/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/docker/usr/share/aws/emr/security/conf:/docker/usr/share/aws/emr/security/lib/*:/docker/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/docker/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/docker/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/docker/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/usr/share/aws/redshift/jdbc/RedshiftJDBC.jar:/usr/share/aws/redshift/spark-redshift/lib/*:/usr/share/aws/iceberg/lib/iceberg-emr-common.jar:/usr/share/aws/iceberg/lib/iceberg-spark3-runtime.jar")
                .config("spark.executor.extraJavaOptions", "-Djava.net.preferIPv6Addresses=false -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+UseParallelGC -XX:InitiatingHeapOccupancyPercent=70 -XX:OnOutOfMemoryError='kill -9 %p' -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+UseParallelGC -XX:InitiatingHeapOccupancyPercent=70 -XX:OnOutOfMemoryError='kill -9 %p' -XX:UseAVX=2")
                .config("spark.hadoop.fs.s3a.aws.credentials.provider", "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider")
                .config("spark.hadoop.fs.s3.customAWSCredentialsProvider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
                .config("spark.hadoop.fs.defaultFS", "file:///")
                .config("spark.hadoop.fs.s3.impl", "com.amazon.ws.emr.hadoop.fs.EmrFileSystem")
                .config("spark.hadoop.fs.AbstractFileSystem.s3.impl", "org.apache.hadoop.fs.s3.EMRFSDelegate")
                .config("spark.hadoop.hive.metastore.warehouse.dir", "file:///tmp/hive-warehouse")
                .config("spark.ui.enabled", "false")
                .enableHiveSupport()
                .getOrCreate();
        
        spark.sparkContext().hadoopConfiguration().set("fs.s3.impl", "com.amazon.ws.emr.hadoop.fs.EmrFileSystem");
        spark.sparkContext().hadoopConfiguration().set("fs.AbstractFileSystem.s3.impl", "org.apache.hadoop.fs.s3.EMRFSDelegate");
        spark.sparkContext().hadoopConfiguration().addResource(new Path("/etc/hadoop/conf/core-site.xml"));
        spark.sparkContext().hadoopConfiguration().set("fs.s3.buffer.dir", "/tmp/s3");
        

        logger.log(new java.text.SimpleDateFormat("yy/MM/dd HH:mm:ss.SSS").format(new java.util.Date()) + " Executing query at " + query + "\n");
        long startTime = System.nanoTime();

        try {
            Dataset<Row> queryResult = spark.sql(query);
            result.append(queryResult.showString(20, 0, false));
        } catch (Exception e) {
            logger.log("Error executing query: " + query + "\n");
            logger.log(e.getMessage() + "\n");
            result.append("Error executing query: ").append(query).append("\n")
                  .append(e.getMessage()).append("\n");
        }

        long endTime = System.nanoTime();
        double duration = (endTime - startTime) / 1e9d;
        logger.log(new java.text.SimpleDateFormat("yy/MM/dd HH:mm:ss.SSS").format(new java.util.Date()) + " Finished query in " + duration + " seconds\n");

        return result.toString();
    }
}