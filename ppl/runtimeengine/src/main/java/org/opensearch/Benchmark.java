package org.opensearch;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Benchmark {
  public static void main(String[] args) {
//    testSpark();
//    testCalcite();
//    testCalciteRelNode();
    testCalciteDataType();
  }

  public static void printStats(List<Long> times, String name) {
    Collections.sort(times);

    long total = times.stream().mapToLong(Long::longValue).sum();
    double average = total / (double) times.size();
    long p50 = times.get(times.size() / 2);
    long p100 = times.get(times.size() - 1);

    System.out.println(String.format("====== %s Benchmark Results ======", name));
    System.out.println("Average: " + average + " ms");
    System.out.println("p50: " + p50 + " ms");
    System.out.println("p100: " + p100 + " ms");
  }

  public static void testSpark() {
    String csvFilePath = "/Users/penghuo/oss/BusyBox/ppl/data/spark/people.csv";
    String query = "SELECT name, age FROM people WHERE age > 30";

    SparkBH sparkBH = new SparkBH();
    // warmup
    for (int i = 0; i < 3; i++) {
      sparkBH.run(csvFilePath, query);
    }

    // iteration
    int rounds = 10;
    List<Long> executionTimes = new ArrayList<>();
    for (int i = 0; i < rounds; i++) {
      long startTime = System.nanoTime();
      sparkBH.run(csvFilePath, query);
      long endTime = System.nanoTime();

      long durationInMillis = (endTime - startTime) / 1_000_000;
      executionTimes.add(durationInMillis);
    }

    sparkBH.clean();
    printStats(executionTimes, "Spark");
  }

  public static void testCalcite() {
    String csvFilePath = "/Users/penghuo/oss/BusyBox/ppl/data/calcite";
    String query = "SELECT name, age FROM people WHERE age > 30";

    CalciteBH calciteBH = new CalciteBH(csvFilePath);
    // warmup
    for (int i = 0; i < 3; i++) {
      calciteBH.run(query);
    }

    // iteration
    int rounds = 10;
    List<Long> executionTimes = new ArrayList<>();
    for (int i = 0; i < rounds; i++) {
      long startTime = System.nanoTime();
      calciteBH.run(query);
      long endTime = System.nanoTime();

      long durationInMillis = (endTime - startTime) / 1_000_000;
      executionTimes.add(durationInMillis);
    }

    calciteBH.clean();
    printStats(executionTimes, "Calcite");
  }

  public static void testCalciteRelNode() {
    String csvFilePath = "/Users/penghuo/oss/BusyBox/ppl/data/calcite";
//    String query = "SELECT name, age FROM people WHERE age > 30";
    String query = "SELECT p1.name, p2.age FROM people as p1 JOIN people as p2 ON p1.age = p2.age";

    CalciteBH calciteBH = new CalciteBH(csvFilePath);
    // warmup
    for (int i = 0; i < 3; i++) {
      calciteBH.run(query);
    }

    // iteration
    int rounds = 10;
    List<Long> executionTimes = new ArrayList<>();
    for (int i = 0; i < rounds; i++) {
      long startTime = System.nanoTime();
      calciteBH.runRelNode(query);
      long endTime = System.nanoTime();

      long durationInMillis = (endTime - startTime) / 1_000_000;
      executionTimes.add(durationInMillis);
    }

    calciteBH.clean();
    printStats(executionTimes, "Calcite");
  }

  public static void testCalciteDataType() {
    String csvFilePath = "/Users/penghuo/oss/BusyBox/ppl/data/calcite";
    String query = "describe table people";

    CalciteBH calciteBH = new CalciteBH(csvFilePath);
    // warmup
    for (int i = 0; i < 3; i++) {
      calciteBH.run(query);
    }

    // iteration
    int rounds = 10;
    List<Long> executionTimes = new ArrayList<>();
    for (int i = 0; i < rounds; i++) {
      long startTime = System.nanoTime();
      calciteBH.run(query);
      long endTime = System.nanoTime();

      long durationInMillis = (endTime - startTime) / 1_000_000;
      executionTimes.add(durationInMillis);
    }

    calciteBH.clean();
    printStats(executionTimes, "Calcite");
  }
}
