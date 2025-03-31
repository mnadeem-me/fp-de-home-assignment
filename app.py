from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col

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

sensor_stream.writeStream \
    .outputMode("update") \
    .format("console").option("truncate", False)\
    .trigger(processingTime="5 seconds") \
    .start().awaitTermination()