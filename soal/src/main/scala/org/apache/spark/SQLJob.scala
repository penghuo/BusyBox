package org.apache.spark

import org.apache.spark.internal.Logging
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.streaming.Trigger

import java.util.concurrent.TimeUnit

import scala.concurrent.duration._

object SQLJob extends Logging {

  def main(args: Array[String]) {
    // val queries = args(0).split(";").map(_.trim)

    val spark = SparkSession.builder()
      .appName("Spark SQL Job")
      .master("local[*]")
      .config("spark.driver.memory", "5g")
      .config("spark.executor.memory", "5g")
      .config(
        "spark.hadoop.hive.metastore.client.factory.class",
        "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory",
      )
      .enableHiveSupport()
      .getOrCreate()

    args.foreach { query =>
      logInfo(s"Executing query: $query")
      println(s"Executing query: $query")
      val startTime = System.nanoTime()

      try {
        val result = spark.sql(query)
        result.show()
      } catch {
        case e: Exception =>
          logError(s"Error executing query: $query", e)
      }

      val endTime = System.nanoTime()
      val duration = (endTime - startTime) / 1e9d
      logInfo(s"Finished query in $duration seconds")
      println(s"Finished query in $duration seconds")
    }

    spark.stop()
  }
}