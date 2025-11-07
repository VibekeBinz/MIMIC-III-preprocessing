# ======================================
# MIMIC-III MERGE SCRIPT (Memory-Safe)
# ======================================

import pandas as pd
from tqdm import tqdm
import os

# ---------- CONFIG ----------
data_path = "C:/Users/vibek/.vscode/DATA/MIMICIII/"  # <-- change this

# ----------------------------


# ---------- UTILITIES ----------

def parse_datetime_columns(df):
    for col in df.columns:
        if "TIME" in col.upper() or "DATE" in col.upper():
            df.loc[:, col] = pd.to_datetime(df[col], errors="coerce")
    return df


# ---------- LOAD CORE TABLES ----------

print("Loading lavevents summary and chartevents summary...")

labs_summary = pd.read_csv("First_labevents_selected.csv")
vitals = pd.read_csv("First_chartevents_vitals.csv")

print("Load admissions...")

admissions = pd.read_csv(
    os.path.join(data_path, "ADMISSIONS_cleaned.csv"),
    sep=",",
    quotechar='"',
    dtype=str,
    encoding="utf-8",
    skipinitialspace=True,
    engine="python",
    on_bad_lines="warn"
)
#print(admissions.head())

#admissions.columns = admissions.columns.str.strip().str.replace('"', '').str.upper()

print("✅ Columns:", admissions.columns.tolist())
print("Number of columns:", len(admissions.columns))

print("cleaning the column names...")

print("Number of columns:", len(admissions.columns))
print("Raw column names:", admissions.columns.tolist())

print("Loading  PATIENTS ...")

patients = pd.read_csv(os.path.join(data_path, "PATIENTS.csv"), usecols=lambda col: col != "ROW_ID")
patients = parse_datetime_columns(patients)
patients["SUBJECT_ID"] = patients["SUBJECT_ID"].astype("int64")

print("Something something SUBJECT_ID ...")
print("Kolonner i admissions:", admissions.columns.tolist())

admissions = parse_datetime_columns(admissions)
admissions.columns = admissions.columns.str.strip().str.upper()
admissions["SUBJECT_ID"] = admissions["SUBJECT_ID"].astype("int64")

# ---------- MERGE INTO FINAL ----------

print("\nMerging into FINAL dataset ...")

# Merge patients onto admissions
final = admissions.merge(
    patients[["SUBJECT_ID", "GENDER", "DOB", "DOD", "DOD_HOSP", "DOD_SSN", "EXPIRE_FLAG"]],
    on="SUBJECT_ID",
    how="left"
 )


final["HADM_ID"] = pd.to_numeric(final["HADM_ID"], errors="coerce").astype("Int64")
labs_summary["HADM_ID"] = pd.to_numeric(labs_summary["HADM_ID"], errors="coerce").astype("Int64")



final = final.merge(labs_summary, on="HADM_ID", how="left")
final = final.merge(vitals, on="HADM_ID", how="left")


print("final HADM_ID type:", final["HADM_ID"].dtype)
print("labs_summary HADM_ID type:", labs_summary["HADM_ID"].dtype)

final = parse_datetime_columns(final)
final.to_csv("MIMIC_III_merged.csv", index=False)

print("\n✅ Saved: MIMIC_III_merge.csv")
print("\n--- Headers & first row ---")
print("FINAL dataset columns:", final.columns.tolist())
print(final.iloc[:5].T)