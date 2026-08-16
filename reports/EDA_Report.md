# Exploratory Data Analysis Report — Supermarket Sales

**Author:** Sanjana R
**Project:** Exploratory Data Analysis Project
**Dataset period:** January 1, 2019 – March 30, 2019

This report summarizes the full project and is self-contained — it can be read and understood
without opening the notebook.

---

## 1. Introduction

Retail businesses generate large volumes of point-of-sale data, but that data only becomes
useful when it is systematically cleaned, explored, and interpreted. This project analyzes
1,000 transactions from three branches of a supermarket chain to answer a practical question:
**what actually drives revenue, profitability, and customer satisfaction in this business, and
what should management do about it?**

The analysis follows a standard EDA workflow: data understanding, cleaning, univariate
analysis, bivariate analysis, multivariate/correlation analysis, and a translation of findings
into recommendations.

## 2. Dataset Description

| Attribute | Value |
|---|---|
| Source | [Kaggle — Supermarket Sales](https://www.kaggle.com/datasets/aungpyaeap/supermarket-sales) |
| Rows | 1,000 transactions |
| Columns | 17 (raw), 21 after feature engineering |
| Branches | 3 (A – Yangon, B – Mandalay, C – Naypyitaw) |
| Time span | 3 months (Jan – Mar 2019) |
| Categorical variables | Branch, City, Customer type, Gender, Product line, Payment |
| Numeric variables | Unit price, Quantity, Tax 5%, Total, cogs, gross income, Rating |

Full column dictionary is available in `data/README.md`.

## 3. Data Cleaning

A full data-quality audit was performed before any analysis:

| Check | Result |
|---|---|
| Missing values | **0** across all 17 columns |
| Duplicate invoices | **0** |
| Negative/zero price or quantity rows | **0** |
| `total` formula mismatches (`unit_price × quantity × 1.05`) | **0** |
| Rating values outside 0–10 range | **0** |
| Inconsistent categorical labels | **0** (all categories already consistently formatted) |
| Outliers in `total` (1.5×IQR rule) | **9 transactions (0.9%)** — kept, as they represent legitimate large baskets |
| Outliers in `quantity` / `unit_price` | 0 |

**Cleaning actions taken:**
- Standardized column names to snake_case for code readability (e.g. `Tax 5%` → `tax_5_pct`)
- Converted `Date` and `Time` from text to proper datetime types
- Engineered `month`, `day_of_week`, and `hour` columns to enable time-pattern analysis
- Applied defensive whitespace/casing normalization to all categorical fields

Because the source export was already exceptionally clean, no rows were dropped and no values
were imputed — every cleaning step here is a type/format correction or a validation check, not
a data-quality fix. This is documented transparently rather than fabricated, in line with the
project's principle of not manufacturing findings that aren't in the data.

## 4. Exploratory Analysis

### Univariate
- `total` (transaction value) is right-skewed, concentrated between $50–$400 with a long tail
  up to just over $1,000.
- `quantity` is close to uniformly distributed between 1–10 units per transaction.
- `rating` is fairly flat across its 4–10 range, mean ≈ 6.97, with no ceiling/floor effect.
- Transaction counts are well balanced across the six product lines (no single category
  dominates by volume).

### Bivariate
- **Food and beverages** leads total revenue (≈ $56,145); **Health and beauty** trails
  (≈ $49,194), a ~12% gap despite similar transaction counts.
- **Branch C (Naypyitaw)** has the highest revenue (≈ $110,569) on the fewest transactions
  (328) — a higher-average-basket branch, not a higher-traffic one.
- **Member** customers slightly out-spend **Normal** customers in total revenue on almost
  identical transaction counts.
- Revenue is highest on **Saturday** (≈ $56,121) and lowest on **Monday** (≈ $37,899).
- Average rating varies only slightly by product line (6.8–7.1).

### Multivariate / Correlation
- `total`, `tax_5_pct`, `cogs`, and `gross_income` correlate at r = 1.00 with each other — by
  mathematical construction (all derived from `unit_price × quantity`), not as an independent
  finding.
- `quantity` correlates with `total` at **r = 0.71**; `unit_price` at **r = 0.63** — quantity is
  the slightly stronger lever on basket size.
- `rating` correlates with every financial variable at **|r| < 0.05** — statistically
  independent of spend.
- A city × product-line revenue pivot table shows branch-level differences in category
  performance, indicating a one-size-fits-all inventory strategy would be suboptimal.

## 5. Statistical Findings

| Metric | Value |
|---|---|
| Total revenue (all transactions) | $322,966.75 |
| Average transaction value | $322.97 |
| Median transaction value | ≈ $253.85 |
| Standard deviation of transaction value | ≈ $245.89 |
| Average quantity per transaction | 5.51 items |
| Average customer rating | 6.97 / 10 |

Grouped statistics (revenue sum/mean/count) by product line, city, customer type, gender, and
payment method are provided in full in the notebook (Section 9).

## 6. Visual Findings

22 visualizations were produced and saved under `visualizations/`, organized into:
- `distribution_plots/` — histograms, boxplots, and the daily revenue trend line
- `correlation_plots/` — heatmap, pairplot, and price/quantity vs. total scatter plots
- `categorical_analysis/` — count plots and grouped bar charts by branch, product line,
  payment method, city, and day of week

Highlights are embedded in the main `README.md`.

## 7. Correlation Analysis

The correlation matrix confirms two distinct groups of variables:
1. **Revenue-derived variables** (`total`, `tax_5_pct`, `cogs`, `gross_income`) that move in
   perfect lockstep because they share the same underlying formula.
2. **Independent explanatory variables** (`unit_price`, `quantity`, `rating`), of which only
   `unit_price` and `quantity` meaningfully explain `total`. `rating` behaves as a genuinely
   independent signal, uncorrelated with any financial metric.

This distinction matters for interpretation: reporting four "different" 1.00 correlations as
four separate findings would overstate the analysis. Treating them as one revenue concept, and
focusing analytical attention on `unit_price`, `quantity`, and `rating`, gives a more honest
and useful picture.

## 8. Key Insights

1. Food and beverages generates the highest revenue (≈ $56,145, 17.4% of total), narrowly ahead
   of Sports & travel and Electronic accessories.
2. Health and beauty underperforms every other category by ≈ 12% in revenue despite a
   comparable transaction count.
3. Branch C (Naypyitaw) has the highest revenue per branch with the fewest transactions —
   basket size, not footfall, drives its lead.
4. Saturday generates ≈ 48% more revenue than the weakest day, Monday.
5. January was the strongest month (≈ $116,292); February the weakest (≈ $97,219) — a ≈ 20%
   swing within the observed window.
6. Member customers contribute ≈ 3.4% more revenue than Normal customers on nearly identical
   transaction counts.
7. Cash is the most-used payment method, followed by Ewallet, then Credit card.
8. Quantity purchased (r = 0.71) is a stronger driver of transaction value than unit price
   (r = 0.63).
9. Customer rating is essentially independent of spend (|r| < 0.05 against every financial
   variable).
10. 9 transactions (0.9%) are statistical outliers on total value — all legitimate high-value
    baskets, none removed.
11. The dataset passed every data-quality and business-rule check with zero issues found.
12. Average customer rating (6.97/10) varies little across product lines, suggesting
    satisfaction is driven by factors outside this dataset (e.g. service, wait time).

## 9. Recommendations

| # | Observed Fact | Interpretation | Recommendation |
|---|---|---|---|
| 1 | Food & beverages and Sports & travel are the top two revenue lines | These categories have proven demand | Prioritize marketing budget and shelf space here |
| 2 | Health and beauty has ~12% lower revenue despite similar transaction volume | Average basket value, not customer interest, is the constraint | Test bundling/upselling/repricing within this category |
| 3 | Branch C earns the most revenue on the fewest transactions | It likely has a stronger product mix or upselling practice | Audit Branch C and replicate successful practices at A and B |
| 4 | Saturday revenue is ~48% higher than Monday's | Demand is not evenly spread across the week | Align staffing and promotions with this weekly cycle |
| 5 | Members generate more revenue on the same transaction count as Normal customers | Membership correlates with (not proven to cause) higher spend | Run a controlled sign-up campaign and re-measure before scaling |
| 6 | Rating is uncorrelated with spend | Satisfaction is driven by non-financial factors | Track satisfaction as an independent KPI; collect operational data |
| 7 | Cash and Ewallet dominate payment volume | Customers already have a clear preference | Keep cash/Ewallet checkout frictionless rather than pushing card incentives |
| 8 | The dataset spans only 3 months | Seasonal claims are not yet statistically robust | Re-run this analysis on a 12-month dataset before seasonal budget decisions |

## 10. Limitations

- **Short time window (3 months):** limits confidence in seasonal/monthly claims.
- **Constant gross margin:** `gross margin percentage` is fixed at 4.76% for every row, so
  margin-based profitability differences could not be analyzed — only volume/value-based ones.
- **No operational variables:** staffing levels, queue times, and store size are not captured,
  limiting the ability to explain the variance in customer `rating`.
- **Single-country, single-chain data:** findings may not generalize to other markets or
  retail formats.

## 11. Conclusion

This EDA turned a clean, well-structured 1,000-row transactional dataset into a set of
specific, quantified findings: which product lines and branches perform best (and why), a
clear weekly demand cycle, a modest membership effect on spend, and — perhaps most
importantly — clear evidence that customer satisfaction is not simply a byproduct of how much
a customer spends. Each recommendation in this report is traceable back to a specific,
verifiable statistic rather than a generic observation, and the accompanying notebook and
scripts make every step fully reproducible on a refreshed dataset.
