from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, from_json, round, struct, to_json, window

# Initialize Spark session
spark = SparkSession.builder.appName("SensorWindowAggregation").getOrCreate()

spark.sparkContext.setLogLevel("WARN")  # Set log level to reduce verbosity

# Configure Kafka input stream to read from 'sensor-input' topic
input_kakfa_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "sensor-input")
    .option("startingOffsets", "latest")  # Read only new messages
    .load()
)

# Define schema for parsing Kafka messages
schema = "sensorId STRING, value DOUBLE, timestamp STRING"

# Parse Kafka messages and extract fields based on the schema
sensor_stream = (
    input_kakfa_stream.selectExpr("CAST(value AS STRING) as data")
    .select(from_json("data", schema).alias("data"))
    .select("data.*")
)

# Apply watermarking to handle late data with a 1-minute threshold
watermarked_stream = sensor_stream.withColumn(
    "event_time", (col("timestamp").cast("long") / 1000).cast("timestamp")
).withWatermark("event_time", "1 minute")

# Perform aggregation: calculate average value in 1-minute windows
agg_stream = watermarked_stream.groupBy(
    col("sensorId"), window(col("event_time"), "1 minute")
).agg(round(avg("value")).alias("averageValue"))

# Select and format the result stream for output
result_stream = agg_stream.select(
    col("sensorId"),
    (col("window.start").cast("long") * 1000).alias("windowStart"),
    (col("window.end").cast("long") * 1000).alias("windowEnd"),
    col("averageValue"),
)

# Format the result stream to json structure
output_stream = result_stream.select(
    to_json(struct("sensorId", "windowStart", "windowEnd", "averageValue")).alias("value")
)

# Write the output stream to Kafka topic 'sensor-output'
output_stream.writeStream.outputMode("update").option(
    "checkpointLocation", f"C:\\Users\\Nadeem\\Downloads\\fp-de-home-assignment\\KAFKA_CP"
).format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option(
    "topic", "sensor-output"
).trigger(
    processingTime="1 minute"
).start().awaitTermination()
