# 介绍
ElasticSearch含有IK分词插件。基于官方elasticsearch镜像。
## Using 7.16.2 或以上版本，修复了log4j2的安全漏洞；7.16.2以下版本风险自担。

# docker-compose.yml

```
version: '3'
services:
  es01:
    image: davyinsa/elasticsearch-ik:7.16.1
    container_name: es01
    environment:
      - discovery.type=single-node
      - node.name=es01
      - cluster.name=es-docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=password
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - ./es01:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
```
# 变量说明
  - ELASTIC_PASSWORD的默认对应的默认用户名为：elastic

# max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```
# vim /etc/sysctl.conf 追加以下内容：
vm.max_map_count=655360
# 保存后，执行：
sysctl -p
```

# elasticsearch docker release
https://hub.docker.com/_/elasticsearch?tab=tags&page=1&ordering=last_updated

# 相似项目
https://github.com/pipizhang/docker-elasticsearch-analysis-ik

