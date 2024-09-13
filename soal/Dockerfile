# Use EMR Spark as the base image
FROM public.ecr.aws/emr-serverless/spark/emr-7.2.0:latest as spark-base

# Build stage using the original base image
FROM public.ecr.aws/amazoncorretto/amazoncorretto:11 as build

# Install maven
RUN yum install -y maven
WORKDIR /src

# Cache and copy dependencies
ADD pom.xml .
RUN mvn dependency:go-offline dependency:copy-dependencies

# Compile the function
ADD . .
RUN mvn package

# Use the Spark base image as the final base
FROM spark-base

USER root
RUN rm -rf /home/hadoop
RUN mkdir -p /tmp/home/hadoop
RUN usermod -d /tmp/home/hadoop hadoop
RUN sed -i 's|^HOME=.*|HOME=/tmp/home|' /etc/default/useradd

# Set the working directory
WORKDIR /usr/lib/spark/jars/

# Copy built artifacts from the build stage
COPY --from=build /src/target/dependency/*.jar ./
COPY --from=build /src/target/*.jar ./
COPY src/lib/hive-site.xml /etc/spark/conf/

ENV AWS_REGION=us-west-2

ENTRYPOINT ["/usr/bin/java", "-Daws.region=us-west-2", "-Daws.glue.endpoint=glue.us-west-2.amazonaws.com", "-Djava.library.path=/usr/lib/hadoop/lib/native:/usr/lib/hadoop-lzo/lib/native:/usr/java/packages/lib:/usr/lib64:/lib64:/lib:/usr/lib", "-Djava.net.preferIPv6Addresses=false", "-XX:OnOutOfMemoryError=kill -9 %p", "-XX:+IgnoreUnrecognizedVMOptions", "--add-opens", "java.base/java.lang=ALL-UNNAMED", "--add-opens", "java.base/java.lang.invoke=ALL-UNNAMED", "--add-opens", "java.base/java.lang.reflect=ALL-UNNAMED", "--add-opens", "java.base/java.io=ALL-UNNAMED", "--add-opens", "java.base/java.net=ALL-UNNAMED", "--add-opens", "java.base/java.nio=ALL-UNNAMED", "--add-opens", "java.base/java.util=ALL-UNNAMED", "--add-opens", "java.base/java.util.concurrent=ALL-UNNAMED", "--add-opens", "java.base/java.util.concurrent.atomic=ALL-UNNAMED", "--add-opens", "java.base/jdk.internal.ref=ALL-UNNAMED", "--add-opens", "java.base/sun.nio.ch=ALL-UNNAMED", "--add-opens", "java.base/sun.nio.cs=ALL-UNNAMED", "--add-opens", "java.base/sun.security.action=ALL-UNNAMED", "--add-opens", "java.base/sun.util.calendar=ALL-UNNAMED", "--add-opens", "java.security.jgss/sun.security.krb5=ALL-UNNAMED", "-Djdk.reflect.useDirectMethodHandle=false", "-XX:UseAVX=2", "-cp", "./*:/usr/lib/livy/rsc-jars/*:/usr/lib/livy/repl_2.12-jars/*:/usr/lib/hadoop-lzo/lib/*:/usr/lib/hadoop/hadoop-aws.jar:/usr/share/aws/aws-java-sdk/*:/usr/share/aws/emr/emrfs/conf:/usr/share/aws/emr/emrfs/lib/*:/usr/share/aws/emr/emrfs/auxlib/*:/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/usr/share/aws/emr/goodies/lib/emr-serverless-spark-goodies.jar:/usr/share/aws/emr/security/conf:/usr/share/aws/emr/security/lib/*:/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/docker/usr/lib/hadoop-lzo/lib/*:/docker/usr/lib/hadoop/hadoop-aws.jar:/docker/usr/share/aws/aws-java-sdk/*:/docker/usr/share/aws/emr/emrfs/conf:/docker/usr/share/aws/emr/emrfs/lib/*:/docker/usr/share/aws/emr/emrfs/auxlib/*:/docker/usr/share/aws/emr/goodies/lib/emr-spark-goodies.jar:/docker/usr/share/aws/emr/security/conf:/docker/usr/share/aws/emr/security/lib/*:/docker/usr/share/aws/hmclient/lib/aws-glue-datacatalog-spark-client.jar:/docker/usr/share/java/Hive-JSON-Serde/hive-openx-serde.jar:/docker/usr/share/aws/sagemaker-spark-sdk/lib/sagemaker-spark-sdk.jar:/docker/usr/share/aws/emr/s3select/lib/emr-s3-select-spark-connector.jar:/usr/share/aws/redshift/jdbc/RedshiftJDBC.jar:/usr/share/aws/redshift/spark-redshift/lib/*:/usr/share/aws/iceberg/lib/iceberg-emr-common.jar:/usr/share/aws/iceberg/lib/iceberg-spark3-runtime.jar", "com.amazonaws.services.lambda.runtime.api.client.AWSLambda"]


# Pass the name of the function handler as an argument to the runtime
CMD [ "example.LambdaHandler::handleRequest" ]