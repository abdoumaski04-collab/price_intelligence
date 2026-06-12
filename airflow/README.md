# Real-Time E-commerce Price Intelligence Platform

## Architecture
Scrapy → Kafka → Apache NiFi → Google Cloud Bigtable → dbt → BigQuery → Airflow

## Stack Technique
| Layer | Technologies |
|-------|-------------|
| Scraping | Scrapy (Jumia, IKEA, Kitea) |
| Streaming | Apache Kafka, Apache NiFi |
| Storage | Google Cloud Bigtable |
| Transformation | dbt (10 modeles, 21 tests) |
| Orchestration | Apache Airflow (5 DAGs) |
| Cloud | GCP (Bigtable, BigQuery) |

## Sources de donnees
- Jumia : 167,000+ produits
- IKEA Maroc : 5,700+ produits
- Kitea : 4,700+ produits

## DAGs Airflow
- jumia_pipeline
- ikea_pipeline
- kitea_pipeline
- bigtable_pipeline
- weekly_report_pipeline
