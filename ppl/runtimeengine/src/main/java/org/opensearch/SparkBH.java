package org.opensearch;

import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class SparkBH {
  private JavaSparkContext sc;
  private SparkSession sparkSession;

  public SparkBH() {
    SparkConf conf = new SparkConf()
        .setAppName("CalciteSparkBH")
        .setMaster("local[*]")
        .set("spark.ui.enabled", "false");

    sc = new JavaSparkContext(conf);
    sparkSession = SparkSession.builder()
        .config(conf)
        .getOrCreate();

    System.out.printf("", sparkSession.sql("select 1"));
  }

  public void run(String csvFilePath, String query) {
    Dataset<Row> csvDataset = sparkSession.read()
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(csvFilePath);

    csvDataset.createOrReplaceTempView("people");
    Dataset<Row> results = sparkSession.sql(query);
    results.count();
  }

  public void clean() {
    sc.stop();
  }
}
