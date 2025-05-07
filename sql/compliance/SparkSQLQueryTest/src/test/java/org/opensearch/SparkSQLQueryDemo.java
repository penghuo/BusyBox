package org.opensearch;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Arrays;
import java.util.List;

public class SparkSQLQueryDemo {

  public static void main(String[] args) throws Exception {
    String modelPath = "src/test/resources/model.json";
    String
        url =
        "jdbc:calcite:model=" + modelPath + ";conformance=BABEL;fun=standard,spark;lenientOperatorLookup=true;parserFactory=org.apache.calcite.server.ServerDdlExecutor#PARSER_FACTORY";

    List<String> queries = Arrays.asList(
        "create view data as select * from (values\n" + "  ('one', array[11, 12, 13], array[array[111, 112, 113], array[121, 122, 123]]),\n" + "  ('two', array[21, 22, 23], array[array[211, 212, 213], array[221, 222, 223]]))\n" + "  as data(a, b, c)",
        "select b from data",
        "select a, b[0], b[0] + b[1] from data"
    );

    try (
        Connection conn = DriverManager.getConnection(url, "admin", "admin"); Statement stmt = conn.createStatement()) {

      for (String sql : queries) {
        SparkSQLQueryTest.TestResult result = new SparkSQLQueryTest.TestResult();
        try {
          ResultSet rs = stmt.executeQuery(sql);
          System.out.println(resultToString(rs));
        } catch (SQLException e) {
          String errorMsg = e.getMessage();
          System.out.println(errorMsg);
        }
      }
    }
  }

  static String resultToString(ResultSet rs) throws SQLException {
    StringBuilder out = new StringBuilder();
    ResultSetMetaData meta = rs.getMetaData();
    int colCount = meta.getColumnCount();
    while (rs.next()) {
      for (int i = 1; i <= colCount; i++) {
        Object val = rs.getObject(i);
        out.append(val == null ? "NULL" : val.toString());
        if (i < colCount) {out.append("\t");}
      }
      out.append("\n");
    }
    return out.toString().trim();
  }
}
