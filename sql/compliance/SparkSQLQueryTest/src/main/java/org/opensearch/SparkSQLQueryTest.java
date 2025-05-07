package org.opensearch;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class SparkSQLQueryTest {
  public static void main(String[] args) {
    System.out.println("Run Spark SQL Compliance Test");

    query("select ifnull(null, 1)");
  }

  public static void query(String sql) {
    String modelPath = "src/main/resources/model.json"; // Update to your actual path
    String url = "jdbc:calcite:model=" + modelPath +
        ";conformance=BABEL;fun=spark;lenientOperatorLookup=true";

    try (
        Connection conn = DriverManager.getConnection(url, "admin", "admin");
        Statement stmt = conn.createStatement()) {
      ResultSet rs = stmt.executeQuery(sql);

      while (rs.next()) {
        System.out.println("Result: " + rs.getObject(1));
      }

    } catch (SQLException e) {
      e.printStackTrace();
    }
  }
}
