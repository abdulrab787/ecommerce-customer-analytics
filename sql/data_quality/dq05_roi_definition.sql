-- The source ROI column must equal (revenue - cost*conversions) / (cost*conversions).
-- This is the evidence that acquisition_cost is a cost PER CONVERSION.
-- Inputs are rounded to 2dp, so the tolerance is max(0.01, 0.1% of the value) - the same rule as
-- src/data_quality/checks.py::row_level_formula (large ROIs such as 60x differ by up to ~0.03).
WITH f AS (
    SELECT ROI, (Revenue - Acquisition_Cost * Conversions) / (Acquisition_Cost * Conversions) AS roi_formula
    FROM raw_campaigns
)
SELECT 'SQL-DQ05' AS check_id, 'raw ROI matches per-conversion cost definition' AS check_name,
       COUNT(*) AS failing_rows
FROM f
WHERE ABS(ROI - roi_formula) > GREATEST(0.01, ABS(roi_formula) * 0.001);
