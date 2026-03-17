# 📥 Data Ingestion — Concepts & Best Practices

> Personal notes from building the COVID Data Pipeline project.
> Reference this before any DE interview or pipeline design discussion.

---

## What is Data Ingestion?

Ingestion = bringing data from its source into your pipeline's control.

The moment data moves from a static source (CSV, DB, API, Kafka topic)
into an active object your code can work with — that handoff is ingestion.

**Analogy:** Raw materials sitting outside a factory = useless.
The moment a truck brings them inside the factory gate = ingestion.
What happens inside (cleaning, shaping) = transformation.

---

## Real Production Ingestion Flow

```
Bank Transaction API  ──→
MySQL Production DB   ──→   Ingestion Layer   ──→   Raw S3 / Data Lake
Kafka Event Stream    ──→
Salesforce CRM        ──→
```

---

## Your Project vs Real World

| Your Project              | Real Production                          |
|---------------------------|------------------------------------------|
| `pd.read_csv()`           | Airbyte / Kafka consumer / API call      |
| `data/raw/` folder        | S3 raw bucket / Data Lake landing zone   |
| `os.path.exists` check    | Pipeline health monitoring / alerts      |
| Running manually          | Scheduled via Airflow every hour         |

---

## Best Practices in Production Ingestion

### 1. Source Connectivity & Authentication
- Verify you can reach the source before reading data
- Store credentials in a secrets manager (AWS Secrets Manager, HashiCorp Vault)
- **Never hardcode credentials**
- If connection fails → alert immediately, don't proceed

```
✔ Connected to source
✘ Connection failed → alert → retry → fail gracefully
```

---

### 2. Data Availability Check
- Just because you connected doesn't mean data is there
- Check if the API returned 0 records, or the source table has no new rows
- Upstream system may have failed silently

**Real scenario:** Bank batch job runs at 2am, your pipeline at 3am.
If bank job failed → you connect fine but pull 0 rows → silent bad load.

```
✔ Row count > 0 → proceed
✘ Row count = 0 → alert "No data received from source"
```

---

### 3. Schema Validation
- Verify incoming data has the structure you expect
- Check all expected columns are present
- Check data types are correct (date as string? number as text?)

**Real scenario:** Source team renames `customer_id` to `cust_id` without
telling you. Your pipeline silently breaks or loads nulls.

```
Expected columns: [date, country, new_cases, new_deaths]
✔ All present → proceed
✘ Column missing → alert "Schema mismatch detected"
```

---

### 4. Data Quality Checks
- Are critical columns (primary keys, dates) null?
- Are values in a valid range? (negative case counts don't make sense)
- Are there duplicate records?
- Is the date range what you expected?

```
✔ No nulls in key columns
✔ No duplicate primary keys
✔ Values within expected range
✘ Any failure → quarantine the data, alert, don't load
```

---

### 5. Watermarking / Incremental Load Tracking
- Track what you've already ingested so you don't re-process old data
- Store the last ingested timestamp or ID in a metadata table
- Next run picks up only from where you left off

```
Last run  : 2024-01-15 03:00:00
This run  : Pull records where updated_at > 2024-01-15 03:00:00
```

---

### 6. Raw Data Preservation
- Always save raw data exactly as received before doing anything to it
- Write to a raw layer (S3 bucket, raw DB schema, `data/raw/`)
- **Never modify raw data — it is your recovery point**

---

### 7. Logging
- Log when ingestion started and ended
- Log how many records were pulled
- Log how long it took
- Log what failed and why

Tools: Apache Airflow logs, AWS CloudWatch, Datadog

---

### 8. Alerting & Notifications
- Alert the right people immediately when something goes wrong
- Channels: Email / Slack / PagerDuty
- Alert on: zero records, schema mismatch, connection failure
- Never let silent failures go unnoticed

---

### 9. Idempotency
- If the pipeline runs twice by mistake, it should produce the same result
- No duplicate data should be created
- Use upserts, `INSERT OR REPLACE`, or truncate-and-reload strategies
- Critical in production where retries are common

---

## ✅ The Mental Checklist — Interview Design Questions

When asked to design an ingestion layer, walk through this out loud:

```
1.  Where is the data coming from?          → source type (API, DB, Kafka, file)
2.  How do I connect securely?              → auth + secrets manager
3.  Is the source available right now?      → connectivity check
4.  Did it actually produce data?           → availability / row count check
5.  Does it look like what I expect?        → schema validation
6.  Is the data quality acceptable?         → null checks, range checks, duplicates
7.  What do I do if any check fails?        → alerting + graceful failure strategy
8.  Where do I land the raw data?           → raw storage layer (S3, data/raw/)
9.  How do I track what I've processed?     → watermarking / incremental load
10. What if this pipeline runs twice?       → idempotency strategy
```

---

## Tools Used in Production Ingestion

| Purpose               | Tools                                      |
|-----------------------|--------------------------------------------|
| Real-time streams     | Apache Kafka, AWS Kinesis                  |
| Batch ingestion       | Airbyte, Apache NiFi, AWS Glue             |
| Cloud pipelines       | Azure Data Factory, Google Dataflow        |
| Orchestration         | Apache Airflow, Prefect, Dagster           |
| Secrets management    | AWS Secrets Manager, HashiCorp Vault       |
| Monitoring/Alerting   | Datadog, AWS CloudWatch, PagerDuty         |

---

*Notes built during COVID Pipeline project — March 2026*
