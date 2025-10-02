#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
dynamic_account_report
======================

This module processes Dynamic Account transaction data for reporting.

It provides functionality to:
- Load and clean dynamic account transaction data.
- Convert timestamps to Africa/Lagos timezone.
- Filter NGN transactions with successful status ("Done").
- Compute charges, partner costs, profits, and percentages.
- Classify transactions into Profit, Loss, or NLNP categories.
- Export results to a structured CSV file.

"""

import warnings
import numpy as np
import pandas as pd
from utils import partner_charge

warnings.filterwarnings("ignore")


def Dynamic_Account_Transaction(data_path: str, output_path: str = "dynamic_report.csv") -> pd.DataFrame:
    """
    Process Dynamic Account transactions and export results.

    Parameters
    ----------
    data_path : str
        Path to the input CSV file containing raw transaction data.
    output_path : str, optional
        File path to save the processed CSV file. Defaults to 'dynamic_report.csv'.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame containing cleaned and enriched transaction data.

    Notes
    -----
    - Input data is expected to have at least the following columns:
      ['user_id', 'internal_ref', 'type', 'transaction_amount', 'settled_amount', 
       'charge', 'status', 'currency', 'time']
    - Only NGN transactions with status 'Done' are processed.
    - The `partner_charge` function is applied to each transaction amount to determine partner cost.
    """

    # Load data
    data = pd.read_csv(data_path)

    # Convert UNIX time to Africa/Lagos timezone
    data["time"] = (
        pd.to_datetime(data["time"], unit="s", utc=True)
        .dt.tz_convert("Africa/Lagos")
        .dt.tz_localize(None)
    )
    data["transaction_date"] = pd.to_datetime(data["time"]).dt.date

    # Sort chronologically
    data = data.sort_values(by=["time"])

    # Filter NGN transactions
    df_ngn = data.loc[data["currency"] == "NGN"]

    # Keep only required columns
    df_ngn = df_ngn[
        [
            "user_id",
            "internal_ref",
            "type",
            "transaction_amount",
            "settled_amount",
            "charge",
            "status",
            "currency",
            "transaction_date",
            "time",
        ]
    ]

    # Fill missing values with zeros
    df_ngn.fillna(0.00, inplace=True)

    # Keep only successful transactions
    df = df_ngn.loc[df_ngn["status"] == "Done"]

    # Add metadata
    df["account_type"] = "Dynamic"
    df["channel"] = "Collection"
    df["payment_rail"] = "Checkout_Collection"

    # Rename columns for consistency
    df.rename(
        columns={
            "user_id": "merchantId",
            "internal_ref": "transaction_reference",
            "time": "created_at",
        },
        inplace=True,
    )

    # Partner cost calculation
    df["partner_cost"] = df["transaction_amount"].apply(partner_charge)

    # Profit computation
    df["profit"] = (df["charge"] - df["partner_cost"]).round(2)

    # Percentage charged
    df["pct_charged"] = ((df["charge"] * 100) / df["transaction_amount"]).round(3)

    # Profit classification
    df["gain_status"] = ""
    df.loc[df["profit"] < 0, "gain_status"] = "Loss"
    df.loc[df["profit"] == 0, "gain_status"] = "NLNP"
    df.loc[df["profit"] > 0, "gain_status"] = "Profit"

    # Select final output columns
    processed = df[
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
