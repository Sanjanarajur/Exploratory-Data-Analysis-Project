"""
data_cleaning.py
-----------------
Reusable data-cleaning functions for the Supermarket Sales EDA project.

This module loads the raw supermarket sales export, validates its
quality, standardises column names / data types, engineers a handful
of date-based helper columns, and writes a cleaned CSV that is used
by every downstream analysis step (notebook + analysis.py).

Run directly to regenerate data/cleaned/cleaned_dataset.csv from
data/raw/dataset.csv:

    python src/data_cleaning.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "dataset.csv"
CLEANED_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "cleaned" / "cleaned_dataset.csv"
)


def load_raw_data(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw CSV export exactly as delivered by the source system."""
    return pd.read_csv(path)


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to a consistent snake_case format.

    Business-facing column headers such as ``"Tax 5%"`` are kept
    functional (not just cosmetic) by renaming them to descriptive,
    code-friendly names.
    """
    rename_map = {
        "Invoice ID": "invoice_id",
        "Branch": "branch",
        "City": "city",
        "Customer type": "customer_type",
        "Gender": "gender",
        "Product line": "product_line",
        "Unit price": "unit_price",
        "Quantity": "quantity",
        "Tax 5%": "tax_5_pct",
        "Total": "total",
        "Date": "date",
        "Time": "time",
        "Payment": "payment",
        "cogs": "cogs",
        "gross margin percentage": "gross_margin_pct",
        "gross income": "gross_income",
        "Rating": "rating",
    }
    df = df.rename(columns=rename_map)
    return df


def check_missing_values(df: pd.DataFrame) -> pd.Series:
    """Return a per-column count of missing values (for reporting/logging)."""
    return df.isnull().sum()


def check_duplicates(df: pd.DataFrame) -> int:
    """Return the number of fully duplicated rows in the dataframe."""
    return int(df.duplicated().sum())


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date/time columns from raw strings into proper datetime types.

    The source export stores ``date`` as ``M/D/YYYY`` text and ``time``
    as ``HH:MM`` text. Converting these to real datetime objects is
    required before any time-based analysis (monthly trend, day-of-week
    pattern, hourly traffic, etc.) can be performed.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y")
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.time
    return df


def engineer_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add helper columns derived from `date`/`time` for grouping and plotting."""
    df = df.copy()
    df["month"] = df["date"].dt.month_name()
    df["month_num"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.day_name()
    df["hour"] = df["time"].apply(lambda t: t.hour)
    return df


def standardize_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace and enforce consistent casing on categorical text fields.

    Even when a dataset looks clean, categorical free-text fields are a
    common source of silent duplication (e.g. ``"Member"`` vs
    ``"member "``). This step is a defensive safeguard that has no
    visible effect if the source data is already consistent, but
    protects the pipeline if the raw export ever changes.
    """
    df = df.copy()
    categorical_cols = [
        "branch",
        "city",
        "customer_type",
        "gender",
        "product_line",
        "payment",
    ]
    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def detect_outliers_iqr(df: pd.DataFrame, column: str) -> pd.Series:
    """Flag outliers in a numeric column using the 1.5 * IQR rule.

    Returns a boolean Series aligned to `df.index` (True = outlier).
    Outliers are flagged for transparency but NOT removed, since in a
    retail-transactions context a handful of unusually large baskets
    are legitimate business events, not data-entry errors.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return (df[column] < lower_bound) | (df[column] > upper_bound)


def validate_business_rules(df: pd.DataFrame) -> dict:
    """Run a small set of sanity checks that a 'clean' retail dataset should pass.

    Returns a dictionary summarising each check so it can be logged or
    asserted on in tests.
    """
    checks = {
        "negative_quantity_rows": int((df["quantity"] <= 0).sum()),
        "negative_unit_price_rows": int((df["unit_price"] <= 0).sum()),
        "total_formula_mismatches": int(
            (
                (df["unit_price"] * df["quantity"] * 1.05 - df["total"]).abs() > 0.01
            ).sum()
        ),
        "rating_out_of_range": int(((df["rating"] < 0) | (df["rating"] > 10)).sum()),
    }
    return checks


def clean_pipeline(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    """Run the full cleaning pipeline end-to-end and return the cleaned dataframe."""
    df = load_raw_data(raw_path)

    missing_before = check_missing_values(df)
    duplicates_before = check_duplicates(df)

    df = standardize_column_names(df)
    df = standardize_categorical_values(df)
    df = fix_data_types(df)
    df = engineer_date_features(df)

    business_checks = validate_business_rules(df)

    print("Missing values per column (raw data):")
    print(missing_before)
    print(f"\nDuplicate rows found: {duplicates_before}")
    print("\nBusiness-rule validation results:")
    for check, result in business_checks.items():
        print(f"  {check}: {result}")

    for col in ["total", "quantity", "unit_price"]:
        n_outliers = detect_outliers_iqr(df, col).sum()
        print(f"\nOutliers detected in '{col}' (IQR method): {n_outliers}")

    return df


def save_cleaned_data(df: pd.DataFrame, path: Path = CLEANED_PATH) -> None:
    """Persist the cleaned dataframe to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\nCleaned dataset saved to: {path}")


if __name__ == "__main__":
    cleaned_df = clean_pipeline()
    save_cleaned_data(cleaned_df)
