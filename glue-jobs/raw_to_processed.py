"""
AWS Glue ETL Job: Raw to Processed Layer
Converts raw CSV/JSON data to Parquet format with Snappy compression
Implements partitioning strategy and data quality checks
"""

import sys
from datetime import datetime
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    col, year, month, dayofmonth, hour, 
    to_timestamp, regexp_replace, trim,
    when, lit, round as spark_round
)
from pyspark.sql.types import DoubleType, IntegerType, TimestampType

args = getResolvedOptions(
    sys.argv,
    [
        'JOB_NAME',
        'DATABASE_NAME',
        'SOURCE_BUCKET',
        'TARGET_BUCKET'
    ]
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

logger = glueContext.get_logger()
logger.info(f"Starting job: {args['JOB_NAME']}")
logger.info(f"Processing data from: s3://{args['SOURCE_BUCKET']}/raw/")

database_name = args['DATABASE_NAME']
source_bucket = args['SOURCE_BUCKET']
target_bucket = args['TARGET_BUCKET']

source_path = f"s3://{source_bucket}/raw/taxi_trips/"
target_path = f"s3://{target_bucket}/processed/taxi_trips/"

try:
    logger.info("Reading raw data from S3")
    
    # Read raw data using Glue DynamicFrame with job bookmarks
    datasource = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [source_path],
            "recurse": True
        },
        format="csv",
        format_options={
            "withHeader": True,
            "separator": ","
        },
        transformation_ctx="datasource"
    )
    
    if datasource.count() == 0:
        logger.warn("No new data to process")
        job.commit()
        sys.exit(0)
    
    logger.info(f"Read {datasource.count()} records from raw layer")
    
    # Convert to Spark DataFrame for transformations
    df = datasource.toDF()
    
    logger.info("Applying data transformations and quality checks")
    
    # Data Cleansing and Transformation
    df_cleaned = df \
        .withColumn("pickup_datetime", to_timestamp(col("tpep_pickup_datetime"))) \
        .withColumn("dropoff_datetime", to_timestamp(col("tpep_dropoff_datetime"))) \
        .withColumn("passenger_count", col("passenger_count").cast(IntegerType())) \
        .withColumn("trip_distance", col("trip_distance").cast(DoubleType())) \
        .withColumn("fare_amount", col("fare_amount").cast(DoubleType())) \
        .withColumn("tip_amount", col("tip_amount").cast(DoubleType())) \
        .withColumn("total_amount", col("total_amount").cast(DoubleType())) \
        .withColumn("payment_type", col("payment_type").cast(IntegerType()))
    
    # Data Quality Filters
    df_quality = df_cleaned.filter(
        (col("pickup_datetime").isNotNull()) &
        (col("dropoff_datetime").isNotNull()) &
        (col("passenger_count") > 0) &
        (col("passenger_count") <= 8) &
        (col("trip_distance") > 0) &
        (col("trip_distance") < 100) &
        (col("fare_amount") > 0) &
        (col("fare_amount") < 500) &
        (col("total_amount") > 0) &
        (col("pickup_datetime") < col("dropoff_datetime"))
    )
    
    # Add derived columns
    df_enriched = df_quality \
        .withColumn("trip_duration_minutes", 
                   (col("dropoff_datetime").cast("long") - col("pickup_datetime").cast("long")) / 60) \
        .withColumn("avg_speed_mph", 
                   when(col("trip_duration_minutes") > 0, 
                        spark_round((col("trip_distance") / col("trip_duration_minutes")) * 60, 2))
                   .otherwise(0)) \
        .withColumn("tip_percentage", 
                   when(col("fare_amount") > 0, 
                        spark_round((col("tip_amount") / col("fare_amount")) * 100, 2))
                   .otherwise(0))
    
    # Add partition columns
    df_partitioned = df_enriched \
        .withColumn("year", year(col("pickup_datetime"))) \
        .withColumn("month", month(col("pickup_datetime"))) \
        .withColumn("day", dayofmonth(col("pickup_datetime")))
    
    # Select final columns
    df_final = df_partitioned.select(
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "tip_amount",
        "total_amount",
        "payment_type",
        "trip_duration_minutes",
        "avg_speed_mph",
        "tip_percentage",
        "year",
        "month",
        "day"
    )
    
    logger.info(f"After quality checks: {df_final.count()} records")
    
    # Write to S3 in Parquet format with Snappy compression
    logger.info(f"Writing processed data to: {target_path}")
    
    df_final.write \
        .mode("append") \
        .partitionBy("year", "month", "day") \
        .option("compression", "snappy") \
        .parquet(target_path)
    
    logger.info("Successfully wrote data to processed layer")
    
    # Log statistics
    total_records = df_final.count()
    logger.info(f"Job Statistics:")
    logger.info(f"  Total records processed: {total_records}")
    logger.info(f"  Output format: Parquet with Snappy compression")
    logger.info(f"  Partitioning: year/month/day")
    
    job.commit()
    logger.info("Job completed successfully")

except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
