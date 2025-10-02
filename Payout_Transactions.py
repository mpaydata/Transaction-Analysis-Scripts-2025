#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
payout_report
=============

This module processes Payout transaction data for reporting.

It provides functionality to:
- Load and clean payout transaction data.
- Convert timestamps to Africa/Lagos timezone.
- Filter only NGN transactions with successful status.
- Compute charges, partner costs, profits, and gain status.
- Export results to a structured CSV file.
"""

import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


def Payout_Transaction(data_path: str, output_path: str = "payout_report.csv") -> pd.DataFrame:
    """
    Process payout transactions and export results.

    Parameters
    ----------
    data_path : str
        Path to the input CSV file containing raw payout transaction data.
    output_path : str, optional
        File path to save the processed CSV file. Defaults to 'payout_report.csv'.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame containing cleaned and enriched payout transaction data.

    Notes
    -----
    - Input data is expected to have at least the following columns:
      ['id', 'session_id', 'time', 'userId', 'transaction_reference', 
       'amount', 'charge', 'status', 'currency']
    - Only NGN transactions with status 'success' are processed.
    - Partner cost is currently set as a flat 10.00 per successful transaction.
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

    # Filter NGN transactions
    df_ngn = data.loc[data["currency"] == "NGN"]

    # Drop irrelevant columns
    df_ngn = df_ngn.drop(["id", "session_id"], axis=1, errors="ignore")

    # Ensure numeric types
    df_ngn["userId"] = pd.to_numeric(df_ngn["userId"], errors="coerce").astype("Int64")
    df_ngn["amount"] = pd.to_numeric(df_ngn["amount"], errors="coerce")
    df_ngn["charge"].fillna(0.0, inplace=True)

    # Add metadata
    df_ngn["account_type"] = "Payout"
    df_ngn["channel"] = "Payout"
    df_ngn["payment_rail"] = "Payout"
    df_ngn["settled_amount"] = 0.00

    # Rename columns for consistency
    df_ngn.rename(
        columns={
            "userId": "merchantId",
            "amount": "transaction_amount",
            "time": "created_at",
        },
        inplace=True,
    )

    # Partner cost (flat assumption here)
    df_ngn.loc[df_ngn["status"] == "success", "partner_cost"] = 10.00

    # Keep only successful transactions
    df = df_ngn.loc[df_ngn["status"] == "success"]

    # Add transaction type
    df["type"] = "TRANSFER"

    # Use charge as pct_charged for reporting (no percentage calculation in payout)
    df["pct_charged"] = df["charge"]

    # Profit computation
    df["profit"] = (df["charge"] - df["partner_cost"]).round(1)

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
