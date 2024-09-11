name := "SQLJob"
version := "1.0"
scalaVersion := "2.12.15"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.5.1" % "provided",
  "org.apache.spark" %% "spark-sql" % "3.5.1" % "provided"
)

// Assembly settings
assemblyJarName in assembly := s"${name.value}-${version.value}.jar"
mainClass in assembly := Some("org.apache.spark.SQLJob")

// Merge strategy for assembly
assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}