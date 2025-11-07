import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load your merged dataset from step 3 and coerce death dates to valid dataetime 
superdf = pd.read_csv(
    "MIMIC_III_merged.csv",
    parse_dates=["DOB", "DOD", "DOD_HOSP", "DOD_SSN", "ADMITTIME", "DISCHTIME"],
    low_memory=False
)

for col in ["DOD", "DOD_HOSP", "DOD_SSN"]:
    superdf[col] = pd.to_datetime(superdf[col], errors="coerce")

# -------------------------------
# 🧠 AGE Calculation
# -------------------------------
superdf["ESTIMATED_AGE"] = 2131 - superdf["DOB"].dt.year
age_distribution_fallback = superdf[
    (superdf["ESTIMATED_AGE"] > 89) & (superdf["ESTIMATED_AGE"] <= 120)
]["ESTIMATED_AGE"].dropna().astype(int).values

def calculate_age(row):
    dob = row["DOB"]
    admit = row["ADMITTIME"]

    # 1. If patient has a valid death date
    for death_col in ["DOD", "DOD_HOSP", "DOD_SSN"]:
        death_date = row[death_col]
        if pd.notna(death_date) and pd.notna(dob):
           
            try:
                age = (death_date - dob).days // 365
                return int(age) if 0 <= age <= 120 else 120
            except (OverflowError, ValueError):
                break  # Treat as alive if subtraction fails



# If patietn is still alive 
    if row["EXPIRE_FLAG"] == 0:
        # Check for newborn
        if "NEWBORN" in str(row["ADMISSION_TYPE"]).upper() or "NEWBORN" in str(row["DIAGNOSIS"]).upper():
            return 0
        # Estimate age from DOB minus 100 years
        estimated_age = 2131 - row["DOB"].year
      
        # return estimated_age if 0 <= estimated_age <= 120 else np.random.choice(age_distribution_fallback)
        
        return estimated_age if 0 <= estimated_age <= 120 else np.random.choice(age_distribution_fallback)

    # 3. Fallback
    return np.nan


superdf["AGE"] = superdf.apply(calculate_age, axis=1)


# -------------------------------
# 🧠 Fill missing AGE (nan) using similar DOBs
# -------------------------------

# Round DOB to year for grouping
superdf["DOB_YEAR"] = superdf["DOB"].dt.year

# Create a lookup table: median AGE per DOB_YEAR
age_lookup = superdf[superdf["AGE"].notna()].groupby("DOB_YEAR")["AGE"].median()

# Fill missing AGE using the median AGE of patients with same DOB_YEAR
superdf["AGE"] = superdf.apply(
    lambda row: age_lookup[row["DOB_YEAR"]] if pd.isna(row["AGE"]) and row["DOB_YEAR"] in age_lookup else row["AGE"],
    axis=1
)

# Drop helper column
superdf.drop(columns=["DOB_YEAR"], inplace=True)


# -------------------------------
# 🔁 READMISSION Flag
# -------------------------------

# Sort by SUBJECT_ID and ADMITTIME
superdf.sort_values(by=["SUBJECT_ID", "ADMITTIME"], inplace=True)

# Calculate time since last discharge for same patient
superdf["PREV_DISCHTIME"] = superdf.groupby("SUBJECT_ID")["DISCHTIME"].shift(1)
superdf["DAYS_SINCE_LAST_DISCHARGE"] = (superdf["ADMITTIME"] - superdf["PREV_DISCHTIME"]).dt.days

# Flag readmissions within 30 days
superdf["READMISSION"] = (superdf["DAYS_SINCE_LAST_DISCHARGE"] <= 30).astype(int)

# Replace NaN (first admission) with 0
superdf["READMISSION"] = superdf["READMISSION"].fillna(0)
superdf["READMISSION"] = superdf["READMISSION"].astype(int)


# -------------------------------
# ✅ Save updated dataset
# -------------------------------

superdf.drop(columns=["PREV_DISCHTIME", "DAYS_SINCE_LAST_DISCHARGE"], inplace=True)
superdf.to_csv("MIMICIII_merged_w_AGEandREADMISSION.csv", index=False)

# -------------------------------
# ✅ Visualize! 
# -------------------------------
# Total number of unique patients
num_patients = superdf["SUBJECT_ID"].nunique()
print("Total unique patients:", num_patients)

# Total number of admissions (rows in the dataset)
num_admissions = len(superdf)
print("Total admissions:", num_admissions)

# Count missing AGE entries
missing_age_rows = superdf[superdf["AGE"].isna()]
print("Rows with missing AGE:", len(missing_age_rows))

# Number of unique newborn patients
newborn_mask = (
    superdf["ADMISSION_TYPE"].str.upper().str.contains("NEWBORN", na=False) |
    superdf["DIAGNOSIS"].str.upper().str.contains("NEWBORN", na=False)
)
num_newborns = superdf.loc[newborn_mask, "SUBJECT_ID"].nunique()
print("🍼 Unique newborn patients:", num_newborns)

# Number of unique deceased patients (EXPIRE_FLAG = 1)
num_deceased = superdf.loc[superdf["EXPIRE_FLAG"] == 1, "SUBJECT_ID"].nunique()
print("⚰️ Unique deceased patients:", num_deceased)

# Number of unique living patients (EXPIRE_FLAG = 0)
num_alive = superdf.loc[superdf["EXPIRE_FLAG"] == 0, "SUBJECT_ID"].nunique()
print("❤️ Unique living patients:", num_alive)


# # Drop missing ages or fill w -1 for the plot
age_data = superdf["AGE"].dropna()
#age_data = superdf["AGE"].fillna(-50)

# Plot histogram of age distribution 
# plt.figure(figsize=(10, 6))
# plt.hist(age_data, bins=30, color="skyblue", edgecolor="black")
# plt.title("Age Distribution of Patients")
# plt.xlabel("Age")
# plt.ylabel("Number of Admissions")
# plt.grid(True)
# plt.tight_layout()
# plt.show()


# Create a flag for age availability
superdf["AGE_AVAILABLE"] = superdf["AGE"].notna()

# Filter DOBs
valid_dobs = superdf[pd.notna(superdf["DOB"])]

# plot 3 test 
import matplotlib.pyplot as plt

# Split data into two groups
expired = superdf[superdf["EXPIRE_FLAG"] == 1]
alive = superdf[superdf["EXPIRE_FLAG"] == 0]

# Plot histogram
plt.figure(figsize=(10, 6))
plt.hist(expired["AGE"].dropna(), bins=30, color="blue", alpha=0.6, label="Expired (EXPIRE_FLAG = 1)")
plt.hist(alive["AGE"].dropna(), bins=30, color="red", alpha=0.6, label="Alive (EXPIRE_FLAG = 0)")

# Add labels and legend
plt.title("Age Distribution by Expiry Status")
plt.xlabel("Age")
plt.ylabel("Number of Patients")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()















