package org.opensearch;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;
import org.apache.calcite.jdbc.CalciteConnection;

public class CalciteBH {

  private Statement statement;
  private Connection connection;

  public CalciteBH(String csvDir) {
    Properties info = new Properties();
    info.put("model", "inline:"
        + "{\n"
        + "  \"version\": \"1.0\",\n"
        + "  \"defaultSchema\": \"test\",\n"
        + "  \"schemas\": [\n"
        + "    {\n"
        + "      \"name\": \"test\",\n"
        + "      \"type\": \"custom\",\n"
        + "      \"factory\": \"org.apache.calcite.adapter.csv.CsvSchemaFactory\",\n"
        + "      \"operand\": {\n"
        + "        \"directory\": \"" + csvDir + "\",\n"
        + "        \"flavor\": \"scannable\"\n"
        + "      }\n"
        + "    }\n"
        + "  ]\n"
        + "}");

    try {
      connection = DriverManager.getConnection("jdbc:calcite:", info);
      CalciteConnection calciteConnection = connection.unwrap(CalciteConnection.class);
      statement = calciteConnection.createStatement();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public void run(String query) {
    try {
        ResultSet resultSet = statement.executeQuery(query);

        while (resultSet.next()) {
          String result = resultSet.getString(1) + ", " + resultSet.getInt(2);
        }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public void clean() {
    try {
      connection.close();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }
}
