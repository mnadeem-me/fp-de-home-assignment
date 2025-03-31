from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, round, to_json, struct

spark = SparkSession.builder.appName("SensorWindowAggregation").getOrCreate()

spark.sparkContext.setLogLevel("WARN")

input_kakfa_stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "sensor-input") \
    .option("startingOffsets", "latest") \
    .load()

schema = "sensorId STRING, value DOUBLE, timestamp STRING"

data_stream = input_kakfa_stream.selectExpr("CAST(value AS STRING) as data") \
    .select(from_json("data", schema).alias("data")).select("data.*")

sensor_stream = data_stream.select(
    col("timestamp").cast("long").alias("timestamp"), col("value"), col("sensorId").alias("sensorId")
)

watermarked_stream = sensor_stream.withColumn("event_time", (col("timestamp") / 1000).cast("timestamp")) \
    .withWatermark("event_time", "1 minute")

agg_stream = watermarked_stream.groupBy(
    col("sensorId"),
    window(col("event_time"), "1 minute")
).agg(round(avg("value")).alias("averageValue"))

result_stream = agg_stream.select(
    col("sensorId"),
    (col("window.start").cast("long") * 1000).alias("windowStart"),
    (col("window.end").cast("long") * 1000).alias("windowEnd"),
    col("averageValue")
)

output_stream = result_stream.select(to_json(struct("sensorId", "windowStart", "windowEnd", "averageValue")).alias("value"))

output_stream.writeStream \
    .outputMode("update") \
    .format("console").option("truncate", False)\
    .trigger(processingTime="1 minute") \
    .start().awaitTermination()