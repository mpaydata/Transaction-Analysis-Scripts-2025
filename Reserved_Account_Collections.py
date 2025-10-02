#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reserved_account_report
=======================

This module processes Reserved Account transaction data for reporting.  

It provides functionality to:
- Load and clean raw reserved account transaction data.
- Convert timestamps to Africa/Lagos timezone.
- Compute transaction charges, partner costs, profits, and percentages.
- Classify transactions into Profit, Loss, or NLNP categories.
- Export results to a structured CSV file.
"""

import warnings
import numpy as np
import pandas as pd
from utils import partner_charge

warnings.filterwarnings("ignore")


def Reserved_account_collections(data_path: str, output_path: str = "reserved_report.csv") -> pd.DataFrame:
    """
    Process Reserved Account transactions and export results.

    Parameters
    ----------
    data_path : str
        Path to the input CSV file containing raw transaction data.
    output_path : str, optional
        File path to save the processed CSV file. Defaults to 'reserved_report.csv'.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame containing cleaned and enriched transaction data.

    Notes
    -----
    - Input data is expected to have at least the following columns:
      ['id', 'time', 'userId', 'reference', 'amount', 'amount_settled', 'transaction_reference', 'currency']
    - The `partner_charge` function is applied to each transaction amount to determine partner cost.
    """

    # Load data
    data = pd.read_csv(data_path)

    # Remove unnecessary column
    if "id" in data.columns:
        data = data.drop("id", axis=1)

    # Convert UNIX time to Africa/Lagos timezone
    data["time"] = (
        pd.to_datetime(data["time"], unit="s", utc=True)
        .dt.tz_convert("Africa/Lagos")
        .dt.tz_localize(None)
    )
    data["transaction_date"] = pd.to_datetime(data["time"]).dt.date

    # Clean up invalid rows
    data = data.dropna(subset=["userId", "reference"])
    data = data[~((data["userId"] == "") & (data["reference"] == ""))]

    # Sort chronologically
    data = data.sort_values(by=["time"])

    # Ensure numeric types
    data["userId"] = pd.to_numeric(data["userId"], errors="coerce").astype("Int64")
    data["amount"] = data["amount"].astype(float)

    # Calculate charges and percentage charged
    data["charge"] = (data["amount"] - data["amount_settled"]).round(2)
    data["pct_charged"] = ((data["charge"] * 100) / data["amount"]).round(1)

    # Identify payment rail
    data["payment_rail"] = np.where(
        (data["transaction_reference"].isna()) & (data["userId"].notna()),
        "Settlement",
        "Reserved_Account",
    )

    # Replace missing references
    data["transaction_reference"].fillna(data["reference"], inplace=True)

    # Partner cost calculation
    data["partner_cost"] = data["amount"].apply(partner_charge)

    # Add metadata
    data["type"] = "TRANSFER"
    data["account_type"] = "Reserved"
    data["channel"] = "Collection"

    # Profit computation
    data["profit"] = (data["charge"] - data["partner_cost"]).round(2)

    # Rename columns for clarity
    data.rename(
        columns={
            "userId": "merchantId",
            "amount": "transaction_amount",
            "time": "created_at",
            "amount_settled": "settled_amount",
        },
        inplace=True,
    )

    # Profit classification
    data["gain_status"] = ""
    data.loc[data["profit"] < 0, "gain_status"] = "Loss"
    data.loc[data["profit"] == 0, "gain_status"] = "NLNP"
    data.loc[data["profit"] > 0, "gain_status"] = "Profit"

    # Select final output columns
    processed = data[
        [
            "transaction_reference",
            "merchantId",
            "type",
            "currency",
            "channel",
            "account_type",
            "payment_rail",
            "transaction_amount",
            "settled_amount",
            "charge",
            "partner_cost",
            "profit",
            "pct_charged",
            "gain_status",
            "transaction_date",
            "created_at",
        ]
    ]

    # Save to CSV
    processed.to_csv(output_path, index=False)

    return processed
