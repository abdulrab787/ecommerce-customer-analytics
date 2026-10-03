# Data Quality Report

Run: 2026-10-03 05:58:55  

**63 pass · 2 warn · 0 fail** out of 65 checks


## Summary by layer

| Layer | Pass | Warn | Fail |
|---|---|---|---|
| Duplicate records | 3 | 0 | 0 |
| Null checks | 13 | 0 | 0 |
| Referential integrity | 3 | 0 | 0 |
| Date validity | 4 | 0 | 0 |
| Negative values | 12 | 0 | 0 |
| Duplicate joins | 3 | 1 | 0 |
| Unexpected row multiplication | 4 | 0 | 0 |
| KPI reconciliation | 8 | 0 | 0 |
| Source-to-report validation | 13 | 1 | 0 |

## Failures and warnings

| ID | Severity | Table | Rule | Observed | Expected | Detail |
|---|---|---|---|---|---|---|
| DQ039 | warning | campaign_data | channel_used distinct <= 10 | 156.0 | 10.0 | multi-valued attribute? split into a bridge table |
| DQ052 | warning | campaign_data | target_audience == customer_segment (mismatch <= 5%) | 0.8007 | 0.05 |  |