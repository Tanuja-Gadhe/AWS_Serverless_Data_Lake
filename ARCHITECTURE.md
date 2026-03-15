# Architecture Documentation

## Overview

This project implements a serverless, event-driven data lake architecture on AWS, designed for scalability, cost optimization, and production reliability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Lake Architecture                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Data Source  │
│ (NYC Taxi)   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          S3 Data Lake (3-Layer)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐      ┌──────────────┐      ┌─────────────┐            │
│  │ Raw Layer   │─────▶│ Processed    │─────▶│ Curated     │            │
│  │ (CSV/JSON)  │      │ (Parquet)    │      │ (Analytics) │            │
│  │             │      │ Partitioned  │      │ Aggregated  │            │
│  └─────────────┘      └──────────────┘      └─────────────┘            │
│       │                     │                      │                     │
│       │ Lifecycle           │ Lifecycle            │ Lifecycle           │
│       │ 30d→IA              │ 60d→IA               │ 90d→IA              │
│       │ 90d→Glacier         │ 180d→Glacier         │                     │
│       │ 180d→Deep Archive   │                      │                     │
└───────┼─────────────────────┼──────────────────────┼─────────────────────┘
        │                     │                      │
        │ S3 Event            │                      │
        ▼                     │                      │
┌──────────────┐              │                      │
│ EventBridge  │              │                      │
└──────┬───────┘              │                      │
       │                      │                      │
       ▼                      │                      │
┌──────────────┐              │                      │
│   Lambda     │              │                      │
│ Orchestrator │              │                      │
└──────┬───────┘              │                      │
       │                      │                      │
       │ Trigger              │                      │
       ▼                      │                      │
┌─────────────────────────────┼──────────────────────┼─────────────────────┐
│                      AWS Glue                      │                     │
├────────────────────────────────────────────────────┤                     │
│                                                    │                     │
│  ┌──────────────┐    ┌──────────────────────┐    │                     │
│  │   Crawler    │───▶│   Data Catalog       │    │                     │
│  │  (Raw Data)  │    │   (Metadata Store)   │    │                     │
│  └──────────────┘    └──────────────────────┘    │                     │
│                               │                    │                     │
│  ┌──────────────────────────────────────────┐    │                     │
│  │        Spark ETL Jobs                    │    │                     │
│  ├──────────────────────────────────────────┤    │                     │
│  │  1. Raw → Processed (Parquet + Snappy)   │    │                     │
│  │     - Data cleansing                     │    │                     │
│  │     - Quality checks                     │    │                     │
│  │     - Partitioning (year/month/day)      │    │                     │
│  │     - Job bookmarks (incremental)        │    │                     │
│  │                                          │    │                     │
│  │  2. Processed → Curated (Analytics)      │    │                     │
│  │     - Daily statistics                   │    │                     │
│  │     - Hourly patterns                    │    │                     │
│  │     - Payment analysis                   │    │                     │
│  │     - Distance distribution              │    │                     │
│  └──────────────────────────────────────────┘    │                     │
└────────────────────────────────────────────────────┘                     │
                                │                                          │
                                ▼                                          │
┌─────────────────────────────────────────────────────────────────────────┤
│                         Amazon Athena                                    │
│  - Serverless SQL queries                                               │
│  - Query processed & curated layers                                     │
│  - Cost optimized with partition projection                             │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Amazon QuickSight                                   │
│  - Interactive dashboards                                               │
│  - Business intelligence                                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    Monitoring & Alerting                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  CloudWatch Logs  │  CloudWatch Alarms  │  SNS Notifications           │
│  - Job execution  │  - Job failures     │  - Email alerts              │
│  - Error tracking │  - Lambda errors    │  - Status updates            │
│  - Performance    │  - Cost anomalies   │                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Security (IAM)                                   │
│  - Least privilege access                                               │
│  - Service-specific roles                                               │
│  - S3 encryption at rest                                                │
│  - VPC endpoints (optional)                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Ingestion Layer (Raw)
- **Input**: CSV/JSON files uploaded to `s3://bucket/raw/taxi_trips/`
- **Trigger**: S3 event → EventBridge → Lambda
- **Storage**: Original format, unmodified
- **Lifecycle**: 30d → IA, 90d → Glacier, 180d → Deep Archive

### 2. Processing Layer (Processed)
- **ETL Job**: `raw_to_processed.py`
- **Transformations**:
  - Data type conversions
  - Data quality filters
  - Derived columns (trip duration, speed, tip percentage)
  - Partitioning by year/month/day
- **Output Format**: Parquet with Snappy compression
- **Incremental Processing**: Glue job bookmarks enabled
- **Lifecycle**: 60d → IA, 180d → Glacier

### 3. Analytics Layer (Curated)
- **ETL Job**: `processed_to_curated.py`
- **Analytics Tables**:
  1. **Daily Trip Statistics**: Aggregated daily metrics
  2. **Hourly Trip Patterns**: Time-based analysis
  3. **Payment Type Analysis**: Payment method insights
  4. **Distance Distribution**: Trip distance buckets
- **Output Format**: Parquet with Snappy compression
- **Partitioning**: year/month
- **Lifecycle**: 90d → IA

## Key Components

### AWS Glue
- **Data Catalog**: Centralized metadata repository
- **Crawlers**: Automatic schema discovery
- **ETL Jobs**: Spark-based transformations (Python 3, Glue 4.0)
- **Job Bookmarks**: Incremental processing to avoid reprocessing

### Amazon S3
- **Versioning**: Enabled for data protection
- **Encryption**: SSE-S3 encryption at rest
- **Lifecycle Policies**: Automated tiering for cost optimization
- **Event Notifications**: EventBridge integration

### AWS Lambda
- **Event-Driven**: Triggered by S3 events via EventBridge
- **Orchestration**: Manages Glue job execution
- **Error Handling**: Retry logic and SNS notifications
- **Concurrency Control**: Prevents duplicate job runs

### Amazon Athena
- **Serverless Queries**: Pay-per-query pricing
- **Partition Projection**: Eliminates MSCK REPAIR overhead
- **Workgroup**: Centralized query management and cost controls

### CloudWatch
- **Logs**: Centralized logging for all services
- **Alarms**: Proactive alerting for failures
- **Dashboards**: Real-time monitoring
- **Metrics**: Performance and cost tracking

### IAM Security
- **Least Privilege**: Service-specific roles with minimal permissions
- **Resource-Based Policies**: Fine-grained access control
- **Encryption**: Data encrypted at rest and in transit

## Cost Optimization Strategies

### 1. Storage Optimization
- **Parquet Format**: 70-80% compression vs CSV
- **Snappy Compression**: Fast compression with good ratio
- **Lifecycle Policies**: Automatic tiering to cheaper storage classes
- **Partition Pruning**: Reduces data scanned by queries

### 2. Compute Optimization
- **Glue Job Bookmarks**: Process only new data
- **Right-Sized Workers**: G.1X workers for moderate workloads
- **Timeout Controls**: Prevent runaway jobs
- **Concurrent Run Limits**: Prevent accidental parallel execution

### 3. Query Optimization
- **Partition Projection**: Eliminates metadata operations
- **Columnar Format**: Read only required columns
- **Result Caching**: Athena caches results for 24 hours
- **Workgroup Limits**: Set per-query data scan limits

### 4. Monitoring & Alerts
- **Cost Anomaly Detection**: CloudWatch alarms for unusual costs
- **Resource Tagging**: Track costs by project/environment
- **Log Retention**: 14-30 days to reduce storage costs

## Scalability Features

1. **Horizontal Scaling**: Add more Glue workers as data volume grows
2. **Partitioning Strategy**: Efficient data pruning for large datasets
3. **Serverless Architecture**: Auto-scaling for Lambda and Athena
4. **Decoupled Layers**: Independent scaling of ingestion, processing, and analytics

## Performance Characteristics

- **Data Ingestion**: Event-driven, sub-minute latency
- **ETL Processing**: 2-10 minutes for typical batch sizes
- **Query Performance**: Sub-second to seconds (depending on data volume)
- **Incremental Updates**: Only new data processed

## Security Best Practices

1. **Encryption**: All data encrypted at rest (S3, Glue)
2. **Access Control**: IAM roles with least privilege
3. **Network Security**: VPC endpoints for private connectivity (optional)
4. **Audit Logging**: CloudTrail for API activity
5. **Data Protection**: S3 versioning and MFA delete (optional)

## Disaster Recovery

- **S3 Versioning**: Recover from accidental deletions
- **Cross-Region Replication**: Optional for critical data
- **Backup Strategy**: Glacier/Deep Archive for long-term retention
- **Documentation**: Comprehensive setup guide for reproducible deployments

## Monitoring & Observability

### Key Metrics
- Glue job success/failure rate
- Lambda invocation count and errors
- S3 storage size and object count
- Athena query execution time and data scanned
- Cost per day/week/month

### Alerting
- SNS notifications for job failures
- CloudWatch alarms for anomalies
- Email alerts for critical issues

## Future Enhancements

1. **Data Quality Framework**: Great Expectations integration
2. **Data Lineage**: AWS Glue Data Lineage tracking
3. **Real-Time Streaming**: Kinesis Data Streams + Firehose
4. **Machine Learning**: SageMaker integration for predictive analytics
5. **Data Governance**: AWS Lake Formation for fine-grained access control
