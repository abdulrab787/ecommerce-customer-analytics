# Legacy order-schema SQL (not runnable against this repo)

These scripts were written for a generic `customers / orders / order_items / products`
schema. **That schema does not exist in this project.** The data here is campaign-level
(see `docs/data_dictionary.md`), so these queries cannot be executed against it.

They are kept only as a record of earlier work. The SQL that actually runs on this
project's data is in `sql/campaign/` and `sql/data_quality/` (run with `python -m src.sql_runner`).
