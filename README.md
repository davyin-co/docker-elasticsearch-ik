# 介绍
ElasticSearch含有IK分词插件。基于官方elasticsearch镜像。

# docker-compose.yml

```
version: '2.2'
services:
  es01:
    image: zterry95/elasticsearch-ik:7.8.1
    container_name: es01
    environment:
      - node.name=es01
      - cluster.name=es-docker-cluster
      - cluster.initial_master_nodes=es01
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - esdata01:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
volumes:
  esdata01:
    driver: local

#networks:
#  default:
#    external:
#      name: proxy

```



# 相似项目

https://github.com/pipizhang/docker-elasticsearch-analysis-ik

