-- ============================================
-- Athena Analytics Queries
-- Sample queries for data analysis and validation
-- ============================================

-- ============================================
-- 1. Daily Revenue Trends
-- ============================================

SELECT 
    pickup_date,
    total_trips,
    total_revenue,
    total_tips,
    ROUND(total_revenue / total_trips, 2) AS revenue_per_trip,
    ROUND(total_tips / total_trips, 2) AS tips_per_trip,
    avg_tip_percentage
FROM curated_daily_trip_statistics
WHERE year = 2024 AND month = 1
ORDER BY pickup_date DESC
LIMIT 31;

-- ============================================
-- 2. Peak Hours Analysis
-- ============================================

SELECT 
    pickup_hour,
    day_name,
    trip_count,
    avg_fare,
    avg_distance,
    avg_duration
FROM curated_hourly_trip_patterns
WHERE year = 2024 AND month = 1
ORDER BY trip_count DESC
LIMIT 20;

-- ============================================
-- 3. Weekend vs Weekday Performance
-- ============================================

SELECT 
    CASE 
        WHEN pickup_day_of_week IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    SUM(trip_count) AS total_trips,
    ROUND(AVG(avg_fare), 2) AS avg_fare,
    ROUND(AVG(avg_distance), 2) AS avg_distance,
    ROUND(AVG(avg_duration), 2) AS avg_duration
FROM curated_hourly_trip_patterns
WHERE year = 2024 AND month = 1
GROUP BY 
    CASE 
        WHEN pickup_day_of_week IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END
ORDER BY day_type;

-- ============================================
-- 4. Payment Method Preferences
-- ============================================

SELECT 
    payment_method,
    transaction_count,
    total_revenue,
    ROUND(total_revenue / transaction_count, 2) AS avg_transaction_value,
    avg_tip_percentage,
    ROUND(100.0 * transaction_count / SUM(transaction_count) OVER (), 2) AS percentage_of_total
FROM curated_payment_type_analysis
WHERE year = 2024 AND month = 1
ORDER BY transaction_count DESC;

-- ============================================
-- 5. Trip Distance Distribution
-- ============================================

SELECT 
    distance_bucket,
    trip_count,
    total_revenue,
    avg_fare,
    avg_duration,
    ROUND(100.0 * trip_count / SUM(trip_count) OVER (), 2) AS percentage_of_trips
FROM curated_distance_distribution
WHERE year = 2024 AND month = 1
ORDER BY 
    CASE distance_bucket
        WHEN '0-1 miles' THEN 1
        WHEN '1-3 miles' THEN 2
        WHEN '3-5 miles' THEN 3
        WHEN '5-10 miles' THEN 4
        WHEN '10-20 miles' THEN 5
        WHEN '20+ miles' THEN 6
    END;

-- ============================================
-- 6. High-Value Trips Analysis
-- ============================================

SELECT 
    DATE(pickup_datetime) AS trip_date,
    pickup_datetime,
    dropoff_datetime,
    trip_distance,
    trip_duration_minutes,
    fare_amount,
    tip_amount,
    total_amount,
    tip_percentage
FROM processed_taxi_trips
WHERE year = 2024 
    AND month = 1
    AND total_amount > 100
ORDER BY total_amount DESC
LIMIT 50;

-- ============================================
-- 7. Average Trip Metrics by Day of Week
-- ============================================

SELECT 
    day_name,
    SUM(trip_count) AS total_trips,
    ROUND(AVG(avg_fare), 2) AS avg_fare,
    ROUND(AVG(avg_distance), 2) AS avg_distance,
    ROUND(AVG(avg_duration), 2) AS avg_duration_minutes
FROM curated_hourly_trip_patterns
WHERE year = 2024 AND month = 1
GROUP BY day_name, pickup_day_of_week
ORDER BY pickup_day_of_week;

-- ============================================
-- 8. Tip Analysis by Trip Characteristics
-- ============================================

SELECT 
    CASE 
        WHEN trip_distance < 2 THEN 'Short (< 2 mi)'
        WHEN trip_distance < 5 THEN 'Medium (2-5 mi)'
        WHEN trip_distance < 10 THEN 'Long (5-10 mi)'
        ELSE 'Very Long (10+ mi)'
    END AS trip_category,
    COUNT(*) AS trip_count,
    ROUND(AVG(tip_percentage), 2) AS avg_tip_percentage,
    ROUND(AVG(tip_amount), 2) AS avg_tip_amount,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM processed_taxi_trips
WHERE year = 2024 
    AND month = 1
    AND payment_type = 1
    AND tip_amount > 0
GROUP BY 
    CASE 
        WHEN trip_distance < 2 THEN 'Short (< 2 mi)'
        WHEN trip_distance < 5 THEN 'Medium (2-5 mi)'
        WHEN trip_distance < 10 THEN 'Long (5-10 mi)'
        ELSE 'Very Long (10+ mi)'
    END
ORDER BY avg_tip_percentage DESC;

-- ============================================
-- 9. Monthly Revenue Summary
-- ============================================

SELECT 
    year,
    month,
    SUM(total_trips) AS monthly_trips,
    ROUND(SUM(total_revenue), 2) AS monthly_revenue,
    ROUND(SUM(total_tips), 2) AS monthly_tips,
    ROUND(AVG(avg_trip_distance), 2) AS avg_distance,
    ROUND(AVG(avg_trip_duration), 2) AS avg_duration
FROM curated_daily_trip_statistics
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- ============================================
-- 10. Data Quality Check
-- ============================================

SELECT 
    year,
    month,
    COUNT(*) AS total_records,
    COUNT(DISTINCT day) AS days_with_data,
    MIN(pickup_datetime) AS earliest_trip,
    MAX(pickup_datetime) AS latest_trip,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM processed_taxi_trips
WHERE year = 2024 AND month = 1
GROUP BY year, month;

-- ============================================
-- 11. Cost Optimization Query
-- Query to analyze S3 storage usage patterns
-- ============================================

SELECT 
    year,
    month,
    COUNT(*) AS record_count,
    ROUND(COUNT(*) * 0.00001, 4) AS estimated_storage_gb
FROM processed_taxi_trips
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- ============================================
-- 12. Performance Benchmark Query
-- Test query performance on partitioned data
-- ============================================

SELECT 
    COUNT(*) AS total_trips,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM processed_taxi_trips
WHERE year = 2024 
    AND month = 1 
    AND day = 15;
