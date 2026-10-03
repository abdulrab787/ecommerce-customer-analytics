-- Raw dates must parse as dd-mm-yyyy and fall between 2024-01-01 and today.
SELECT 'SQL-DQ04' AS check_id, 'raw dates parse (dd-mm-yyyy) and are in range' AS check_name,
       COUNT(*) AS failing_rows
FROM raw_campaigns
WHERE TRY_STRPTIME("Date", '%d-%m-%Y') IS NULL
   OR TRY_STRPTIME("Date", '%d-%m-%Y') < TIMESTAMP '2024-01-01'
   OR TRY_STRPTIME("Date", '%d-%m-%Y') > CURRENT_DATE;
