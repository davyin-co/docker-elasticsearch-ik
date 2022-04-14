# https://github.com/elastic/elasticsearch-docker
FROM elasticsearch:8.1.2

# https://github.com/medcl/elasticsearch-analysis-ik/releases
ENV IK_RELEASE=https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.1.2/elasticsearch-analysis-ik-8.1.2.zip
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install --batch $IK_RELEASE
