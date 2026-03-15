# Cost Optimization Guide

## Overview

This document outlines the cost optimization strategies implemented in the data lake architecture and provides recommendations for further cost reduction.

## Current Cost Optimization Features

### 1. S3 Storage Optimization

#### Lifecycle Policies
- **Raw Layer**: 
  - 30 days → Standard-IA (50% cost reduction)
  - 90 days → Glacier Instant Retrieval (68% cost reduction)
  - 180 days → Deep Archive (95% cost reduction)
  
- **Processed Layer**:
  - 60 days → Standard-IA
  - 180 days → Glacier Instant Retrieval
  
- **Curated Layer**:
  - 90 days → Standard-IA (frequently accessed)
  
- **Temp Data**:
  - 7 days → Automatic deletion

#### Storage Format
- **Parquet with Snappy**: 70-80% smaller than CSV
- **Columnar Storage**: Athena reads only required columns
- **Example Savings**: 1TB CSV → 200-300GB Parquet

### 2. Compute Optimization

#### AWS Glue
- **Worker Type**: G.1X (4 vCPU, 16GB RAM) - $0.44/DPU-hour
- **Worker Count**: 2 workers (right-sized for moderate workloads)
- **Job Bookmarks**: Process only new data (incremental processing)
- **Timeout**: 60 minutes (prevents runaway jobs)
- **Max Concurrent Runs**: 1 (prevents duplicate execution)

**Cost Example**:
- Without bookmarks: Process 1TB daily = $50/day
- With bookmarks: Process 10GB new data = $0.50/day
- **Savings**: 99% reduction

#### AWS Lambda
- **Memory**: 256MB (right-sized for orchestration)
- **Timeout**: 5 minutes
- **Free Tier**: 1M requests/month, 400,000 GB-seconds
- **Typical Cost**: $0.01-0.10/day for orchestration

### 3. Query Optimization (Catalog-Enabled)

#### Amazon Athena with Partition Pruning
- **Pricing**: $5 per TB scanned
- **Partition Pruning via Catalog**: Scan only relevant partitions
- **Parquet Format**: Scan 5-10x less data vs CSV
- **Result Caching**: 24-hour cache for repeated queries

**How Partition Pruning Works**:
1. Crawlers register partitions in Catalog with metadata
2. Athena queries Catalog for partition locations
3. WHERE clause filters applied to partition metadata
4. Only matching partitions scanned

**Cost Example Without Partition Pruning**:
- Query: `SELECT * FROM trips WHERE year=2024 AND month=1`
- Scans: All 100 partitions = 10GB
- Cost: $0.05

**Cost Example With Partition Pruning (Catalog-Enabled)**:
- Query: Same query
- Catalog returns: Only 30 partitions for Jan 2024
- Scans: 3GB
- Cost: $0.015
- **Savings**: 70% reduction

**Additional Savings**:
- Parquet columnar format: Read only required columns
- Snappy compression: Less data to scan
- Combined savings: 90%+ vs CSV full scans

**Best Practices**:
- Always filter on partition keys in WHERE clause
- Use Catalog partition indexes for large tables
- Monitor partition count (more partitions = more savings)

#### Glue Data Catalog Costs

**Pricing**:
- **Storage**: First 1M objects free, then $1 per 100K objects/month
- **API Calls**: First 1M requests/month free, then $1 per 1M requests
- **Objects**: Tables, partitions, databases count as objects

**My Project Costs**:
- 6 tables + 100 partitions = 106 objects
- Storage: Free (under 1M objects)
- API calls: ~10K-100K/month
  - Glue ETL: GetTable, GetPartitions, UpdateJobBookmark
  - Athena: GetTable, GetPartitions
  - Crawlers: UpdateTable, CreatePartition
- API cost: Free (under 1M requests)

**Total Catalog Cost**: $0-1/month (essentially free for small-medium workloads)

**Cost Optimization**:
- Use partition indexes (reduces GetPartitions calls)
- Cache table metadata in applications (reduce GetTable calls)
- Batch partition operations (CreatePartition)
- Monitor API usage in CloudWatch

**ROI**: 
- Catalog cost: $1/month
- Savings from job bookmarks: $20-200/month (99% compute reduction)
- Savings from partition pruning: $5-50/month (90% query reduction)
- **Net Savings**: 25-250x return on Catalog investment

### 4. Monitoring Optimization

#### CloudWatch
- **Log Retention**: 14-30 days (vs default indefinite)
- **Metric Filters**: Only essential metrics
- **Dashboard**: Single consolidated view

**Cost Savings**: $5-10/month vs unmanaged logs

## Estimated Monthly Costs

### Small Workload (100GB/month new data)
| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | 500GB average | $11.50 |
| S3 Requests | 10K PUT, 100K GET | $0.10 |
| Glue ETL | 10 job runs, 30 min each (with bookmarks) | $4.40 |
| Glue Crawler | 10 runs (3 crawlers × 3-4 runs) | $0.44 |
| Glue Catalog | 10K API calls (GetTable, GetPartitions) | $0.01 |
| Lambda | 1K invocations | $0.00 (free tier) |
| Athena | 100GB scanned (with partition pruning) | $0.50 |
| CloudWatch | Logs + Metrics (including Catalog) | $5.00 |
| **Total** | | **~$22/month** |

**Without Catalog Optimization**:
- Glue ETL: 10 full runs = $44.00 (no bookmarks)
- Athena: 1TB scanned = $5.00 (no partition pruning)
- **Total**: ~$66/month
- **Savings with Catalog**: 67% reduction

### Medium Workload (1TB/month new data)
| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | 5TB average | $115.00 |
| S3 Requests | 100K PUT, 1M GET | $1.00 |
| Glue ETL | 30 job runs, 1 hour each (with bookmarks) | $26.40 |
| Glue Crawler | 30 runs (3 crawlers × 10 runs) | $1.32 |
| Glue Catalog | 100K API calls | $0.10 |
| Lambda | 10K invocations | $0.20 |
| Athena | 1TB scanned (with partition pruning) | $5.00 |
| CloudWatch | Logs + Metrics (including Catalog) | $15.00 |
| **Total** | | **~$164/month** |

**Without Catalog Optimization**:
- Glue ETL: 30 full runs = $264.00 (no bookmarks)
- Athena: 10TB scanned = $50.00 (no partition pruning)
- **Total**: ~$453/month
- **Savings with Catalog**: 64% reduction

### Large Workload (10TB/month new data)
| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | 50TB average | $1,150.00 |
| S3 Requests | 1M PUT, 10M GET | $10.00 |
| Glue ETL | 100 job runs, 2 hours each (with bookmarks) | $176.00 |
| Glue Crawler | 100 runs (3 crawlers × 33 runs) | $4.40 |
| Glue Catalog | 1M API calls | $1.00 |
| Lambda | 100K invocations | $2.00 |
| Athena | 10TB scanned (with partition pruning) | $50.00 |
| CloudWatch | Logs + Metrics (including Catalog) | $50.00 |
| **Total** | | **~$1,443/month** |

**Without Catalog Optimization**:
- Glue ETL: 100 full runs = $1,760.00 (no bookmarks)
- Athena: 100TB scanned = $500.00 (no partition pruning)
- **Total**: ~$3,677/month
- **Savings with Catalog**: 61% reduction

## Additional Cost Optimization Recommendations

### 1. Use S3 Intelligent-Tiering
- Automatically moves data between access tiers
- No retrieval fees
- Small monitoring fee ($0.0025 per 1,000 objects)
- **Best for**: Unpredictable access patterns

### 2. Optimize Glue Job Configuration
```python
# Use smaller worker types for light workloads
worker_type = "G.025X"  # $0.11/DPU-hour (vs G.1X at $0.44)

# Use Glue Flex for non-time-sensitive jobs
execution_class = "FLEX"  # 35% discount, 10-minute startup delay
```

### 3. Implement Data Retention Policies
```python
# Delete old data after business retention period
lifecycle_rule = {
    "raw_data": "Delete after 365 days",
    "processed_data": "Delete after 730 days",
    "curated_data": "Keep indefinitely (small size)"
}
```

### 4. Use Athena Workgroup Limits
```hcl
# Set per-query data scan limits
resource "aws_athena_workgroup" "data_lake" {
  configuration {
    bytes_scanned_cutoff_per_query = 1073741824  # 1GB limit
  }
}
```

### 5. Optimize Partitioning Strategy
- **Current**: year/month/day (good for time-series queries)
- **Consider**: Add location-based partitioning if querying by region
- **Avoid**: Over-partitioning (too many small files)

### 6. Use AWS Cost Explorer
```bash
# Enable Cost Explorer tags
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=TAG,Key=Project
```

### 7. Reserved Capacity (for predictable workloads)
- **Glue**: No reserved capacity available
- **Athena**: No reserved capacity available
- **S3**: Use S3 Intelligent-Tiering instead

## Cost Monitoring

### Set Up Budget Alerts
```bash
aws budgets create-budget \
    --account-id YOUR_ACCOUNT_ID \
    --budget file://budget.json \
    --notifications-with-subscribers file://notifications.json
```

### CloudWatch Cost Anomaly Detection
- Enable AWS Cost Anomaly Detection
- Set up alerts for 20%+ cost increases
- Monitor daily spend trends

## Best Practices

### 1. Development vs Production
- **Dev**: Use smaller datasets, fewer workers
- **Prod**: Full-scale resources, automated monitoring

### 2. Data Sampling
- Use `TABLESAMPLE` in Athena for development queries
- Test ETL jobs on small data samples first

### 3. Query Optimization
```sql
-- Good: Partition pruning
SELECT * FROM processed_taxi_trips
WHERE year = 2024 AND month = 1 AND day = 15;

-- Bad: Full table scan
SELECT * FROM processed_taxi_trips
WHERE pickup_datetime > '2024-01-15';
```

### 4. Compression Testing
- Test different compression codecs (Snappy, GZIP, ZSTD)
- Balance compression ratio vs query performance
- Snappy: Fast decompression, good compression (recommended)

## Cost Comparison: This Architecture vs Alternatives

### vs Traditional Data Warehouse (Redshift)
- **Redshift**: $180/month (dc2.large, 24/7)
- **This Solution**: $22-164/month (serverless, pay-per-use)
- **Savings**: 50-90% for intermittent workloads

### vs Managed ETL (AWS Data Pipeline)
- **Data Pipeline**: $1/pipeline/day + EC2 costs
- **This Solution**: Glue (serverless, pay-per-job)
- **Savings**: 40-60% for batch workloads

### vs Self-Managed Spark on EMR
- **EMR**: $200+/month (cluster running 24/7)
- **This Solution**: Glue (serverless, no cluster management)
- **Savings**: 70-90% + reduced operational overhead

## ROI Analysis

### Time Savings
- **Infrastructure Setup**: 30 minutes (Terraform)
- **Manual Setup**: 4-6 hours
- **Ongoing Maintenance**: Minimal (serverless)

### Cost Savings
- **Year 1**: $2,000-5,000 saved vs traditional architecture
- **Year 2+**: $3,000-8,000 saved (no migration costs)

## Monitoring Your Costs

### Daily Checks
1. CloudWatch dashboard for resource usage
2. S3 storage metrics
3. Glue job execution times

### Weekly Reviews
1. AWS Cost Explorer for spend trends
2. Athena query costs
3. Identify optimization opportunities

### Monthly Analysis
1. Compare actual vs budgeted costs
2. Review lifecycle policy effectiveness
3. Analyze query patterns for optimization

## Cost Optimization Checklist

- [ ] Enable S3 lifecycle policies
- [ ] Use Parquet with Snappy compression
- [ ] Enable Glue job bookmarks
- [ ] Implement partition projection in Athena
- [ ] Set CloudWatch log retention policies
- [ ] Configure budget alerts
- [ ] Tag all resources for cost allocation
- [ ] Use Athena workgroup query limits
- [ ] Monitor and optimize slow queries
- [ ] Delete temporary/test data regularly
- [ ] Review and remove unused resources monthly

## Conclusion

This architecture is designed to be cost-effective from day one, with built-in optimizations that scale with your data volume. By following these best practices, you can maintain a production-grade data lake at a fraction of the cost of traditional solutions.
