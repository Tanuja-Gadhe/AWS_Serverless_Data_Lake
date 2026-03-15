# AWS Serverless Data Lake - Production-Grade Architecture

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Tanuja-Gadhe/AWS_Serverless_Data_Lake/graphs/commit-activity)

> **Project Status**: ✅ Production-ready | 📊 Processing 3M+ records/month | 💰 81% cost savings vs traditional warehouse

A scalable, event-driven data lake architecture built on AWS with **AWS Glue Data Catalog** as the central metadata repository, demonstrating production-grade data engineering best practices including automated schema discovery, incremental processing, cost optimization, and comprehensive monitoring.

> **Note**: This project uses manual deployment through AWS Console and CLI to ensure deep understanding of each service. While automation tools like Terraform are valuable, I chose the hands-on approach to truly master AWS data engineering concepts and be able to explain every component confidently in interviews.

## 🏗️ Architecture Overview

This project implements a **3-layer data lake architecture** (Raw → Processed → Curated) using AWS serverless services with **Glue Data Catalog** at the core:

- **Metadata Layer**: AWS Glue Data Catalog (centralized metadata for 6 tables, 100+ partitions)
- **Schema Discovery**: 3 Glue Crawlers for automated schema inference and partition management
- **Ingestion**: Event-driven pipeline with S3, EventBridge, and Lambda
- **Processing**: Spark-based ETL with AWS Glue (job bookmarks for incremental processing)
- **Storage**: Parquet + Snappy compression (70-80% reduction)
- **Analytics**: Serverless SQL queries with Amazon Athena (partition pruning via Catalog)
- **Visualization**: Business intelligence with Amazon QuickSight (Catalog integration)
- **Monitoring**: CloudWatch logs, metrics, alarms (including Catalog API metrics) with SNS notifications

### Architecture Diagram

```
                                    ┌─────────────────────────────┐
                                    │   AWS Glue Data Catalog     │
                                    │  (Metadata Repository)      │
                                    │  - 6 Tables                 │
                                    │  - 100+ Partitions          │
                                    │  - Job Bookmarks            │
                                    │  - Schema Versions          │
                                    └──────────┬──────────────────┘
                                               │ (All services read/write metadata)
                                               │
        ┌──────────────────────────────────────┼──────────────────────────────────────┐
        │                                      │                                      │
        ▼                                      ▼                                      ▼
Data Source → S3 (Raw) → EventBridge → Lambda → Glue ETL → S3 (Processed) → Glue ETL → S3 (Curated) → Athena → QuickSight
        ↓                                      ↓                           ↓
   Crawler (Raw)                         Crawler (Processed)         Crawler (Curated)
   (Hourly scan)                         (Daily scan)                (Daily scan)
        │                                      │                           │
        └──────────────────────────────────────┴───────────────────────────┘
                            (Update Catalog with schemas/partitions)
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 🚀 Key Features

### Metadata & Catalog Management
- 📚 **Glue Data Catalog**: Centralized metadata repository (6 tables, 100+ partitions)
- 🤖 **Automated Crawlers**: 3 crawlers for schema discovery and partition management
- 📖 **Job Bookmarks**: Incremental processing tracking (stored in Catalog)
- 📊 **Partition Indexes**: Accelerated partition filtering
- 🔄 **Table Versioning**: Automatic schema history tracking
- 📈 **Column Statistics**: Query optimization metadata

### Production-Grade Capabilities
- ✅ **Event-Driven Orchestration**: Automatic pipeline triggering on data arrival
- ✅ **Incremental Processing**: Glue job bookmarks for processing only new data (99% cost reduction)
- ✅ **Automated Schema Discovery**: Crawlers eliminate manual table definitions
- ✅ **Data Quality**: Built-in validation and cleansing rules
- ✅ **Partition Optimization**: Year/month/day partitioning for efficient queries
- ✅ **Compression**: Parquet with Snappy (70-80% size reduction)
- ✅ **Cross-Service Integration**: All services use Catalog for metadata
- ✅ **Monitoring**: CloudWatch dashboards, alarms, Catalog API metrics, and SNS notifications
- ✅ **Security**: IAM least-privilege access, S3 encryption, Catalog encryption
- ✅ **Manual Setup**: Step-by-step guide for AWS Console and CLI

### Cost Optimization
- 💰 **Job Bookmarks**: Process only new data (99% compute cost reduction)
- 💰 **Partition Pruning**: Catalog-enabled optimization (90%+ query cost reduction)
- 💰 **S3 Lifecycle Policies**: Automatic tiering to IA, Glacier, Deep Archive
- 💰 **Serverless Architecture**: Pay only for what you use
- 💰 **Columnar Storage**: Parquet reduces storage and query costs
- 💰 **Right-Sized Resources**: Optimized Glue worker configuration
- 💰 **Estimated Cost**: $22-164/month (depending on data volume)

See [COST_OPTIMIZATION.md](docs/COST_OPTIMIZATION.md) for detailed cost analysis.

## 📊 Dataset

**NYC Taxi Trip Records** - Public dataset from NYC Taxi & Limousine Commission

- **Source**: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Format**: CSV/Parquet
- **Volume**: ~3M trips/month, ~500MB compressed
- **Schema**: 19 columns including timestamps, locations, fares, tips

**Why this dataset?**
- Real-world, production-scale data
- Time-series data (perfect for partitioning)
- Rich for analytics (revenue, patterns, trends)
- Publicly available and well-documented

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Metadata** | AWS Glue Data Catalog | Centralized metadata repository (6 tables, 100+ partitions) |
| **Schema Discovery** | AWS Glue Crawlers | Automated schema inference and partition management (3 crawlers) |
| **Storage** | Amazon S3 | Data lake storage with lifecycle policies |
| **ETL** | AWS Glue (Spark) | Distributed data processing with job bookmarks |
| **Orchestration** | AWS Lambda + EventBridge | Event-driven automation |
| **Querying** | Amazon Athena | Serverless SQL analytics with partition pruning |
| **Visualization** | Amazon QuickSight | Business intelligence dashboards (Catalog integration) |
| **Monitoring** | Amazon CloudWatch | Logs, metrics, alarms (including Catalog API metrics) |
| **Notifications** | Amazon SNS | Email alerts |
| **Security** | AWS IAM | Access control and permissions |

## 📁 Project Structure

```
aws-data-lake-project/
├── glue-jobs/                 # Glue ETL scripts
│   ├── raw_to_processed.py    # Raw → Processed transformation
│   └── processed_to_curated.py # Processed → Curated aggregation
├── lambda-functions/          # Lambda orchestration
│   ├── trigger_glue_job.py    # Event-driven job trigger
│   └── requirements.txt
├── scripts/                   # Sample data generation
│   ├── generate_sample_data.py # Generate test data
│   ├── download_sample_data.py # Download NYC Taxi data
│   └── convert_parquet_to_csv.py
├── athena-queries/            # SQL queries
│   ├── create_tables.sql      # DDL statements
│   └── analytics_queries.sql  # Sample analytics queries
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Architecture deep-dive
│   ├── COST_OPTIMIZATION.md   # Cost analysis
│   └── INTERVIEW_GUIDE.md     # Interview preparation
├── AWS_SETUP_GUIDE.md         # Complete manual setup guide
└── README.md                  # This file
```

## 🚦 Getting Started

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Python** 3.11+
4. **Basic AWS knowledge** (Console and CLI)

### Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify AWS access
aws sts get-caller-identity
```

### 📖 Complete Setup Guide

**Follow**: `AWS_SETUP_GUIDE.md` - This is your single, comprehensive guide!

This guide provides step-by-step instructions for:
- ✅ Creating Glue Data Catalog database
- ✅ Configuring 3 Glue Crawlers for automated schema discovery
- ✅ Creating all AWS resources through the Console
- ✅ Configuring IAM roles and permissions
- ✅ Setting up Glue ETL jobs with job bookmarks
- ✅ Setting up the complete data pipeline
- ✅ Testing and validation
- ✅ Monitoring and troubleshooting (including Catalog metrics)
- ✅ Cost optimization strategies
- ✅ Complete cleanup instructions

**Estimated Setup Time**: 2-3 hours (first time)

### 11-Phase Deployment Overview

1. **Phase 1**: Create S3 Buckets (3 buckets with lifecycle policies)
2. **Phase 2**: Setup IAM Roles (Glue and Lambda execution roles)
3. **Phase 3**: Configure AWS Glue Data Catalog
   - 3.1: Create Glue Database
   - 3.2: Create Raw Crawler (hourly schema discovery)
   - 3.3: Create Processed Crawler (daily partition management)
   - 3.4: Create Curated Crawler (daily analytics tables)
   - 3.5: Create ETL Jobs with job bookmarks enabled
4. **Phase 4**: Deploy Lambda Function (Event-driven orchestration)
5. **Phase 5**: Setup EventBridge (S3 event filtering)
6. **Phase 6**: Configure SNS (Email notifications)
7. **Phase 7**: Setup CloudWatch (Monitoring, alarms, Catalog API metrics)
8. **Phase 8**: Configure Athena (Query workgroup with partition pruning)
9. **Phase 9**: Load Sample Data (NYC Taxi dataset)
10. **Phase 10**: Run Pipeline (Execute crawlers and ETL jobs)
11. **Phase 11**: Setup QuickSight (Optional BI dashboards)

Each phase has detailed, step-by-step instructions in `AWS_SETUP_GUIDE.md`.

## 📈 Data Pipeline Flow

### 1. Raw Layer (Bronze)
- **Input**: CSV/JSON files uploaded to `s3://bucket/raw/taxi_trips/`
- **Trigger**: S3 event → EventBridge → Lambda
- **Crawler**: Raw Crawler scans S3 hourly, infers schema from CSV headers
- **Catalog**: Table `raw_taxi_trips` created with schema and partition metadata
- **Storage**: Original format, immutable
- **Partitions**: Detected automatically (year/month/day folders)

### 2. Processed Layer (Silver)
- **ETL Job**: `raw_to_processed.py`
- **Catalog Read**: Job reads `raw_taxi_trips` schema from Catalog
- **Transformations**:
  - Data type conversions and validation
  - Quality filters (remove invalid records)
  - Derived metrics (trip duration, speed, tip percentage)
  - Partitioning by year/month/day
- **Output**: Parquet with Snappy compression to `s3://bucket/processed/`
- **Job Bookmarks**: Catalog tracks processed files (only new data processed)
- **Crawler**: Processed Crawler discovers new partitions daily
- **Catalog Update**: Table `processed_taxi_trips` updated with new partitions

### 3. Curated Layer (Gold)
- **ETL Job**: `processed_to_curated.py`
- **Catalog Read**: Job reads `processed_taxi_trips` schema from Catalog
- **Analytics Tables**:
  - **Daily Trip Statistics**: Revenue, trips, averages
  - **Hourly Trip Patterns**: Time-based demand analysis
  - **Payment Type Analysis**: Payment method insights
  - **Distance Distribution**: Trip distance buckets
- **Output**: Parquet with Snappy, partitioned by year/month
- **Job Bookmarks**: Catalog tracks processed partitions
- **Crawler**: Curated Crawler discovers new analytics tables daily
- **Catalog Update**: 4 analytics tables registered in Catalog
- **Purpose**: Optimized for BI and reporting

### 4. Analytics & Visualization
- **Athena**: Queries Catalog for table metadata and partition locations
- **Partition Pruning**: Only scans relevant partitions (90%+ cost savings)
- **QuickSight**: Discovers tables from Catalog, creates datasets and dashboards
- **Monitoring**: CloudWatch tracks Catalog API calls (GetTable, GetPartitions)

## 🔍 Sample Queries

### Query 1: Daily Revenue Trends
```sql
SELECT 
    pickup_date,
    total_trips,
    total_revenue,
    ROUND(total_revenue / total_trips, 2) AS revenue_per_trip
FROM curated_daily_trip_statistics
WHERE year = 2024 AND month = 1
ORDER BY pickup_date DESC;
```

### Query 2: Peak Hours Analysis
```sql
SELECT 
    pickup_hour,
    day_name,
    trip_count,
    avg_fare
FROM curated_hourly_trip_patterns
WHERE year = 2024 AND month = 1
ORDER BY trip_count DESC
LIMIT 10;
```

### Query 3: Payment Method Distribution
```sql
SELECT 
    payment_method,
    transaction_count,
    ROUND(100.0 * transaction_count / SUM(transaction_count) OVER (), 2) AS percentage
FROM curated_payment_type_analysis
WHERE year = 2024 AND month = 1
ORDER BY transaction_count DESC;
```

See [analytics_queries.sql](athena-queries/analytics_queries.sql) for more examples.

## 📊 Monitoring & Observability

### CloudWatch Dashboards
- Glue job execution metrics
- Lambda invocation and error rates
- S3 storage size and object counts
- Athena query performance

### Alarms & Notifications
- Glue job failures → SNS email alert
- Lambda errors → SNS email alert
- Cost anomalies → Budget alerts

### Log Analysis
```bash
# View Glue job logs
aws logs tail /aws-glue/jobs/<job-name> --follow

# View Lambda logs
aws logs tail /aws/lambda/<function-name> --follow

# Query logs with CloudWatch Insights
aws logs start-query \
    --log-group-name /aws-glue/jobs/<job-name> \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

## 🔒 Security Features

- **S3 Encryption**: SSE-S3 encryption at rest
- **IAM Roles**: Least-privilege access for each service
- **S3 Block Public Access**: Enabled on all buckets
- **VPC Endpoints**: Optional private connectivity
- **Versioning**: Enabled for data protection
- **CloudTrail**: API activity logging (optional)

## 💡 Cost Optimization Strategies

1. **Storage Tiering**: Automatic lifecycle policies (30d → IA, 90d → Glacier)
2. **Incremental Processing**: Job bookmarks process only new data
3. **Parquet + Snappy**: 70-80% compression vs CSV
4. **Partition Pruning**: Reduce Athena scanned data by 90%+
5. **Right-Sized Resources**: Optimized Glue worker configuration
6. **Serverless**: No idle resource costs

**Estimated Monthly Cost**: $22-164 (depending on data volume)

See [COST_OPTIMIZATION.md](docs/COST_OPTIMIZATION.md) for detailed analysis.

## 🧪 Testing

### Test the Pipeline

```bash
# 1. Upload test data
aws s3 cp sample-data/csv/test.csv s3://YOUR-BUCKET/raw/taxi_trips/

# 2. Monitor Lambda execution
aws logs tail /aws/lambda/YOUR-LAMBDA-FUNCTION --follow

# 3. Check Glue job status
aws glue get-job-runs --job-name YOUR-JOB-NAME --max-results 1

# 4. Query results in Athena
aws athena start-query-execution \
    --query-string "SELECT COUNT(*) FROM processed_taxi_trips WHERE year=2024" \
    --result-configuration OutputLocation=s3://YOUR-ATHENA-BUCKET/
```

## 📚 Documentation

- **[AWS Setup Guide](AWS_SETUP_GUIDE.md)** - Complete manual setup instructions ⭐
- [Architecture Documentation](docs/ARCHITECTURE.md) - Detailed system design
- [Cost Optimization Guide](docs/COST_OPTIMIZATION.md) - Cost analysis and savings
- [Interview Preparation Guide](docs/INTERVIEW_GUIDE.md) - Technical deep-dive for interviews

## 🎯 Use Cases

This architecture is suitable for:
- **Batch Analytics**: Daily/hourly aggregations and reporting
- **Data Warehousing**: Cost-effective alternative to Redshift
- **ML Feature Engineering**: Prepare data for machine learning
- **Business Intelligence**: QuickSight dashboards and reports
- **Data Archive**: Long-term storage with lifecycle policies

## 🔧 Customization

### Change Dataset
1. Modify Glue job scripts for your schema
2. Update partition strategy as needed
3. Adjust data quality rules

### Scale Resources
1. In AWS Glue console, edit your ETL job
2. Increase worker type: G.1X → G.2X (for larger workloads)
3. Increase number of workers: 2 → 5 (for more parallelism)
4. Adjust timeout if needed

### Add New Analytics Tables
1. Create transformation logic in `processed_to_curated.py`
2. Run Glue crawler to catalog new tables
3. Create Athena queries for analysis

## 🧹 Cleanup

To destroy all resources and avoid charges, follow the cleanup instructions in `AWS_SETUP_GUIDE.md`.

**Warning**: This will permanently delete all data and infrastructure.

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Data Ingestion Latency | < 1 minute (event-driven) |
| ETL Processing Time | 2-10 minutes (typical batch) |
| Athena Query Performance | Sub-second to seconds |
| Storage Compression Ratio | 70-80% (Parquet vs CSV) |
| Cost per GB Processed | $0.01-0.05 |

## 💡 Why I Built This

I wanted to move beyond basic tutorials and build something that demonstrates real-world data engineering skills. This project showcases:

- **Production-grade architecture** - Not just a proof of concept
- **Cost optimization** - 99% compute savings through job bookmarks
- **Automation** - Event-driven, self-maintaining system
- **Scalability** - Handles millions of records efficiently
- **Best practices** - Monitoring, security, documentation

The goal was to create a portfolio project that stands out in interviews and demonstrates the kind of system I'd build professionally.

## 🎓 Learning Outcomes

By building this project, you demonstrate expertise in:

1. **AWS Services**: Glue Data Catalog, Glue Crawlers, S3, Lambda, Athena, EventBridge, CloudWatch, SNS, IAM
2. **Metadata Management**: Centralized catalog, automated schema discovery, job bookmarks
3. **Data Engineering**: ETL pipelines, data quality, partitioning strategies, incremental processing
4. **Apache Spark**: Distributed data processing with PySpark
5. **Event-Driven Architecture**: Serverless orchestration patterns
6. **Cost Optimization**: Storage tiering, compression, partition pruning, incremental processing
7. **Production Best Practices**: Monitoring, alerting, security, error handling

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:
- Open issues for bugs or improvements
- Submit pull requests with enhancements
- Share your own implementations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Built with ☕ and lots of AWS Console clicking!

**Connect with me:**
- LinkedIn: [Your LinkedIn](https://www.linkedin.com/in/tanuja-gadhe-84a041220/)
- Email: tanujagadhe18@gmail.com

## 🙏 Acknowledgments

- NYC Taxi & Limousine Commission for providing the public dataset
- AWS documentation and community forums for guidance
- Data engineering community for best practices and inspiration

**Special thanks to everyone who reviewed and provided feedback on this project!**

## 📞 Support

For questions or issues:
1. Check `AWS_SETUP_GUIDE.md` for setup help
2. Review [AWS Glue documentation](https://docs.aws.amazon.com/glue/)
3. Open an issue on GitHub

---

**⭐ If you find this project helpful, please give it a star!**
