FROM public.ecr.aws/emr-serverless/spark/emr-7.2.0:latest

USER root
# Install OpenSearch 2.15.0
RUN yum install -y unzip wget tar && \
    wget https://artifacts.opensearch.org/releases/bundle/opensearch/2.15.0/opensearch-2.15.0-linux-x64.tar.gz && \
    tar -xzf opensearch-2.15.0-linux-x64.tar.gz && \
    mv opensearch-2.15.0 /usr/local/opensearch

RUN rm -rf /usr/local/opensearch/plugins/*    

COPY lib/opensearch.yml /usr/local/opensearch/config/opensearch.yml
COPY lib/repository-s3-2.15.1-SNAPSHOT.zip /tmp/repository-s3.zip
COPY lib/jvm.options /usr/local/opensearch/config/jvm.options

RUN unzip /tmp/repository-s3.zip -d /usr/local/opensearch/plugins/repository-s3 && \
    rm /tmp/repository-s3.zip
RUN chmod 644 /usr/local/opensearch/config/opensearch.yml

COPY lib/plugin-descriptor.properties /usr/local/opensearch/plugins/repository-s3/plugin-descriptor.properties

RUN chmod 777 /usr/local/opensearch/config/jvm.options
RUN chmod 777 /usr/local/opensearch/config/
RUN chmod 777 /usr/local/opensearch

ENV OPENSEARCH_HOME=/usr/local/opensearch
ENV OPENSEARCH_JAVA_HOME=/usr/local/opensearch/jdk
ENV OPENSEARCH_PATH_CONF=/usr/local/opensearch/config

COPY lib/entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

USER hadoop