"""
AWS Glue ETL Job: Processed to Curated Layer
Creates analytics-ready aggregated tables for business intelligence
Generates multiple analytical views optimized for different use cases
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    col, sum as spark_sum, avg, count, max as spark_max, min as spark_min,
    round as spark_round, when, hour, dayofweek, date_format
)
from pyspark.sql.window import Window

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

database_name = args['DATABASE_NAME']
source_bucket = args['SOURCE_BUCKET']
target_bucket = args['TARGET_BUCKET']

source_path = f"s3://{source_bucket}/processed/taxi_trips/"
target_base_path = f"s3://{target_bucket}/curated/"

try:
    logger.info("Reading processed data from S3")
    
    # Read processed Parquet data
    df = spark.read.parquet(source_path)
    
    if df.count() == 0:
        logger.warn("No data to process in curated layer")
        job.commit()
        sys.exit(0)
    
    logger.info(f"Read {df.count()} records from processed layer")
    
    # Add time-based dimensions
    df_enriched = df \
        .withColumn("pickup_hour", hour(col("pickup_datetime"))) \
        .withColumn("pickup_day_of_week", dayofweek(col("pickup_datetime"))) \
        .withColumn("pickup_date", date_format(col("pickup_datetime"), "yyyy-MM-dd"))
    
    # Analytics Table 1: Daily Trip Statistics
    logger.info("Creating daily trip statistics table")
    
    daily_stats = df_enriched.groupBy("year", "month", "day", "pickup_date") \
        .agg(
            count("*").alias("total_trips"),
            spark_sum("fare_amount").alias("total_revenue"),
            spark_sum("tip_amount").alias("total_tips"),
            avg("trip_distance").alias("avg_trip_distance"),
            avg("trip_duration_minutes").alias("avg_trip_duration"),
            avg("passenger_count").alias("avg_passengers"),
            avg("tip_percentage").alias("avg_tip_percentage"),
            spark_max("fare_amount").alias("max_fare"),
            spark_min("fare_amount").alias("min_fare")
        ) \
        .withColumn("avg_trip_distance", spark_round(col("avg_trip_distance"), 2)) \
        .withColumn("avg_trip_duration", spark_round(col("avg_trip_duration"), 2)) \
        .withColumn("avg_passengers", spark_round(col("avg_passengers"), 2)) \
        .withColumn("avg_tip_percentage", spark_round(col("avg_tip_percentage"), 2)) \
        .withColumn("total_revenue", spark_round(col("total_revenue"), 2)) \
        .withColumn("total_tips", spark_round(col("total_tips"), 2))
    
    daily_stats_path = f"{target_base_path}daily_trip_statistics/"
    daily_stats.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .option("compression", "snappy") \
        .parquet(daily_stats_path)
    
    logger.info(f"Wrote daily statistics to: {daily_stats_path}")
    
    # Analytics Table 2: Hourly Trip Patterns
    logger.info("Creating hourly trip patterns table")
    
    hourly_patterns = df_enriched.groupBy("year", "month", "pickup_hour", "pickup_day_of_week") \
        .agg(
            count("*").alias("trip_count"),
            avg("trip_distance").alias("avg_distance"),
            avg("trip_duration_minutes").alias("avg_duration"),
            avg("fare_amount").alias("avg_fare"),
            avg("passenger_count").alias("avg_passengers")
        ) \
        .withColumn("avg_distance", spark_round(col("avg_distance"), 2)) \
        .withColumn("avg_duration", spark_round(col("avg_duration"), 2)) \
        .withColumn("avg_fare", spark_round(col("avg_fare"), 2)) \
        .withColumn("avg_passengers", spark_round(col("avg_passengers"), 2)) \
        .withColumn("day_name", 
                   when(col("pickup_day_of_week") == 1, "Sunday")
                   .when(col("pickup_day_of_week") == 2, "Monday")
                   .when(col("pickup_day_of_week") == 3, "Tuesday")
                   .when(col("pickup_day_of_week") == 4, "Wednesday")
                   .when(col("pickup_day_of_week") == 5, "Thursday")
                   .when(col("pickup_day_of_week") == 6, "Friday")
                   .when(col("pickup_day_of_week") == 7, "Saturday"))
    
    hourly_patterns_path = f"{target_base_path}hourly_trip_patterns/"
    hourly_patterns.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .option("compression", "snappy") \
        .parquet(hourly_patterns_path)
    
    logger.info(f"Wrote hourly patterns to: {hourly_patterns_path}")
    
    # Analytics Table 3: Payment Type Analysis
    logger.info("Creating payment type analysis table")
    
    payment_analysis = df_enriched.groupBy("year", "month", "payment_type") \
        .agg(
            count("*").alias("transaction_count"),
            spark_sum("total_amount").alias("total_revenue"),
            avg("tip_percentage").alias("avg_tip_percentage"),
            avg("fare_amount").alias("avg_fare")
        ) \
        .withColumn("total_revenue", spark_round(col("total_revenue"), 2)) \
        .withColumn("avg_tip_percentage", spark_round(col("avg_tip_percentage"), 2)) \
        .withColumn("avg_fare", spark_round(col("avg_fare"), 2)) \
        .withColumn("payment_method",
                   when(col("payment_type") == 1, "Credit Card")
                   .when(col("payment_type") == 2, "Cash")
                   .when(col("payment_type") == 3, "No Charge")
                   .when(col("payment_type") == 4, "Dispute")
                   .otherwise("Unknown"))
    
    payment_analysis_path = f"{target_base_path}payment_type_analysis/"
    payment_analysis.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .option("compression", "snappy") \
        .parquet(payment_analysis_path)
    
    logger.info(f"Wrote payment analysis to: {payment_analysis_path}")
    
    # Analytics Table 4: Trip Distance Distribution
    logger.info("Creating trip distance distribution table")
    
    distance_distribution = df_enriched \
        .withColumn("distance_bucket",
                   when(col("trip_distance") < 1, "0-1 miles")
                   .when(col("trip_distance") < 3, "1-3 miles")
                   .when(col("trip_distance") < 5, "3-5 miles")
                   .when(col("trip_distance") < 10, "5-10 miles")
                   .when(col("trip_distance") < 20, "10-20 miles")
                   .otherwise("20+ miles")) \
        .groupBy("year", "month", "distance_bucket") \
        .agg(
            count("*").alias("trip_count"),
            avg("fare_amount").alias("avg_fare"),
            avg("trip_duration_minutes").alias("avg_duration"),
            spark_sum("total_amount").alias("total_revenue")
        ) \
        .withColumn("avg_fare", spark_round(col("avg_fare"), 2)) \
        .withColumn("avg_duration", spark_round(col("avg_duration"), 2)) \
        .withColumn("total_revenue", spark_round(col("total_revenue"), 2))
    
    distance_distribution_path = f"{target_base_path}distance_distribution/"
    distance_distribution.write \
        .mode("overwrite") \
        .partitionBy("year", "month") \
        .option("compression", "snappy") \
        .parquet(distance_distribution_path)
    
    logger.info(f"Wrote distance distribution to: {distance_distribution_path}")
    
    # Log final statistics
    logger.info("Job Statistics:")
    logger.info(f"  Tables created: 4")
    logger.info(f"  - Daily Trip Statistics")
    logger.info(f"  - Hourly Trip Patterns")
    logger.info(f"  - Payment Type Analysis")
    logger.info(f"  - Trip Distance Distribution")
    logger.info(f"  Output format: Parquet with Snappy compression")
    logger.info(f"  Partitioning: year/month")
    
    job.commit()
    logger.info("Job completed successfully")

except Exception as e:
    logger.error(f"Job failed with error: {str(e)}")
    raise e
