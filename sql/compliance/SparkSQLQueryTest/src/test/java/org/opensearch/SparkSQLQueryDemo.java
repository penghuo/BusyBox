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
        "create view t as select * from (values (0), (1), (2)) as t(id)",
        "create view t2 as select * from (values (0), (1)) as t(id)",
        "WITH t(x, x) AS (SELECT 1, 2) SELECT * FROM t"
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
