'''
AFT Data Visualization Tool
Data Organization
'''
'''-------------------------- Imports & Constants --------------------------'''

# pre-existing python libraries
import pandas as pd

'''--------------------------------- Data ----------------------------------'''

# all data
enrollment_data = "aft_v3.csv" # file name
DATA = pd.read_csv(enrollment_data)

# program codes (i.e., "sports", "arts")
codes_unique = list(DATA.sort_values("Code")["Code"].unique())
# 'A', 'C', 'E', 'IP', 'L', 'O', 'S', 'SA', 'SC', 'TM'
code_labels = ['Arts (A)', 'Community Service (C)', 'Exempt (E)', 
               'Independent Project (IP)', 'Leave (L)', 'Other (O)',
               'Sports (S)',  'Semester Abroad (SA)', 
               'Strength & Conditioning (SC)', 'Team Manager (TM)']
CODES = {codes_unique[i]: code_labels[i] for i in range(len(code_labels))}

# all years in the data
YEARS = list(DATA.sort_values("Acad Yr (start)")["Acad Yr (start)"].unique())

# all unique programs in the data
PROGRAM_LIST = list(DATA.sort_values("Code")["Program (name)"].unique())

# demographics filters
DEMOGRAPHICS={
    "Gender code": "Gender", 
    "Race/ethnicity":"Race/Ethnicity", 
    "FA": "Financial Aid Status", 
    "Grade at Time of Activity":"Grade", 
    "Program (Level)":"Program Level",
    "Code":"Program Code",
    "Program (name)": "None"}

# grade divisions
GRADES = {
    "hs": "High school only (9-12)",
    "ms": "Middle school only (7-8)",
    "all": "All years"
}

# for comparison charts
COMPARISON_GROUPS = {
    "Program (name)": "Program",
    "Grade at Time of Activity":"Grade",
    "FA": "Financial Aid Status",
    "Gender code": "Gender", 
    "Race/ethnicity":"Race/Ethnicity"}

# for popularity treemap
TREEMAP_DEMOGS = {
    "Gender code": "Gender", 
    "Race/ethnicity":"Race/Ethnicity", 
    "FA": "Financial Aid Status", 
    "Grade at Time of Activity":"Grade", 
    "Program (Level)":"Program Level",
    "Code":"Program Code"
}