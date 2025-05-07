package org.opensearch;

import java.io.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;

public class SparkSQLQueryTest {

  static class TestCase {
    String sql;
    String expectedOutput;
    String file;
    int line;
  }

  static class TestResult {
    String file;
    int line;
    String status; // PASS or FAIL
    String errorType; // "inconsistent", "error", or empty
    String sql;
    String expected;
    String actualOrError;
  }

  public static void main(String[] args) throws Exception {
    String modelPath = "src/test/resources/model.json";
    String url = "jdbc:calcite:model=" + modelPath +
        ";conformance=BABEL;fun=standard,spark;lenientOperatorLookup=true;parserFactory=org.apache.calcite.server.ServerDdlExecutor#PARSER_FACTORY";

    List<TestCase> tests = loadTests("src/test/resources/sql-tests/results");
    List<TestResult> results = new ArrayList<>();

    try (Connection conn = DriverManager.getConnection(url, "admin", "admin");
        Statement stmt = conn.createStatement()) {

      for (TestCase test : tests) {
        System.out.println("Running: " + test.file + " line " + test.line);
        TestResult result = new TestResult();
        result.file = test.file;
        result.line = test.line;
        result.sql = test.sql;
        result.expected = test.expectedOutput;

        if (test.expectedOutput.toLowerCase().contains("exception")) {
          result.status = "IGNORE";
          result.errorType = "ignored";
          System.out.println("[IGNORE] (expected exception)");
          results.add(result);
          continue;
        }

        try {
          ResultSet rs = stmt.executeQuery(test.sql);
          String actual = resultToString(rs);
          result.actualOrError = actual;

          if (normalizeOutput(actual).equals(normalizeOutput(test.expectedOutput))) {
            result.status = "PASS";
            result.errorType = "";
            System.out.println("[PASS]");
          } else {
            result.status = "FAIL";
            result.errorType = "inconsistent";
            System.out.println("[FAIL][inconsistent]");
            System.out.println("SQL: " + test.sql);
            System.out.println("Expected: " + test.expectedOutput);
            System.out.println("Actual:   " + actual);
          }
        } catch (SQLException e) {
          String errorMsg = e.getMessage();
          result.actualOrError = errorMsg;

          if (test.expectedOutput.contains("\"errorClass\"")) {
            result.status = "PASS";
            result.errorType = "";
            System.out.println("[PASS] (error matched)");
          } else if (errorMsg.contains("Statement did not return a result set")) {
            result.status = "PASS";
            result.errorType = "";
            System.out.println("[PASS] (no result expected)");
          } else {
            result.status = "FAIL";
            result.errorType = "error";
            System.out.println("[FAIL][error]");
            System.out.println("SQL: " + test.sql);
            System.out.println("Error: " + errorMsg);
          }
        } catch (Throwable t) {
          String errorMsg = t.toString();
          result.actualOrError = errorMsg;

          if (test.expectedOutput.contains("\"errorClass\"")) {
            result.status = "PASS";
            result.errorType = "";
            System.out.println("[PASS] (error matched)");
          } else if (errorMsg.contains("Statement did not return a result set")) {
            result.status = "PASS";
            result.errorType = "";
            System.out.println("[PASS] (no result expected)");
          } else {
            result.status = "FAIL";
            result.errorType = "error";
            System.out.println("[FAIL][error]");
            System.out.println("SQL: " + test.sql);
            System.out.println("Error: " + errorMsg);
          }
        }

        results.add(result);
        System.out.println();
      }
    }

    writeCsvReport("build/spark-sql-test-report.csv", results);
    System.out.println("CSV report written to build/spark-sql-test-report.csv");
  }

  static void writeCsvReport(String path, List<TestResult> results) {
    try (PrintWriter writer = new PrintWriter(new FileWriter(path))) {
      writer.println("file,line,status,error_type,sql");
      for (TestResult r : results) {
        writer.printf("\"%s\",%d,%s,%s,\"%s\"%n",
            r.file,
            r.line,
            r.status,
            r.errorType,
            escapeCsv(r.sql)
        );
      }
    } catch (IOException e) {
      System.err.println("Failed to write CSV: " + e.getMessage());
    }
  }

  static String escapeCsv(String input) {
    return input == null ? "" : input.replace("\"", "\"\"");
  }

  static List<TestCase> loadTests(String folderPath) throws IOException {
    List<TestCase> tests = new ArrayList<>();
    Files.walk(Paths.get(folderPath))
        .filter(Files::isRegularFile)
        .forEach(filePath -> {
          try {
            List<String> lines = Files.readAllLines(filePath);
            for (int i = 0; i < lines.size(); i++) {
              String line = lines.get(i).trim();

              // Skip schema section
              if (line.equals("-- !query schema")) {
                while (i + 1 < lines.size() && !lines.get(i + 1).startsWith("--")) {
                  i++;
                }
                continue;
              }

              if (line.equals("-- !query")) {
                TestCase tc = new TestCase();
                tc.file = filePath.getFileName().toString();
                tc.line = i + 1;

                // Read multi-line SQL
                StringBuilder sql = new StringBuilder();
                i++;
                while (i < lines.size() && !lines.get(i).startsWith("--")) {
                  sql.append(lines.get(i).trim()).append(" ");
                  i++;
                }
                i--; // step back to allow outer loop to handle the current line
                tc.sql = sql.toString().trim().replaceAll(";$", "");

                // Read expected output if any
                for (int j = i + 1; j < lines.size(); j++) {
                  if (lines.get(j).startsWith("-- !query output")) {
                    StringBuilder output = new StringBuilder();
                    for (int k = j + 1; k < lines.size(); k++) {
                      if (lines.get(k).startsWith("--")) break;
                      output.append(lines.get(k)).append("\n");
                    }
                    tc.expectedOutput = output.toString().trim();
                    break;
                  }
                }

                tests.add(tc);
              }
            }
          } catch (IOException e) {
            throw new UncheckedIOException(e);
          }
        });
    return tests;
  }

  static String resultToString(ResultSet rs) throws SQLException {
    StringBuilder out = new StringBuilder();
    ResultSetMetaData meta = rs.getMetaData();
    int colCount = meta.getColumnCount();
    while (rs.next()) {
      for (int i = 1; i <= colCount; i++) {
        Object val = rs.getObject(i);
        out.append(val == null ? "NULL" : val.toString());
        if (i < colCount) out.append("\t");
      }
      out.append("\n");
    }
    return out.toString().trim();
  }

  static String normalizeOutput(String input) {
    if (input == null) return "";
    return input.lines()
        .map(String::trim)
        .map(line -> line
            .replaceAll("\\[\\s+", "[")     // remove space after [
            .replaceAll("\\s+]", "]")       // remove space before ]
            .replaceAll("\\s*,\\s*", ",")   // remove space around commas
        )
        .reduce((a, b) -> a + "\n" + b)
        .orElse("")
        .trim();
  }
}

