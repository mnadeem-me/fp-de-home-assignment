def write_to_mongodb(batch_df, batch_id):
    batch_df.selectExpr(
        "sensorId as sensor_id",
        "CAST(windowStart/1000 AS TIMESTAMP) as window_start",
        "CAST(windowEnd/1000 AS TIMESTAMP) as window_end",
        "averageValue as average_value",
    ).write.format("mongodb").option(
        "spark.mongodb.write.connection.uri", "mongodb://localhost:27017"
    ).option(
        "spark.mongodb.write.database", "sensors"
    ).option(
        "spark.mongodb.write.collection", "sensor_aggregates_ts"
    ).mode(
        "append"
    ).save()
