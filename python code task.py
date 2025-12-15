import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_transaction_data(file_path):
    """
    Clean and handle data quality issues in transaction data
    
    Parameters:
    file_path (str): Path to the Excel file
    
    Returns:
    tuple: (cleaned_df, issues_report)
    """
    
    df = pd.read_excel(file_path)
    
    issues = {
        'malformed_dates': [],
        'missing_values': [],
        'invalid_totals': [],
        'negative_values': [],
        'duplicate_transactions': [],
        'data_type_issues': []
    }
    
    print("=" * 70)
    print("DATA QUALITY ANALYSIS AND CLEANING")
    print("=" * 70)
    print(f"\nOriginal dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {', '.join(df.columns.tolist())}")

    print("\n" + "=" * 70)
    print("1. FIXING DATE FORMAT ISSUES")
    print("=" * 70)
    
    def fix_date(date_val, row_idx):
        """Fix malformed dates"""
        if pd.isna(date_val):
            return None
        
        date_str = str(date_val).strip()
        
        
        if date_str.startswith('C') and len(date_str) == 4:
            issues['data_type_issues'].append({
                'row': row_idx + 2,
                'column': 'Date',
                'value': date_str,
                'issue': 'Date column contains CustomerID'
            })
            return None
        

        match = re.match(r'(\d{2,4})-(\d{1,2})-(\d{1,4})', date_str)
        if match:
            year, month, day = match.groups()
            
            
            if len(year) == 3:
                year = year + '4'  
            elif len(year) == 2:
                year = '20' + year
            
            
            if len(day) == 1 and day == '0':
                day = '01'
            elif len(day) == 1:
                day = '0' + day
            
            
            if len(month) == 1:
                month = '0' + month
            
            try:
                fixed_date = pd.to_datetime(f"{year}-{month}-{day}")
                if date_str != f"{year}-{month}-{day}":
                    issues['malformed_dates'].append({
                        'row': row_idx + 2,
                        'original': date_str,
                        'fixed': f"{year}-{month}-{day}"
                    })
                return fixed_date
            except:
                issues['malformed_dates'].append({
                    'row': row_idx + 2,
                    'original': date_str,
                    'fixed': 'Unable to parse'
                })
                return None
        
        
        try:
            return pd.to_datetime(date_str)
        except:
            issues['malformed_dates'].append({
                'row': row_idx + 2,
                'original': date_str,
                'fixed': 'Unable to parse'
            })
            return None
    
    df['Date_Original'] = df['Date'].copy()
    df['Date'] = df.apply(lambda row: fix_date(row['Date'], row.name), axis=1)
    
    print(f"Fixed {len(issues['malformed_dates'])} malformed dates")
    for issue in issues['malformed_dates'][:5]:  # Show first 5
        print(f"  Row {issue['row']}: '{issue['original']}' → '{issue['fixed']}'")
    if len(issues['malformed_dates']) > 5:
        print(f"  ... and {len(issues['malformed_dates']) - 5} more")
    
    
    print("\n" + "=" * 70)
    print("2. CHECKING MISSING VALUES")
    print("=" * 70)
    
    for col in df.columns:
        if col == 'Date_Original':
            continue
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_rows = df[df[col].isna()].index + 2
            issues['missing_values'].append({
                'column': col,
                'count': missing_count,
                'rows': missing_rows.tolist()[:10]  # First 10 rows
            })
            print(f"  {col}: {missing_count} missing values in rows {missing_rows.tolist()[:10]}")
    
    
    if df['Quantity'].isna().any():
        df['Quantity'].fillna(1, inplace=True)
        print("\n  → Filled missing Quantity values with 1")
    
    
    print("\n" + "=" * 70)
    print("3. VALIDATING TOTAL CALCULATIONS")
    print("=" * 70)
    
    df['Expected_Total'] = df['Quantity'] * df['Price']
    
    
    missing_total_mask = df['Total'].isna()
    if missing_total_mask.any():
        print(f"  Found {missing_total_mask.sum()} rows with missing Total values")
        df.loc[missing_total_mask, 'Total'] = df.loc[missing_total_mask, 'Expected_Total']
        print("  → Calculated missing Total values")
    
    
    total_mismatch = ~np.isclose(df['Total'].fillna(0), df['Expected_Total'], rtol=0.01, atol=0.01)
    mismatched = df[total_mismatch]
    
    if len(mismatched) > 0:
        print(f"\n  Found {len(mismatched)} rows with incorrect totals:")
        for idx, row in mismatched.iterrows():
            issues['invalid_totals'].append({
                'row': idx + 2,
                'transaction_id': row['TransactionID'],
                'current_total': row['Total'],
                'expected_total': row['Expected_Total'],
                'difference': row['Total'] - row['Expected_Total']
            })
            print(f"    Row {idx + 2} ({row['TransactionID']}): {row['Total']} → {row['Expected_Total']} (diff: {row['Total'] - row['Expected_Total']:.2f})")
        
        df['Total'] = df['Expected_Total']
        print("\n  → Corrected all Total values")
    else:
        print("  All Total calculations are correct!")
    
    df.drop('Expected_Total', axis=1, inplace=True)
    
    
    print("\n" + "=" * 70)
    print("4. CHECKING FOR INVALID VALUES")
    print("=" * 70)
    
    for col in ['Quantity', 'Price', 'Total']:
        negative_mask = df[col] < 0
        zero_mask = df[col] == 0
        
        if negative_mask.any():
            print(f"  {col}: {negative_mask.sum()} negative values found")
            for idx in df[negative_mask].index:
                issues['negative_values'].append({
                    'row': idx + 2,
                    'column': col,
                    'value': df.loc[idx, col]
                })
        
        if zero_mask.any():
            print(f"  {col}: {zero_mask.sum()} zero values found")
    
    
    print("\n" + "=" * 70)
    print("5. CHECKING FOR DUPLICATE TRANSACTION IDs")
    print("=" * 70)
    
    duplicates = df[df.duplicated(subset=['TransactionID'], keep=False)]
    if len(duplicates) > 0:
        print(f"  Found {len(duplicates)} rows with duplicate transaction IDs:")
        for trans_id in duplicates['TransactionID'].unique():
            dup_rows = df[df['TransactionID'] == trans_id].index + 2
            issues['duplicate_transactions'].append({
                'transaction_id': trans_id,
                'rows': dup_rows.tolist()
            })
            print(f"    {trans_id}: appears in rows {dup_rows.tolist()}")
    else:
        print("  No duplicate transaction IDs found!")
    
    
    print("\n" + "=" * 70)
    print("6. STANDARDIZING TEXT COLUMNS")
    print("=" * 70)
    
    df['CustomerID'] = df['CustomerID'].astype(str).str.strip().str.upper()
    df['Product'] = df['Product'].astype(str).str.strip().str.title()
    print("  → Standardized CustomerID and Product columns")
    
    
    print("\n" + "=" * 70)
    print("7. ADDING DATA QUALITY FLAGS")
    print("=" * 70)
    
    df['Quality_Flag'] = 'OK'
    df.loc[df['Date'].isna(), 'Quality_Flag'] = 'MISSING_DATE'
    df.loc[df.duplicated(subset=['TransactionID'], keep=False), 'Quality_Flag'] = 'DUPLICATE_ID'
    
    flag_counts = df['Quality_Flag'].value_counts()
    print("  Quality flag distribution:")
    for flag, count in flag_counts.items():
        print(f"    {flag}: {count} rows")
    
    
    df.drop('Date_Original', axis=1, inplace=True)
    
    # Final summary
    print("\n" + "=" * 70)
    print("CLEANING SUMMARY")
    print("=" * 70)
    print(f"Total rows: {len(df)}")
    print(f"Clean rows: {len(df[df['Quality_Flag'] == 'OK'])}")
    print(f"Rows with issues: {len(df[df['Quality_Flag'] != 'OK'])}")
    print(f"\nIssues found:")
    print(f"  - Malformed dates: {len(issues['malformed_dates'])}")
    print(f"  - Missing values: {sum([i['count'] for i in issues['missing_values']])}")
    print(f"  - Invalid totals: {len(issues['invalid_totals'])}")
    print(f"  - Negative values: {len(issues['negative_values'])}")
    print(f"  - Duplicate IDs: {len(issues['duplicate_transactions'])}")
    
    return df, issues


def save_cleaned_data(df, output_path='cleaned_transactions.xlsx'):
    """Save cleaned data to Excel file"""
    df.to_excel(output_path, index=False)
    print(f"\n✓ Cleaned data saved to: {output_path}")


def save_issues_only(df, issues, output_path='data_issues.xlsx'):
    """Save only problematic rows to a separate file"""
    problematic_df = df[df['Quality_Flag'] != 'OK']
    if len(problematic_df) > 0:
        problematic_df.to_excel(output_path, index=False)
        print(f"✓ Problematic rows saved to: {output_path}")
    else:
        print("✓ No problematic rows to save!")


def generate_quality_report(issues, report_path='data_quality_report.txt'):
    """Generate a detailed quality report"""
    with open(report_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("DATA QUALITY DETAILED REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"1. MALFORMED DATES: {len(issues['malformed_dates'])}\n")
        f.write("-" * 70 + "\n")
        for issue in issues['malformed_dates']:
            f.write(f"  Row {issue['row']}: '{issue['original']}' → '{issue['fixed']}'\n")
        
        f.write(f"\n2. MISSING VALUES\n")
        f.write("-" * 70 + "\n")
        for issue in issues['missing_values']:
            f.write(f"  {issue['column']}: {issue['count']} missing in rows {issue['rows']}\n")
        
        f.write(f"\n3. INVALID TOTALS: {len(issues['invalid_totals'])}\n")
        f.write("-" * 70 + "\n")
        for issue in issues['invalid_totals']:
            f.write(f"  Row {issue['row']} ({issue['transaction_id']}): ")
            f.write(f"Current={issue['current_total']}, Expected={issue['expected_total']}, ")
            f.write(f"Diff={issue['difference']:.2f}\n")
        
        f.write(f"\n4. NEGATIVE VALUES: {len(issues['negative_values'])}\n")
        f.write("-" * 70 + "\n")
        for issue in issues['negative_values']:
            f.write(f"  Row {issue['row']}, {issue['column']}: {issue['value']}\n")
        
        f.write(f"\n5. DUPLICATE TRANSACTIONS: {len(issues['duplicate_transactions'])}\n")
        f.write("-" * 70 + "\n")
        for issue in issues['duplicate_transactions']:
            f.write(f"  {issue['transaction_id']}: Rows {issue['rows']}\n")
        
        f.write(f"\n6. DATA TYPE ISSUES: {len(issues['data_type_issues'])}\n")
        f.write("-" * 70 + "\n")
        for issue in issues['data_type_issues']:
            f.write(f"  Row {issue['row']}, {issue['column']}: {issue['value']} - {issue['issue']}\n")
    
    print(f"✓ Detailed quality report saved to: {report_path}")


# Main execution
if __name__ == "__main__":
    # Replace with your actual file path
    file_path = 'transactions.xlsx'
    
    print("\n" + "=" * 70)
    print("EXCEL DATA QUALITY HANDLER")
    print("=" * 70)
    
    try:
        # Clean the data
        cleaned_df, issues = clean_transaction_data(file_path)
        
        # Save outputs
        print("\n" + "=" * 70)
        print("SAVING OUTPUTS")
        print("=" * 70)
        
        save_cleaned_data(cleaned_df, 'cleaned_transactions.xlsx')
        save_issues_only(cleaned_df, issues, 'problematic_rows.xlsx')
        generate_quality_report(issues, 'data_quality_report.txt')
        
        # Display summary statistics
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)
        print("\nNumeric columns summary:")
        print(cleaned_df[['Quantity', 'Price', 'Total']].describe())
        
        print("\nProduct distribution:")
        print(cleaned_df['Product'].value_counts())
        
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE!")
        print("=" * 70)
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: File '{file_path}' not found!")
        print("Please update the 'file_path' variable with the correct path to your Excel file.")
        print("\nExample: file_path = 'C:/Users/YourName/Documents/transactions.xlsx'")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()