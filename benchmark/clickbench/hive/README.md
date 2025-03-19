## setup
* download hive and hadoop
```
/home/ec2-user/hive/apache-hive-3.1.3-bin
/home/ec2-user/hadoop/hadoop-3.3.6
```

* hive-site.xml
  * [ec2-user@ip-172-31-0-95 apache-hive-3.1.3-bin]$ cat conf/hive-site.xml
```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <!-- Derby Metastore Configuration -->
  <property>
    <name>javax.jdo.option.ConnectionURL</name>
    <value>jdbc:derby:;databaseName=/home/ec2-user/hive/apache-hive-3.1.3-bin/metastore_db;create=true</value>
    <description>Path to Derby metastore database</description>
  </property>
  <property>
    <name>javax.jdo.option.ConnectionDriverName</name>
    <value>org.apache.derby.jdbc.EmbeddedDriver</value>
    <description>Derby JDBC driver class</description>
  </property>

  <!-- Hive Warehouse Directory -->
  <property>
    <name>hive.metastore.warehouse.dir</name>
    <value>file:///home/ec2-user/hive/warehouse</value>
    <description>Local directory for Hive table data</description>
  </property>

  <!-- Metastore Configuration -->
  <property>
    <name>hive.metastore.uris</name>
    <value>thrift://localhost:9083</value>
    <description>Thrift URI for Hive metastore</description>
  </property>
  <property>
    <name>hive.metastore.local</name>
    <value>false</value>
    <description>Disable local metastore mode</description>
  </property>

  <!-- Schema Validation -->
  <property>
    <name>hive.metastore.schema.verification</name>
    <value>false</value>
    <description>Disable schema validation (for testing)</description>
  </property>

  <!-- Hive Security (for testing) -->
  <property>
    <name>hive.security.authorization.enabled</name>
    <value>false</value>
    <description>Disable authorization for testing</description>
  </property>
  <property>
    <name>hive.security.metastore.authorization.manager</name>
    <value>org.apache.hadoop.hive.ql.security.authorization.StorageBasedAuthorizationProvider</value>
  </property>

  <!-- Hive Server2 (Optional) -->
  <property>
    <name>hive.server2.thrift.port</name>
    <value>10000</value>
    <description>Port for Hive Server2</description>
  </property>
  <property>
    <name>hive.server2.thrift.bind.host</name>
    <value>localhost</value>
  </property>

  <!-- Scratch Directory -->
  <property>
    <name>hive.exec.scratchdir</name>
    <value>/tmp/hive-${user.name}</value>
    <description>Temporary directory for Hive jobs</description>
  </property>

  <!-- JSON Support -->
  <property>
    <name>hive.support.concurrency</name>
    <value>false</value>
    <description>Disable concurrency for JSON tables</description>
  </property>
  <property>
    <name>hive.txn.manager</name>
    <value>org.apache.hadoop.hive.ql.lockmgr.DummyTxnManager</value>
  </property>
</configuration>
```