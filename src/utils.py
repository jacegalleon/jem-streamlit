"""
Utility functions for expense sharing and balance computation.

This module provides:
- balance computation
- DataFrame formatting for display
- settlement transaction generation
- CSV validation
- settled-item filtering
"""

import pandas as pd


def get_active_df(df):
    """
    Return only the expense rows that have NOT been marked as settled.

    If the DataFrame does not contain a "Settled" column, every row is
    treated as active (unsettled), so this is safe to call on data that
    predates the settled-item feature.

    Parameters
    ----------
    df : pandas.DataFrame
        Expense data, optionally containing a "Settled" boolean column.

    Returns
    -------
    pandas.DataFrame
        Copy of df containing only rows where "Settled" is not True.
    """
    if df is None:
        return df

    if "Settled" not in df.columns:
        return df.copy()

    settled_mask = df["Settled"].fillna(False).astype(bool)

    return df[~settled_mask].copy()


def compute_balances(df):
    """
    Compute net balances for each participant.

    Each contributor initially pays the full expense amount per item.
    Each payor then owes their proportional share based on Contribution %.

    Positive values indicate the person should receive money.
    Negative values indicate the person owes money.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns:
        - Contributor
        - Payor
        - Item
        - Amount
        - Contribution %

    Returns
    -------
    dict
        Mapping of person to net balance.
    """

    # Step 1: contributor pays ONCE per item
    balances = {}
    item_paid = (
        df.groupby(["Item", "Contributor"])["Amount"]
        .first()
        .reset_index()
    )

    for _, row in item_paid.iterrows():
        contributor = row["Contributor"]
        amount = float(row["Amount"])

        balances[contributor] = balances.get(contributor, 0) + amount

    # Step 2: deduct each payor's share
    for _, row in df.iterrows():
        payor = row["Payor"]
        amount = float(row["Amount"])
        percentage = float(row["Contribution %"])

        owed = amount * percentage
        balances[payor] = balances.get(payor, 0) - owed

    return balances


def balances_to_df(balances):
    """
    Convert balances dictionary into a sorted DataFrame.

    Parameters
    ----------
    balances : dict
        Mapping of person to net balance.

    Returns
    -------
    pandas.DataFrame
        Sorted DataFrame with columns:
        - Person
        - Net Balance
    """
    return (
        pd.DataFrame(
            [(person, amount) for person, amount in balances.items()],
            columns=["Person", "Net Balance"]
        )
        .sort_values(by="Net Balance", ascending=False)
        .reset_index(drop=True)
    )


def settle_debts(balances):
    """
    Generate minimal settlement transactions.

    Matches debtors (who owe money) with creditors (who are owed money)
    in order to minimize the number of transactions.

    Parameters
    ----------
    balances : dict
        Mapping of person to net balance.

    Returns
    -------
    pandas.DataFrame
        DataFrame with settlement instructions:
        - From (debtor)
        - To (creditor)
        - Amount (payment value)
    """
    creditors = []
    debtors = []

    for person, amount in balances.items():
        if amount > 0:
            creditors.append([person, amount])
        elif amount < 0:
            debtors.append([person, -amount])

    # ✅ Sort by largest balance first
    creditors.sort(key=lambda x: -x[1])
    debtors.sort(key=lambda x: -x[1])

    transactions = []

    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        payment = min(debt, credit)

        transactions.append({
            "From": debtor,
            "To": creditor,
            "Amount": round(payment, 2),
        })

        debtors[i][1] -= payment
        creditors[j][1] -= payment

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return pd.DataFrame(transactions)


def save_settlements(df, file_path="outputs/settlements.csv"):
    """
    Save settlement DataFrame to a CSV file.

    Automatically creates the output directory if it does not exist.

    Parameters
    ----------
    df : pandas.DataFrame
        Settlement DataFrame to be saved.

    file_path : str, optional
        Destination file path (default is "outputs/settlements.csv").
    """
    import os

    # ensure folder exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df.to_csv(file_path, index=False)


def get_person_breakdown(df, person):
    """
    Generate a detailed breakdown of a person's transactions.

    Splits activity into:
    - Credit: amounts paid as Contributor (counted once per item)
    - Debit: amounts owed as Payor (based on Contribution %)

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain:
        - Contributor
        - Payor
        - Item
        - Amount
        - Contribution %

    person : str
        Target person for breakdown.

    Returns
    -------
    pandas.DataFrame
        DataFrame with:
        - Item
        - Type ("Credit" or "Debit")
        - Amount
    """
    import pandas as pd

    records = []

    # ✅ Step 1 — Credit: count ONCE per item
    item_paid = (
        df.groupby(["Item", "Contributor"])["Amount"]
        .first()
        .reset_index()
    )

    for _, row in item_paid.iterrows():
        contributor = row["Contributor"]
        item = row["Item"]
        amount = float(row["Amount"])

        if contributor == person:
            records.append({
                "Item": item,
                "Type": "Credit",
                "Amount": amount
            })

    # ✅ Step 2 — Debit: per row
    for _, row in df.iterrows():
        payor = row["Payor"]
        item = row["Item"]
        amount = float(row["Amount"])
        percentage = float(row["Contribution %"])

        owed = amount * percentage

        if payor == person:
            records.append({
                "Item": item,
                "Type": "Debit",
                "Amount": owed
            })

    return pd.DataFrame(records)


def validate_csv(df):
    """
    Validate uploaded CSV data for correctness and consistency.

    Performs the following checks:
    - Required columns exist
    - No empty values in key fields
    - Amount values are numeric and > 0
    - Contribution % values are numeric and in decimal form (0–1)
    - Aggregated Contribution per (Item + Contributor) does not exceed 1.0

    Parameters
    ----------
    df : pandas.DataFrame
        Uploaded dataset to validate.

    Returns
    -------
    tuple (bool, str)
        - True + success message if valid
        - False + formatted error message if invalid
    """

    required_cols = ["Contributor", "Item", "Amount", "Payor", "Contribution %"]

    # ✅ 1. Check required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return False, f"❌ Missing required columns: {', '.join(missing_cols)}"

    df_check = df.copy()

    # ✅ 2. Clean text fields
    df_check["Contributor"] = df_check["Contributor"].astype(str).str.strip()
    df_check["Payor"] = df_check["Payor"].astype(str).str.strip()
    df_check["Item"] = df_check["Item"].astype(str).str.strip()

    # ✅ 3. Convert numeric fields
    df_check["Amount"] = pd.to_numeric(df_check["Amount"], errors="coerce")

    df_check["Contribution %"] = (
        df_check["Contribution %"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    df_check["Contribution %"] = pd.to_numeric(df_check["Contribution %"], errors="coerce")

    # ✅ 4. Empty field validation
    if (
        (df_check["Contributor"] == "").any()
        or (df_check["Payor"] == "").any()
        or (df_check["Item"] == "").any()
    ):
        return False, "❌ Contributor, Payor, and Item cannot be empty."

    # ✅ 5. Amount validation
    if df_check["Amount"].isna().any():
        return False, "❌ Amount must contain valid numbers."

    if (df_check["Amount"] <= 0).any():
        return False, "❌ Amount must be greater than 0."

    # ✅ 6. Contribution validation
    if df_check["Contribution %"].isna().any():
        return False, "❌ Contribution % must be numeric."

    if (df_check["Contribution %"] > 1.0).any():
        return False, "❌ Contribution % only accepts decimal format (e.g., 0.25 = 25%)."

    if (df_check["Contribution %"] < 0).any():
        return False, "❌ Contribution % cannot be negative."

    # ✅ 7. Aggregated validation
    grouped = df_check.groupby(["Item", "Contributor"])["Contribution %"]
    summary = grouped.agg(["sum", "count"]).reset_index()

    invalid = summary[summary["sum"] > 1.0]

    if not invalid.empty:

        max_show = 5
        sample = invalid.head(max_show)

        lines = [
            f"Contributor: **{row['Contributor']}**, "
            f"Item: **{row['Item']}**, "
            f"Payors: **{int(row['count'])} people**, "
            f"Contribution %: **{(row['sum'] * 100):.2f}%**"
            for _, row in sample.iterrows()
        ]

        more_count = len(invalid) - max_show

        message = "❌ Total Contribution exceeds 100% for:\n\n"
        message += "\n\n".join(lines)

        if more_count > 0:
            message += f"\n\n...and {more_count} more."

        return False, message

    return True, "✅ CSV is valid"
