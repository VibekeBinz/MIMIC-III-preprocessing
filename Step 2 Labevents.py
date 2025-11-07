
import pandas as pd
from tqdm import tqdm
import os
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
data_path = "C:/Users/vibek/.vscode/DATA/MIMICIII/"   

# ----------------------------


# ---------- UTILITIES ----------

def parse_datetime_columns(df):
    for col in df.columns:
        if "TIME" in col.upper() or "DATE" in col.upper():
            df.loc[:, col] = pd.to_datetime(df[col], errors="coerce")
    return df

# ---------- PROCESS LABEVENTS ----------

print("\nProcessing LABEVENTS (first per HADM_ID) ...")

# Add ITEMID for cholesterol
ntprobnp_ids = [50963]
creatinine_ids = [50912]
bun_ids = [51006]
potassium_ids = [50971]
cholesterol_ids = [50861]

# Load and filter LABEVENTS 
lab_cols = ["HADM_ID", "ITEMID", "CHARTTIME", "VALUE"]
labevents = pd.read_csv(
    os.path.join(data_path, "LABEVENTS.csv"),
    usecols=lab_cols
)

labevents = parse_datetime_columns(labevents)
labevents = labevents[labevents["ITEMID"].isin(
    ntprobnp_ids + creatinine_ids + bun_ids + potassium_ids + cholesterol_ids
)]
labevents = labevents.sort_values(["HADM_ID", "CHARTTIME"])

# Reuse the extraction function
def get_first_lab(df, itemids, label):
    subset = df[df["ITEMID"].isin(itemids)]
    first = subset.groupby("HADM_ID").first().reset_index()
    first = first[["HADM_ID", "VALUE"]].rename(columns={"VALUE": label})
    return first

# Apply for all 5 tests 
ntprobnp_df = get_first_lab(labevents, ntprobnp_ids, "NT-proBNP")
creatinine_df = get_first_lab(labevents, creatinine_ids, "Creatinine")
bun_df = get_first_lab(labevents, bun_ids, "BLOOD_UREA_NITRO")
potassium_df = get_first_lab(labevents, potassium_ids, "POTASSIUM")
cholesterol_df = get_first_lab(labevents, cholesterol_ids, "CHOLESTEROL")



# Merge into summary table 
labs_summary = ntprobnp_df \
    .merge(creatinine_df, on="HADM_ID", how="outer") \
    .merge(bun_df, on="HADM_ID", how="outer") \
    .merge(potassium_df, on="HADM_ID", how="outer") \
    .merge(cholesterol_df, on="HADM_ID", how="outer")

# Save to CSV
labs_summary.to_csv("First_labevents_selected.csv", index=False)
print("Saved: First_labevents_selected.csv")


# ----------- visualization ------
print("\nVisualizing LABEVENTS data ...")

# Load the saved lab summary
labs_summary = pd.read_csv("First_labevents_selected.csv")

# Define the lab test columns
lab_columns = ["NT-proBNP", "Creatinine", "BLOOD_UREA_NITRO", "POTASSIUM", "CHOLESTEROL"]

# Count non-null values for each lab test
lab_counts = labs_summary[lab_columns].notnull().sum()

# Plot
plt.figure(figsize=(8, 6))
bars = plt.bar(lab_counts.index, lab_counts.values, color=["#FF9999", "#FFCC99", "#99CCFF", "#66B3FF", "#99FF99"])
plt.xlabel("Lab Test Type")
plt.ylabel("Number of Patients (HADM_ID)")
plt.title("Availability of Lab Test Results per Admission")

# Add value labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 5, int(yval), ha='center', va='bottom')

plt.tight_layout()
plt.show()