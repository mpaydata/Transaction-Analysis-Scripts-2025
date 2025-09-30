Each script reads a raw CSV of transactions, performs cleaning and type conversions, derives a consistent set of reporting fields, computes partner costs and profits, classifies gain/loss status, and writes a cleaned CSV with a standardized schema:

````
transaction_reference, merchantId, type, currency, channel, account_type,
payment_rail, transaction_amount, settled_amount, charge,
partner_cost, profit, pct_charged, gain_status, transaction_date, created_at
````

Common goals across the three flows:

Ensure timestamps are converted to the Africa/Lagos timezone and made human-readable.

Coerce numeric fields safely and handle missing values.

Produce stable derived columns (partner_cost, profit, pct_charged, gain_status) using business rules.

Save a consistent CSV for downstream use.
