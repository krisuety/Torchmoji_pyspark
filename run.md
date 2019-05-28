## 1. zookeeper server
$KAFKA/bin/zookeeper-server-start.sh config/zookeeper.properties

## 2. kafka server
$KAFKA/bin/kafka-server-start.sh config/server.properties

## 3. emoji Topic
$KAFKA/bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic emoji

## 4. Consumer
$KAFKA/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic emoji --from-beginning

## 5. Twit
$KAFKA/bin/connect-standalone.sh connect-simple-source-standalone.properties twitter-source.properties

## 6. Flask
python moji_try.app

http://127.0.0.1:8050/

## 7. Spark submit
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 examples/count_moji.py


