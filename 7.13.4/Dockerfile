# https://github.com/elastic/elasticsearch-docker
FROM elasticsearch:7.13.4

# https://github.com/medcl/elasticsearch-analysis-ik/releases
ENV IK_RELEASE=https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.13.4/elasticsearch-analysis-ik-7.13.4.zip
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch $IK_RELEASE
## update log4j to 2.15.0 for security.
RUN rm /usr/share/elasticsearch/lib/log4j-core-2.11.1.jar \
    /usr/share/elasticsearch/lib/log4j-api-2.11.1.jar \
    /usr/share/elasticsearch/modules/x-pack-core/log4j-1.2-api-2.11.1.jar \
    /usr/share/elasticsearch/modules/repository-url/log4j-1.2-api-2.11.1.jar \
    /usr/share/elasticsearch/modules/x-pack-identity-provider/log4j-slf4j-impl-2.11.1.jar \
    /usr/share/elasticsearch/modules/x-pack-security/log4j-slf4j-impl-2.11.1.jar && \ 
    curl -L https://downloads.apache.org/logging/log4j/2.15.0/apache-log4j-2.15.0-bin.tar.gz -o /tmp/log4j.tgz && \
    cd /tmp/ && \
    tar xzvf log4j.tgz && \
    cp /tmp/apache-log4j-2.15.0-bin/log4j-core-2.15.0.jar /tmp/apache-log4j-2.15.0-bin/log4j-api-2.15.0.jar /usr/share/elasticsearch/lib/ && \
    cp /tmp/apache-log4j-2.15.0-bin/log4j-1.2-api-2.15.0.jar  /usr/share/elasticsearch/modules/x-pack-core/ && \
    cp /tmp/apache-log4j-2.15.0-bin/log4j-1.2-api-2.15.0.jar   /usr/share/elasticsearch/modules/repository-url/ && \
    cp /tmp/apache-log4j-2.15.0-bin/log4j-slf4j-impl-2.15.0.jar  /usr/share/elasticsearch/modules/x-pack-identity-provider/ && \
    cp /tmp/apache-log4j-2.15.0-bin/log4j-slf4j-impl-2.15.0.jar /usr/share/elasticsearch/modules/x-pack-security/ && \
    rm -rf  /tmp/apache-log4j-2.15.0-bin && rm /tmp/log4j.tgz
