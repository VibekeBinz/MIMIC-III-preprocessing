MIMIC-III Preprocessing Pipeline

This repository contains preprocessing scripts for working with the MIMIC-III clinical database, developed by MIT (Alistair E. W. Johnson, Tom J. Pollard, and Leo A. Celi) 
MIMIC-III is a freely accessible critical care database but requires certain course certifications and a data agreement. 
See: https://physionet.org/content/mimiciii/1.4/

Necessarry manual prep 
In the ADMISSIONS file as downloaded from physionet site will break tyhe diagnosis field into several columns, disrupting the csv. This can easily be fixed manually in axcel using a concatenate formula. Save as ADMISSIONS_cleaned.  

Input files: 
ADMISSIONS_cleaned 
PATIENTS
CHARTEVENTS 
LABEVENTS

What the Code Does: 
This pipeline extracts a focused subset of patient-level information from MIMIC-III, including:
- First-recorded vital signs per hospital admission: Heart rate, Systolic blood pressure and Diastolic blood pressure
- First-recorded lab tests per hospital admission: NT-proBNP, Creatinine, Blood urea nitrogen (BUN), Potassium, Cholesterol
This information is merged with patient demographics and a flag is added for patients who were re-admitted within 30 days of discharge.
Patient age is estimated. 

Output: 
The final output is a csv file that merges patient demographics, vitals, labs, calculates ages and includes a readmission flag. 

Requirements
- Python ≥ 3.8
- pandas, tqdm, matplotlib

