# Data Quality Report

Run: 2026-10-02 05:45:18  

**54 pass · 2 warn · 9 fail** out of 65 checks


## Summary by layer

| Layer | Pass | Warn | Fail |
|---|---|---|---|
| Duplicate records | 3 | 0 | 0 |
| Null checks | 12 | 0 | 1 |
| Referential integrity | 3 | 0 | 0 |
| Date validity | 4 | 0 | 0 |
| Negative values | 12 | 0 | 0 |
| Duplicate joins | 3 | 1 | 0 |
| Unexpected row multiplication | 4 | 0 | 0 |
| KPI reconciliation | 7 | 0 | 1 |
| Source-to-report validation | 6 | 1 | 7 |

## Failures and warnings

| ID | Severity | Table | Rule | Observed | Expected | Detail |
|---|---|---|---|---|---|---|
| DQ015 | critical | campaign_data | column 'platform' exists | nan | nan | column missing from table |
| DQ055 | critical | powerbi | Power BI [total_spend] == source (±0.5%) | 62681853.33 | 29128207786.129997 | relative diff 99.78% |
| DQ056 | critical | powerbi | Power BI [roi] == source (±0.5%) | 1365.428105 | 1.940457 | relative diff 70266.31% |
| DQ057 | critical | powerbi | Power BI [roas] == source (±0.5%) | 1366.428105 | 2.940457 | relative diff 46369.92% |
| DQ058 | critical | powerbi | Power BI [total_impressions] == source (±0.5%) | 16666500000.0 | 9176717247.0 | relative diff 81.62% |
| DQ062 | critical | powerbi | Power BI [avg_ctr] == source (±0.5%) | 0.14944 | 0.08504 | relative diff 75.73% |
| DQ064 | critical | powerbi | Power BI [cpa] == source (±0.5%) | 0.365464 | 169.830806 | relative diff 99.78% |
| DQ065 | critical | powerbi | Power BI [net_profit] == source (±0.5%) | 85650283118.19986 | 56522038284.87 | relative diff 51.53% |
| DQ051 | high | churn_predictions | churn minority class >= 5% | 0.000216 | 0.05 | class shares {1: 0.99978, 0: 0.00022} |
| DQ039 | warning | campaign_data | channel_used distinct <= 10 | 156.0 | 10.0 | multi-valued attribute? split into a bridge table |
| DQ052 | warning | campaign_data | target_audience == customer_segment (mismatch <= 5%) | 0.8007 | 0.05 |  |