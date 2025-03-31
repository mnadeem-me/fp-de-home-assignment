# Sensor Window Aggregation with Apache Spark

This application, `app.py`, is a PySpark-based streaming application that reads sensor data from a Kafka topic, performs windowed aggregations, and writes the results back to another Kafka topic.

## Features

- Reads real-time sensor data from a Kafka topic (`sensor-input`).
- Parses JSON-encoded sensor data with fields: `sensorId`, `value`, and `timestamp`.
- Applies a watermark to handle late-arriving data.
- Performs windowed aggregations to calculate the average sensor value over 1-minute windows.
- Writes the aggregated results to a Kafka topic (`sensor-output`) in JSON format.

## Prerequisites

1. **Apache Kafka**: Ensure Kafka is running and accessible at `localhost:9092`.
2. **PySpark**: Install PySpark version compatible with your Spark cluster.
3. **Kafka Topic Setup**:
   - Input topic: `sensor-input`
   - Output topic: `sensor-output`
4. **Python Dependencies**: Install required Python libraries:
   ```bash
   pip install pyspark
## Application Workflow

1. **Input Stream**: Reads data from the Kafka topic sensor-input.
2. **Schema Definition**: Defines the schema for the incoming JSON data.
3. **Data Transformation**:
    - Parses the JSON data.
    - Converts the timestamp field to a proper timestamp type.
    - Applies a watermark to handle late data.
4. **Windowed Aggregation**:
    - Groups data by `sensorId` and 1-minute time windows.
    - Calculates the average value for each sensor within the window.
5. **Output Stream**: Writes the aggregated results to the Kafka topic `sensor-output`.

## Running the Application
1. Initiate Kafka Producer and Topics
    - Run following command:
    ```bash
    docker compose up --build -d
2. Check the Kafka UI at http://localhost:8080/ui/docker-kafka-server/topic
3. Verify `sensor-input` topic with messages from the producer
4. Run the spark application:
    ```bash
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 app.py