# 🧹 Data Filtering & Cleaning — Concepts & Best Practices

> Personal notes from building the COVID Data Pipeline project.
> Reference this before any DE interview or pipeline design discussion.

---

## What is Data Filtering & Cleaning?

Filtering = removing unwanted rows based on business rules.
Cleaning = fixing data quality issues (nulls, duplicates, anomalies).

The moment raw, messy data becomes structured, validated, consistent data
ready for analysis — that transformation is the filtering/cleaning stage.

**Analogy:** Raw materials arrive at factory (ingestion).
Workers sort (filter), fix defects (clean), organize (transform).
Only then does it go to production line (analytics).

---

## Real Production Filtering Flow

```
Raw Data Lake (S3/Data Warehouse)  ──→
                                        Filtering Layer   ──→   Cleaned Data (Silver)
                                        (Remove noise)
                                        (Fix quality)
                                        (Deduplicate)
                                        (Validate rules)
```

---

## Your Project vs Real World

| Your Project                      | Real Production                           |
|-----------------------------------|------------------------------------------|
| Filter 3 countries manually       | Dynamic filters from config/metadata      |
| Drop N/A in hardcoded columns     | Quality rules from data catalog           |
| Save to CSV                       | Load to Parquet/Delta Lake with versioning|
| Manual validation prints          | Automated data quality framework (Great Expectations) |
| Running manually                  | Scheduled in Airflow with SLA monitoring  |

---

## Best Practices in Production Filtering

### 1. Define Business Rules Explicitly
- Never hardcode filter logic like `COUNTRIES = ['India', 'US', 'UK']`
- Store rules in a config file or metadata table
- This allows business teams to update filters without touching code

```python
# ❌ Bad
COUNTRIES_TO_KEEP = ['India', 'US', 'United Kingdom']

# ✔ Good
config = load_config('filtering_rules.yaml')  # Business owns this
COUNTRIES_TO_KEEP = config['countries_to_filter']
```

**Real scenario:** Marketing wants to add Germany to analysis.
Bad approach: Engineer must redeploy code.
Good approach: Business updates config in 5 minutes.

---

### 2. Track Data Quality Metrics
- **Before filtering:** rows, columns, nulls, duplicates
- **After filtering:** same metrics again
- **Data loss reporting:** How many rows were removed? Why?
- **Alert on unexpected changes:** If 80% of data is filtered out (vs usual 5%), something broke

```
Before: 35,156 rows
Filtered by country: -34,592 rows
Cleaned nulls: -0 rows
After: 564 rows

Data loss: 98.4% — Flag this! Did we break something?
```

---

### 3. Handle Nulls Strategically
- **Never silently drop nulls** — log what you're removing
- Different strategies for different columns:
  - **Critical columns (PK, dates):** Drop rows
  - **Non-critical columns (notes, descriptions):** Fill with 'N/A' or mean/median
  - **Date columns:** Maybe pad with data load date?

```python
# ❌ Silent failure
df = df.dropna()  # 50% of data disappeared, nobody knows why

# ✔ Planned & logged
nulls_before = df.isnull().sum()
df = df.dropna(subset=['Date', 'Country', 'Confirmed'])
nulls_removed = df.isnull().sum() - nulls_before
log(f"Removed {len(df) - len(df_after)} rows with nulls")
```

---

### 4. Deduplicate with Care
- Identify duplicate key (usually: date + country + region)
- Decide which copy to keep (first? last? most recent?)
- Log how many duplicates you found and removed

```python
# ❌ Blindly remove duplicates
df = df.drop_duplicates()  # Which copy did we keep? Unknown.

# ✔ Intentional deduplication
duplicates = df.duplicated(subset=['Date', 'Country/Region'], keep=False)
print(f"Found {duplicates.sum()} duplicate rows")
df = df.drop_duplicates(subset=['Date', 'Country/Region'], keep='last')
log(f"Kept last occurrence, removed {duplicates.sum() - df.shape[0]} rows")
```

---

### 5. Validate Output Against Rules
After filtering, verify the data still meets expectations:
- No nulls in critical columns
- No negative values where they shouldn't exist (negative cases?)
- Date range is reasonable
- Country names are valid
- Value ranges are sensible

```python
# Data Validation Checks
assert df['Confirmed'].min() >= 0, "Negative confirmed cases detected!"
assert df['Date'].isnull().sum() == 0, "Nulls in Date column after filtering!"
assert df['Country/Region'].isin(['India', 'US', 'United Kingdom']).all()
print("✔ All validation checks passed")
```

---

### 6. Preserve Audit Trail
- Keep: original record count, filtered record count, removal reason
- Store metadata: who ran this? when? what version of rules?
- If issues found later, you can trace back to which version filtered the data

```python
metadata = {
    'run_timestamp': datetime.now(),
    'rows_input': 35156,
    'rows_output': 564,
    'rows_removed': 34592,
    'filter_version': '1.2',
    'filtered_by': 'ETL_SERVICE',
    'rule_set': 'prod_covid_v2'
}
save_metadata(metadata)  # Store in metadata table or manifest file
```

---

### 7. Handle Outliers & Anomalies
- Flag extreme values for review before removing
- Don't silently drop data that looks "wrong"
- Business may need to investigate (Is it a bug? Or real event?)

```python
# Alert on anomalies
max_cases = df['Confirmed'].max()
if max_cases > EXPECTED_MAX:
    log(f"WARNING: Max confirmed cases ({max_cases}) exceeds threshold")
    alert_business_team()
    
# Don't remove, just flag
df['is_anomaly'] = df['Confirmed'] > ANOMALY_THRESHOLD
anomaly_count = df['is_anomaly'].sum()
if anomaly_count > 0:
    print(f"Found {anomaly_count} anomalies — review before proceeding")
```

---

### 8. Test Filter Logic with Edge Cases
- What if a country name is misspelled in the source?
- What if all rows have nulls in a critical column?
- What if the date column is in a different format?
- What if the input file is empty?

```python
# Test cases
def test_filter_no_data():
    df_empty = pd.DataFrame()
    result = filter_data(df_empty)
    assert len(result) == 0, "Empty input should yield empty output"

def test_filter_all_nulls():
    df_nulls = pd.DataFrame({'Date': [None, None], 'Confirmed': [None, None]})
    result = filter_data(df_nulls)
    assert len(result) == 0, "AllNULL data should be filtered out"

def test_filter_invalid_country():
    df = pd.DataFrame({'Country/Region': ['Narnia', 'Atlantis']})
    result = filter_data(df)
    assert len(result) == 0, "Invalid countries should be filtered"
```

---

### 9. Document Filtering Decisions
- Why are you filtering on these specific columns?
- Why drop nulls vs. fill them?
- What's the business reason for removing 98% of data?
- Link back to requirements document

```markdown
# Filtering Logic for COVID Pipeline

## Countries
- Analysis scope: India, US, UK only
- Reason: Regional focus for pilot
- Owner: Analytics team
- Update frequency: Quarterly review

## Null Handling
- Critical columns: Date, Country/Region, Confirmed
  - Action: Drop rows with nulls in these
  - Rationale: Can't analyze without core metrics
- Non-critical: Recovered, Active
  - Action: Fill with 0
  - Rationale: Not essential; safe to assume no data = not reported
```

---

### 10. Monitor Filter Efficiency
- Is filtering taking too long? Maybe you need indexing in source DB
- Are you filtering before or after joins? (Filter early = faster)
- Can you push filtering to source system? (Push-down predicates)

```python
# ❌ Slow: Load all 35M rows, then filter
df = pd.read_csv('huge_file.csv')  # Takes 5 minutes
df = df[df['Country'] == 'India']  # Filter after load

# ✔ Faster: Filter while reading
df = pd.read_csv('huge_file.csv', 
                  usecols=['Date', 'Country', 'Confirmed'],  # Read only needed columns
                  chunksize=10000)  # Stream in chunks
df = [chunk[chunk['Country'] == 'India'] for chunk in df]
```

---

## ✅ The Mental Checklist — Interview Design Questions

When asked to design a filtering layer, walk through this out loud:

```
1.  What are the filtering criteria?              → business rules, config-driven
2.  Where do filter rules live?                   → config file, metadata table, or code?
3.  How do I handle nulls?                        → drop, fill, or flag?
4.  How do I find & handle duplicates?            → key columns, which copy to keep?
5.  What data quality checks run after filtering? → validation rules
6.  What do I log/alert on?                       → data loss, anomalies, failures
7.  How do I audit what was filtered?             → metadata, metrics, trace
8.  What if filtering removes 80% of data?        → alert or proceed?
9.  How do I test edge cases?                     → empty input, all nulls, etc.
10. Is filtering the bottleneck?                  → performance optimization needed?
```

---

## Tools Used in Production Filtering

| Purpose               | Tools                                      |
|-----------------------|--------------------------------------------|
| Data quality checks   | Great Expectations, dbt, Soda SQL          |
| ETL orchestration     | Apache Airflow, dbt, Prefect               |
| Config management     | YAML/JSON configs, DVC, Parameter stores   |
| Logging/Monitoring    | Datadog, Segment, CloudWatch               |
| Testing              | pytest, dbt tests, SQL unit tests          |
| Cloud data cleaning   | Snowflake (data cleaning functions),       |
|                       | BigQuery (STRUCT/ARRAY functions)         |

---

## Common Mistakes in Production Filtering

| Mistake | Impact | Fix |
|---------|--------|-----|
| Hardcoded filter values | Can't update without code deploy | Use config files |
| Silent data loss | Nobody knows what happened | Log every removal |
| No deduplication | Duplicate rows in analytics | Identify key, deduplicate |
| Blindly drop nulls | Important data lost | Strategic null handling |
| No validation after filter | Bad data goes downstream | Add assertion checks |
| No alerting on anomalies | Broken data silently propagates | Flag + alert on outliers |

---

*Notes built during COVID Pipeline project — April 2026*
