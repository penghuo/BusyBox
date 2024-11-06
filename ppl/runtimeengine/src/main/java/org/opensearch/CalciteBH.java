package org.opensearch;

import com.google.common.collect.ImmutableMap;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;
import org.apache.calcite.adapter.csv.CsvSchemaFactory;
import org.apache.calcite.jdbc.CalciteConnection;
import org.apache.calcite.plan.RelOptUtil;
import org.apache.calcite.rel.RelNode;
import org.apache.calcite.schema.Schema;
import org.apache.calcite.schema.SchemaPlus;
import org.apache.calcite.sql.SqlNode;
import org.apache.calcite.tools.FrameworkConfig;
import org.apache.calcite.tools.Frameworks;
import org.apache.calcite.tools.Planner;
import org.apache.calcite.tools.RelConversionException;
import org.apache.calcite.tools.RelRunner;
import org.apache.calcite.tools.ValidationException;

public class CalciteBH {

  private Statement statement;
  private Connection connection;
  private SchemaPlus rootSchema;
  private String csvDir;

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
      this.csvDir = csvDir;
      connection = DriverManager.getConnection("jdbc:calcite:", info);
      CalciteConnection calciteConnection = connection.unwrap(CalciteConnection.class);
      statement = calciteConnection.createStatement();
      rootSchema = calciteConnection.getRootSchema();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public void runRelNode(String query) {
    try {
      // Step 1: Use the Planner to convert SQL to RelNode
      FrameworkConfig config = Frameworks.newConfigBuilder()
          .defaultSchema(rootSchema.getSubSchema("test"))
          .build();

      Planner planner = Frameworks.getPlanner(config);

      SqlNode parsedQuery = planner.parse(query);

      SqlNode validatedQuery = planner.validate(parsedQuery);

      RelNode relNode = planner.rel(validatedQuery).rel;

      RelRunner runner = connection.unwrap(RelRunner.class);

      try (ResultSet resultSet = runner.prepareStatement(relNode).executeQuery()) {
        while (resultSet.next()) {
          String name = resultSet.getString("name");
          int age = resultSet.getInt("age");
          System.out.println("Name: " + name + ", Age: " + age);
        }
      }
    } catch (ValidationException | RelConversionException e) {
      throw new RuntimeException("Error processing query", e);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public void run(String query) {
    try {
        ResultSet resultSet = statement.executeQuery(query);

        while (resultSet.next()) {
          String result = resultSet.getString(1) + ", " + resultSet.getInt(2);
          System.out.println(result);
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
