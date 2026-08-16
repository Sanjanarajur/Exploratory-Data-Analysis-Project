"""
analysis.py
-----------
Reusable statistical-summary and visualization functions for the
Supermarket Sales EDA project.

These functions are imported by the notebook (notebooks/EDA_Project.ipynb)
so that the notebook stays focused on narrative/interpretation while the
plotting/aggregation logic lives in one tested, reusable place.

Run directly to regenerate every chart used in the report:

    python src/analysis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_PATH = PROJECT_ROOT / "data" / "cleaned" / "cleaned_dataset.csv"
VIZ_DIR = PROJECT_ROOT / "visualizations"

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["font.family"] = "DejaVu Sans"

NUMERIC_COLS = ["unit_price", "quantity", "tax_5_pct", "total", "cogs", "gross_income", "rating"]


def load_cleaned_data(path: Path = CLEANED_PATH) -> pd.DataFrame:
    """Load the cleaned dataset with correct dtypes for date/time columns."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def summary_statistics(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    """Return a descriptive-statistics table (mean, median, std, quartiles, etc.)."""
    columns = columns or NUMERIC_COLS
    stats = df[columns].describe().T
    stats["median"] = df[columns].median()
    stats["skew"] = df[columns].skew()
    return stats


def grouped_summary(df: pd.DataFrame, group_col: str, value_col: str = "total") -> pd.DataFrame:
    """Return sum / mean / count of `value_col`, grouped by `group_col`, sorted by sum."""
    summary = df.groupby(group_col)[value_col].agg(["sum", "mean", "count"])
    return summary.sort_values("sum", ascending=False)


def correlation_matrix(df: pd.DataFrame, columns=None) -> pd.DataFrame:
    """Return the Pearson correlation matrix for the given numeric columns."""
    columns = columns or NUMERIC_COLS
    return df[columns].corr()


# ---------------------------------------------------------------------------
# Visualization helpers — each saves a PNG into the appropriate subfolder
# ---------------------------------------------------------------------------


def _save(fig, subfolder: str, filename: str) -> Path:
    """Save a figure to disk without closing it.

    The figure is intentionally left open so that callers (e.g. a notebook
    cell that follows up with `plt.show()`) can still display it. When
    generating visualizations in bulk via `generate_all_visualizations`,
    open figures are cleaned up afterwards with `plt.close("all")`.
    """
    out_dir = VIZ_DIR / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    fig.savefig(out_path, bbox_inches="tight")
    return out_path


def plot_numeric_distribution(df: pd.DataFrame, column: str, subfolder="distribution_plots"):
    """Histogram + KDE for a single numeric column."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.histplot(df[column], kde=True, bins=30, color="#4C72B0", ax=ax)
    ax.set_title(f"Distribution of {column.replace('_', ' ').title()}")
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_ylabel("Frequency")
    return _save(fig, subfolder, f"{column}_distribution.png")


def plot_boxplot(df: pd.DataFrame, column: str, subfolder="distribution_plots"):
    """Boxplot for outlier inspection of a numeric column."""
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sns.boxplot(x=df[column], color="#DD8452", ax=ax)
    ax.set_title(f"Boxplot of {column.replace('_', ' ').title()}")
    ax.set_xlabel(column.replace("_", " ").title())
    return _save(fig, subfolder, f"{column}_boxplot.png")


def plot_categorical_count(df: pd.DataFrame, column: str, subfolder="categorical_analysis"):
    """Count plot for a categorical column."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    order = df[column].value_counts().index
    sns.countplot(y=df[column], order=order, color="#55A868", ax=ax)
    ax.set_title(f"Count of Transactions by {column.replace('_', ' ').title()}")
    ax.set_xlabel("Number of Transactions")
    ax.set_ylabel(column.replace("_", " ").title())
    return _save(fig, subfolder, f"{column}_countplot.png")


def plot_grouped_bar(df: pd.DataFrame, group_col: str, value_col="total", subfolder="categorical_analysis", agg="sum"):
    """Bar chart of an aggregated value column across a categorical group."""
    data = df.groupby(group_col)[value_col].agg(agg).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.bar(data.index.astype(str), data.values, color=sns.color_palette("viridis", len(data)))
    ax.set_title(f"{agg.title()} of {value_col.replace('_', ' ').title()} by {group_col.replace('_', ' ').title()}")
    ax.set_xlabel(group_col.replace("_", " ").title())
    ax.set_ylabel(f"{agg.title()} {value_col.replace('_', ' ').title()}")
    ax.tick_params(axis="x", rotation=30)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:,.0f}", (bar.get_x() + bar.get_width() / 2, height),
                    ha="center", va="bottom", fontsize=9)
    return _save(fig, subfolder, f"{value_col}_by_{group_col}.png")


def plot_scatter(df: pd.DataFrame, x: str, y: str, hue=None, subfolder="correlation_plots"):
    """Scatter plot exploring the relationship between two numeric columns."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, alpha=0.6, ax=ax, palette="viridis")
    ax.set_title(f"{y.replace('_', ' ').title()} vs {x.replace('_', ' ').title()}")
    return _save(fig, subfolder, f"{y}_vs_{x}.png")


def plot_correlation_heatmap(df: pd.DataFrame, columns=None, subfolder="correlation_plots"):
    """Heatmap of the correlation matrix."""
    columns = columns or NUMERIC_COLS
    corr = df[columns].corr()
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, square=True)
    ax.set_title("Correlation Heatmap - Numeric Variables")
    return _save(fig, subfolder, "correlation_heatmap.png")


def plot_line_trend(df: pd.DataFrame, date_col="date", value_col="total", subfolder="distribution_plots"):
    """Daily revenue trend line chart."""
    daily = df.groupby(date_col)[value_col].sum()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(daily.index, daily.values, color="#4C72B0", linewidth=1.2)
    ax.set_title(f"Daily {value_col.replace('_', ' ').title()} Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel(value_col.replace("_", " ").title())
    fig.autofmt_xdate()
    return _save(fig, subfolder, f"daily_{value_col}_trend.png")


def plot_pairplot(df: pd.DataFrame, columns, hue=None, subfolder="correlation_plots"):
    """Pairplot across a small set of numeric columns."""
    g = sns.pairplot(df[columns + ([hue] if hue else [])], hue=hue, palette="viridis", diag_kind="kde")
    g.fig.suptitle("Pairwise Relationships", y=1.02)
    out_dir = VIZ_DIR / subfolder
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "pairplot.png"
    g.savefig(out_path, bbox_inches="tight")
    return out_path


def generate_all_visualizations(df: pd.DataFrame) -> None:
    """Regenerate the full set of project visualizations in one call."""
    for col in ["unit_price", "quantity", "total", "rating"]:
        plot_numeric_distribution(df, col)
        plot_boxplot(df, col)

    for col in ["branch", "product_line", "payment", "customer_type", "gender"]:
        plot_categorical_count(df, col)

    plot_grouped_bar(df, "product_line", "total")
    plot_grouped_bar(df, "city", "total")
    plot_grouped_bar(df, "day_of_week", "total")
    plot_grouped_bar(df, "product_line", "gross_income")

    plot_scatter(df, "unit_price", "total", hue="product_line")
    plot_scatter(df, "quantity", "total")
    plot_correlation_heatmap(df)
    plot_line_trend(df)
    plot_pairplot(df, ["unit_price", "quantity", "total", "rating"], hue="customer_type")

    plt.close("all")
    print(f"All visualizations saved under: {VIZ_DIR}")


if __name__ == "__main__":
    data = load_cleaned_data()
    generate_all_visualizations(data)
