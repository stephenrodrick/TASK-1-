# TASK-1-
# Manual Data Cleaning in Excel (Final, Submission-Ready Guide)

## Objective

To manually clean and prepare the provided sales transaction dataset in **Microsoft Excel**, ensuring it is accurate, consistent, and ready for analysis. This process covers data profiling, cleaning, validation, feature engineering, and final export.

---

## Dataset Overview

**Columns:**

* TransactionID
* Date
* CustomerID
* Product
* Quantity
* Price
* Total

**Common Issues Identified:**

* Missing values (Quantity, Total)
* Duplicate TransactionIDs
* Inconsistent date formats
* Inconsistent product naming (case, spaces)
* Invalid numeric values (negative or zero)
* Total not matching Quantity × Price

---

## Step 1: Create a Working Copy

1. Open the original Excel file.
2. Click **File → Save As**.
3. Rename as `sales_transactions_cleaning.xlsx`.

**Why:** Preserves raw data integrity.

---

## Step 2: Identify Missing Values

1. Select entire sheet (**Ctrl + A**).
2. Go to **Home → Find & Select → Go To Special**.
3. Choose **Blanks → OK**.

### Actions

* **Quantity (missing):** Replace with median.

  * Formula (example): `=MEDIAN(E:E)`
* **Total (missing):** Leave for recalculation in Step 7.

---

## Step 3: Remove Duplicate Records

1. Select all data.
2. Go to **Data → Remove Duplicates**.
3. Check **TransactionID** only.
4. Click **OK**.

**Reason:** Each transaction must be unique.

---

## Step 4: Standardize Date Format

1. Select the **Date** column.
2. Press **Ctrl + 1** (Format Cells).
3. Choose **Date**.
4. Select a uniform format (e.g., **DD-MM-YYYY**).
5. Click **OK**.

**If dates are stored as text:**

* Use **Data → Text to Columns → Finish**.

---

## Step 5: Standardize Product Names

1. Insert a helper column next to **Product**.
2. Use the formula:

   ```excel
   =PROPER(TRIM(D2))
   ```
3. Drag down.
4. Copy the helper column → **Paste Special → Values** over original Product column.
5. Delete helper column.

---

## Step 6: Validate Quantity and Price

### Quantity Validation

1. Select **Quantity** column.
2. Go to **Data → Data Validation**.
3. Allow: **Whole number**.
4. Minimum: **1**.

### Price Validation

1. Select **Price** column.
2. Data Validation → Allow: **Decimal**.
3. Minimum: **0.01**.

**Purpose:** Prevent invalid future entries.

---

## Step 7: Recalculate Total (Critical)

1. In **Total** column, enter:

   ```excel
   =Quantity * Price
   ```

   Example: `=E2*F2`
2. Drag down to all rows.
3. Replace existing Total values with calculated values.

**Business Logic:** Revenue must equal Quantity × Price.

---

## Step 8: Feature Engineering

### Order Month

```excel
=MONTH(B2)
```

### Order Year

```excel
=YEAR(B2)
```

### Revenue Category

```excel
=IF(G2<50,"Low",IF(G2<=150,"Medium","High"))
```

---

## Step 9: Outlier Detection

1. Sort **Total** column (Largest to Smallest).
2. Identify unusually high values.
3. Cross-check Quantity and Price.

**Action:** Correct if data-entry error; retain if valid.

---

## Step 10: Final Review & Export

### Final Checklist

* No missing values in key columns
* Consistent date format
* Standardized product names
* Valid numeric values
* Correct totals

### Export

1. File → **Save As**.
2. Choose **CSV (Comma delimited)**.
3. Name: `cleaned_sales_transactions.csv`.

---

## Final Deliverables

* **Cleaned Dataset:** `cleaned_sales_transactions.csv`
* **Data Dictionary:** Explaining each column
* **Profiling Notes:** Issues found and fixes applied

---

## Outcome

The dataset is now **clean, consistent, validated, and ready for analysis or visualization**.
