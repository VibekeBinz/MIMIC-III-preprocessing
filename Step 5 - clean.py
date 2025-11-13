import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

# Load dataset
df = pd.read_csv("MIMICIII_merged_w_AGEandREADMISSION.csv")

# Convert columns to numeric in case of formatting issues
df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce')


import pandas as pd

# Load the original dataset
df = pd.read_csv("MIMICIII_merged_w_AGEandREADMISSION.csv", low_memory=False)

# Define the columns to keep
columns_to_keep = [
    'ROW_ID', 'SUBJECT_ID', 'HADM_ID', 'ADMISSION_TYPE', 'INSURANCE', 'LANGUAGE',
    'RELIGION', 'MARITAL_STATUS', 'ETHNICITY', 'DIAGNOSIS', 
    'GENDER', 'EXPIRE_FLAG', 'NT-proBNP', 'Creatinine', 'BLOOD_UREA_NITRO',
    'POTASSIUM', 'CHOLESTEROL', 'HEART_VALUE', 'SYSTOLIC_VALUE', 'DIASTOLIC_VALUE', 'AGE', 'READMISSION'
    ]

# Filter the DataFrame
df_clean = df[columns_to_keep]

# Save to a new CSV file
df_clean.to_csv("MIMIC_clean.csv", index=False)

print("✅ Cleaned dataset saved as 'MIMIC_clean.csv'")


# Load cleaned dataset
df = pd.read_csv("MIMIC_clean.csv")

# Select first 5 rows and transpose
vertical_table = df.head(5).transpose()

# Format and print
print(tabulate(vertical_table, headers=["Row 1", "Row 2", "Row 3", "Row 4", "Row 5"], tablefmt="grid"))