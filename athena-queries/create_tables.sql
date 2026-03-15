-- ============================================
-- Athena DDL Queries for Data Lake Tables
-- ============================================

-- Note: These tables are typically created automatically by Glue Crawlers
-- Use these DDL statements for manual table creation or reference

-- ============================================
-- 1. Raw Layer - Taxi Trips Table
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS raw_taxi_trips (
    tpep_pickup_datetime STRING,
    tpep_dropoff_datetime STRING,
    passenger_count INT,
    trip_distance DOUBLE,
    pickup_longitude DOUBLE,
    pickup_latitude DOUBLE,
    rate_code_id INT,
    store_and_fwd_flag STRING,
    dropoff_longitude DOUBLE,
    dropoff_latitude DOUBLE,
    payment_type INT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://YOUR-BUCKET-NAME/raw/taxi_trips/'
TBLPROPERTIES (
    'skip.header.line.count'='1',
    'classification'='csv'
);

-- ============================================
-- 2. Processed Layer - Taxi Trips Table
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS processed_taxi_trips (
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count INT,
    trip_distance DOUBLE,
    fare_amount DOUBLE,
    tip_amount DOUBLE,
    total_amount DOUBLE,
    payment_type INT,
    trip_duration_minutes DOUBLE,
    avg_speed_mph DOUBLE,
    tip_percentage DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT,
    day INT
)
STORED AS PARQUET
LOCATION 's3://YOUR-BUCKET-NAME/processed/taxi_trips/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'projection.enabled'='true',
    'projection.year.type'='integer',
    'projection.year.range'='2020,2030',
    'projection.month.type'='integer',
    'projection.month.range'='1,12',
    'projection.day.type'='integer',
    'projection.day.range'='1,31',
    'storage.location.template'='s3://YOUR-BUCKET-NAME/processed/taxi_trips/year=${year}/month=${month}/day=${day}'
);

-- ============================================
-- 3. Curated Layer - Daily Trip Statistics
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS curated_daily_trip_statistics (
    pickup_date DATE,
    day INT,
    total_trips BIGINT,
    total_revenue DOUBLE,
    total_tips DOUBLE,
    avg_trip_distance DOUBLE,
    avg_trip_duration DOUBLE,
    avg_passengers DOUBLE,
    avg_tip_percentage DOUBLE,
    max_fare DOUBLE,
    min_fare DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION 's3://YOUR-BUCKET-NAME/curated/daily_trip_statistics/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'projection.enabled'='true',
    'projection.year.type'='integer',
    'projection.year.range'='2020,2030',
    'projection.month.type'='integer',
    'projection.month.range'='1,12',
    'storage.location.template'='s3://YOUR-BUCKET-NAME/curated/daily_trip_statistics/year=${year}/month=${month}'
);

-- ============================================
-- 4. Curated Layer - Hourly Trip Patterns
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS curated_hourly_trip_patterns (
    pickup_hour INT,
    pickup_day_of_week INT,
    day_name STRING,
    trip_count BIGINT,
    avg_distance DOUBLE,
    avg_duration DOUBLE,
    avg_fare DOUBLE,
    avg_passengers DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION 's3://YOUR-BUCKET-NAME/curated/hourly_trip_patterns/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'projection.enabled'='true',
    'projection.year.type'='integer',
    'projection.year.range'='2020,2030',
    'projection.month.type'='integer',
    'projection.month.range'='1,12',
    'storage.location.template'='s3://YOUR-BUCKET-NAME/curated/hourly_trip_patterns/year=${year}/month=${month}'
);

-- ============================================
-- 5. Curated Layer - Payment Type Analysis
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS curated_payment_type_analysis (
    payment_type INT,
    payment_method STRING,
    transaction_count BIGINT,
    total_revenue DOUBLE,
    avg_tip_percentage DOUBLE,
    avg_fare DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION 's3://YOUR-BUCKET-NAME/curated/payment_type_analysis/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'projection.enabled'='true',
    'projection.year.type'='integer',
    'projection.year.range'='2020,2030',
    'projection.month.type'='integer',
    'projection.month.range'='1,12',
    'storage.location.template'='s3://YOUR-BUCKET-NAME/curated/payment_type_analysis/year=${year}/month=${month}'
);

-- ============================================
-- 6. Curated Layer - Distance Distribution
-- ============================================

CREATE EXTERNAL TABLE IF NOT EXISTS curated_distance_distribution (
    distance_bucket STRING,
    trip_count BIGINT,
    avg_fare DOUBLE,
    avg_duration DOUBLE,
    total_revenue DOUBLE
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION 's3://YOUR-BUCKET-NAME/curated/distance_distribution/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'projection.enabled'='true',
    'projection.year.type'='integer',
    'projection.year.range'='2020,2030',
    'projection.month.type'='integer',
    'projection.month.range'='1,12',
    'storage.location.template'='s3://YOUR-BUCKET-NAME/curated/distance_distribution/year=${year}/month=${month}'
);

-- ============================================
-- Repair Partitions (Run after data loads)
-- ============================================

MSCK REPAIR TABLE processed_taxi_trips;
MSCK REPAIR TABLE curated_daily_trip_statistics;
MSCK REPAIR TABLE curated_hourly_trip_patterns;
MSCK REPAIR TABLE curated_payment_type_analysis;
MSCK REPAIR TABLE curated_distance_distribution;
