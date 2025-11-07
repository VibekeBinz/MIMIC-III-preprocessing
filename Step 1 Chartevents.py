
import pandas as pd
from tqdm import tqdm
import os
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
data_path = "C:/Users/vibek/.vscode/DATA/MIMICIII/"  # 
chunksize = 1_000_000  # adjust for your RAM
# ----------------------------


# ---------- UTILITIES ----------

def parse_datetime_columns(df):
    for col in df.columns:
        if "TIME" in col.upper() or "DATE" in col.upper():
            df.loc[:, col] = pd.to_datetime(df[col], errors="coerce")
    return df

# Define ITEMIDs for each measurement
heart_rate_ids = [211, 220045]
systolic_bp_ids = [51, 442, 455, 6701, 220179, 220050]
diastolic_bp_ids = [8368, 8440, 8441, 8555, 220180, 220051]
vital_ids = heart_rate_ids + systolic_bp_ids + diastolic_bp_ids

# Define relevant rows from CHARTEVENTS
chart_cols = ["HADM_ID", "ITEMID", "CHARTTIME", "VALUE"]
chartevents_filtered = []

# ----------------------------


# ---------- LOAD AND CHUNK CORE TABLES ----------

for chunk in tqdm(pd.read_csv(
    os.path.join(data_path, "CHARTEVENTS.csv"),
    usecols=chart_cols,
    chunksize=chunksize,
    low_memory=False
)):
    chunk = chunk[chunk["ITEMID"].isin(vital_ids)]
    chunk = parse_datetime_columns(chunk)
    chartevents_filtered.append(chunk)

chartevents = pd.concat(chartevents_filtered, ignore_index=True)
chartevents = chartevents.sort_values(["HADM_ID", "CHARTTIME"])

# chartevents = parse_datetime_columns(chartevents)
# chartevents = chartevents[chartevents["ITEMID"].isin(vital_ids)]
# chartevents = chartevents.sort_values(["HADM_ID", "CHARTTIME"])

# ---------- PROCESS CHARTEVENTS ----------

# Extract first measurement  per HADM_ID per vital type 
def get_first_measurement(df, itemids, label):
    subset = df[df["ITEMID"].isin(itemids)]
    first = subset.groupby("HADM_ID").first().reset_index()
    first = first[["HADM_ID", "VALUE"]].rename(columns={"VALUE": f"{label}_VALUE"})
    return first

heart_df = get_first_measurement(chartevents, heart_rate_ids, "HEART")
systolic_df = get_first_measurement(chartevents, systolic_bp_ids, "SYSTOLIC")
diastolic_df = get_first_measurement(chartevents, diastolic_bp_ids, "DIASTOLIC")

vitals = heart_df.merge(systolic_df, on="HADM_ID", how="outer")
vitals = vitals.merge(diastolic_df, on="HADM_ID", how="outer")


# ---------- SAVE TO CSV  ----------

vitals.to_csv("First_chartevents_vitals.csv", index=False)
print("Saved: First_chartevents_vitals.csv")


# ---------- SANITY CHECK  ----------


# Quick sanity check
print("Unique HADM_IDs in CHARTEVENTS:", vitals["HADM_ID"].nunique())
print("Total rows in CHARTEVENTS first events:", len(vitals))  


######### VISUALIZATION #########
     
# Load the vitals dataset
vitals = pd.read_csv("First_chartevents_vitals.csv")

# Count non-null values for each vital sign
vital_columns = ["HEART_VALUE", "SYSTOLIC_VALUE", "DIASTOLIC_VALUE"]
vital_counts = vitals[vital_columns].notnull().sum()


# Plot
plt.figure(figsize=(8, 6))
bars = plt.bar(vital_counts.index, vital_counts.values, color=["#FF9999", "#66B3FF", "#99FF99"])
plt.xlabel("Vital Sign Type")
plt.ylabel("Number of Patients (HADM_ID)")
plt.title("Availability of Vital Sign Measurements")

# Add value labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 5, int(yval), ha='center', va='bottom')

plt.tight_layout()
plt.show()

# Diagnostics
print("Total rows in vitals:", len(vitals))
print("Missing HEART_RATE:", vitals["HEART_VALUE"].isnull().sum())
print("Missing SYSTOLIC_BP:", vitals["SYSTOLIC_VALUE"].isnull().sum())
print("Missing DIASTOLIC_BP:", vitals["DIASTOLIC_VALUE"].isnull().sum())