'''
AFT Data Visualization Tool
Data Organization
'''
'''-------------------------- Imports & Constants --------------------------'''

import pandas as pd
import numpy as np

'''--------------------------------- Data ----------------------------------'''
### import DATA, CODES, YEARS, PROGRAM_LIST, DEMOGRAPHICS to main

DATA = pd.read_csv("aft_v3.csv")

codes_unique = list(DATA.sort_values("Code")["Code"].unique())
# 'A', 'C', 'E', 'IP', 'L', 'O', 'S', 'SA', 'SC', 'TM'
code_labels = ['Arts (A)', 'Community Service (C)', 'Exempt (E)', 
               'Independent Project (IP)', 'Leave (L)', 'Other (O)',
               'Sports (S)',  'Semester Abroad (SA)', 
               'Strength & Conditioning (SC)', 'Team Manager (TM)']
CODES = {codes_unique[i]: code_labels[i] for i in range(len(code_labels))}

YEARS = list(DATA.sort_values("Acad Yr (start)")["Acad Yr (start)"].unique())
PROGRAM_LIST = list(DATA.sort_values("Code")["Program (name)"].unique())

DEMOGRAPHICS={
    "Gender code": "Gender", 
    "Race/ethnicity":"Race/Ethnicity", 
    "FA": "Financial Aid Status", 
    "Grade at Time of Activity":"Grade", 
    "Program (Level)":"Program Level",
    "Code": "None"}

COMPARISON_GROUPS = {
    "Program (name)": "Program",
    "Grade at Time of Activity":"Grade",
    "FA": "Financial Aid Status",
    "Gender code": "Gender", 
    "Race/ethnicity":"Race/Ethnicity"}
