import os
import pandas as pd
import numpy as np

# ==============================================================================
# DAY 8: DATA PREPROCESSING & DATA CLEANING
# Intern: Shri Sanjaykumar V | Role: AI/ML Intern | Organization: Linkific
# ==============================================================================

print('=' * 65)
print('       DAY 8: DATA PREPROCESSING & DATA CLEANING PIPELINE       ')
print('=' * 65)

# 1. Load Dataset
possible_paths = [
    os.path.join(os.path.dirname(__file__), 'dataset.csv') if '__file__' in locals() else 'dataset.csv',
    'dataset.csv',
    os.path.join('Day-8', 'dataset.csv'),
    os.path.join('Python', 'Day-8', 'dataset.csv')
]
data_path = next((p for p in possible_paths if os.path.exists(p)), 'dataset.csv')
df = pd.read_csv(data_path)
print(f'Dataset loaded from: {os.path.abspath(data_path)}')
print(f'Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n')

# 2. Initial Dataset Inspection
print('=== First 5 Records ===')
print(df.head())
print()

print('=== Column Data Types ===')
print(df.dtypes)
print()

# 3. Missing Value Detection
print('=== Missing Values Before Cleaning ===')
print(df.isnull().sum())
total_missing_before = df.isnull().sum().sum()
print(f'Total Missing Values: {total_missing_before}\n')

# 4. Missing Value Handling
salary_median = df['BASE_SALARY'].median()
df['BASE_SALARY'] = df['BASE_SALARY'].fillna(salary_median)
print(f'Imputed BASE_SALARY with median: ${salary_median:,.2f}')

race_mode = df['RACE'].mode()[0]
df['RACE'] = df['RACE'].fillna(race_mode)
print(f'Imputed RACE with mode: \'{race_mode}\'')

df['JOB_DATE'] = df['JOB_DATE'].fillna(df['HIRE_DATE'])
print('Imputed missing JOB_DATE entries with HIRE_DATE')

print('\n=== Missing Values After Cleaning ===')
print(df.isnull().sum())
print(f'Total Missing Values Remaining: {df.isnull().sum().sum()}\n')

# 5. Duplicate Detection & Removal
dups_before = df.duplicated().sum()
print(f'Duplicate records in raw dataset: {dups_before}')
df = df.drop_duplicates()
print(f'Duplicate records after drop_duplicates(): {df.duplicated().sum()}')

# Controlled demonstration
print('\n--- Controlled Demonstration on Sample Data ---')
demo_df = pd.DataFrame({
    'employee_id': [101, 102, 102, 103],
    'name': ['Aarav', 'Diya', 'Diya', 'Rohan'],
    'department': ['Engineering', 'HR', 'HR', 'Marketing']
})
print('Sample Data with Duplicate Row:')
print(demo_df)
print(f'Sample Duplicate Count: {demo_df.duplicated().sum()}')
demo_cleaned = demo_df.drop_duplicates()
print('After drop_duplicates():')
print(demo_cleaned)
print(f'Sample Duplicates Remaining: {demo_cleaned.duplicated().sum()}\n')

# 6. Column Renaming
print('Original Columns:')
print(df.columns.tolist())

rename_mapping = {
    'UNIQUE_ID': 'employee_id',
    'POSITION_TITLE': 'position_title',
    'DEPARTMENT': 'department',
    'BASE_SALARY': 'base_salary',
    'RACE': 'race',
    'EMPLOYMENT_TYPE': 'employment_type',
    'GENDER': 'gender',
    'EMPLOYMENT_STATUS': 'employment_status',
    'HIRE_DATE': 'hire_date',
    'JOB_DATE': 'job_date'
}
df.rename(columns=rename_mapping, inplace=True)

print('\nStandardized snake_case Columns:')
print(df.columns.tolist())
print()

# 7. Data Type Conversion
df['hire_date'] = pd.to_datetime(df['hire_date'], errors='coerce')
df['job_date'] = pd.to_datetime(df['job_date'], errors='coerce')
df['gender'] = df['gender'].astype('category')
df['employment_type'] = df['employment_type'].astype('category')

print('=== Data Types After Conversion ===')
print(df.dtypes)
print()

# 8. Final Dataset Validation
print('=' * 65)
print('                   FINAL DATASET HEALTH CHECK                   ')
print('=' * 65)
print(f'Final Shape           : {df.shape[0]} rows, {df.shape[1]} columns')
print(f'Total Missing Values  : {df.isnull().sum().sum()}')
print(f'Total Duplicate Rows  : {df.duplicated().sum()}')
print('\nFirst 5 Records:')
print(df.head())
print('=' * 65)
print()

# 9. Save Cleaned Dataset
out_dir = os.path.dirname(data_path) if os.path.dirname(data_path) else '.'
out_file = os.path.join(out_dir, 'cleaned_dataset.csv')
df.to_csv(out_file, index=False)
print(f'Cleaned dataset saved to: {os.path.abspath(out_file)}')
print(f'File exists: {os.path.exists(out_file)} | File size: {os.path.getsize(out_file):,} bytes\n')

# 10. Before vs After Summary
summary_df = pd.DataFrame({
    'Metric': ['Total Rows', 'Total Columns', 'Missing Values', 'Duplicate Rows', 'Datetime Columns', 'Category Columns'],
    'Before Cleaning': [2000, 10, total_missing_before, dups_before, 0, 0],
    'After Cleaning': [df.shape[0], df.shape[1], df.isnull().sum().sum(), df.duplicated().sum(), 2, 2]
})

print('=' * 65)
print('                     BEFORE VS AFTER SUMMARY                    ')
print('=' * 65)
print(summary_df.to_string(index=False))
print('=' * 65)
