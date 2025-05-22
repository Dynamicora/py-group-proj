import pandas as pd
import numpy as np
import re

# Prompt user to select the CSV file
file_path = input("Please enter the path to the 'Nominal Wages Trends HK.csv' file: ")

# Read the CSV file
raw_data = pd.read_csv(file_path, skiprows=4, header=None, encoding='big5')

# Get the English column headers (years and rate)
headers = raw_data.iloc[0].astype(str).str.replace(r'\n.*', '', regex=True).str.strip().to_list()

# Process the data
nominal_wages = (
    raw_data
    .dropna(how='all')  # Remove empty rows
    .loc[~raw_data[0].str.contains("註釋|Notes|@|Table|指數|Index|行業主類|Industry section", na=False)]  # Remove header rows
)

# Extract English industry names
industry_map = {
    "Manufacturing": "Manufacturing",
    "Import/export": "Import/export, wholesale and retail trades",
    "Transportation": "Transportation",
    "Accommodation": "Accommodation and food service activities",
    "Financial": "Financial and insurance activities",
    "Real estate": "Real estate leasing and maintenance management",
    "Professional": "Professional and business services",
    "Personal services": "Personal services",
    "All selected": "All selected industry sections"
}

# Identify industries
nominal_wages['industry'] = nominal_wages[0].apply(lambda x: next((v for k, v in industry_map.items() if k in x), np.nan))

# Remove rows where industry is NaN
nominal_wages = nominal_wages[nominal_wages['industry'].notna()]

# Remove the original mixed column and reorder
nominal_wages = nominal_wages.drop(columns=[0]).reset_index(drop=True)
nominal_wages = nominal_wages.rename(columns=dict(zip(nominal_wages.columns, headers[1:])))
nominal_wages.insert(0, 'industry', nominal_wages.pop('industry'))

# Remove completely empty columns
nominal_wages = nominal_wages.dropna(axis=1, how='all')

# Save the cleaned data
nominal_wages.to_csv("nominal_wages_hk.csv", index=False)

# Extract industry names
industries = nominal_wages['industry'].str.strip()

# Remove empty rows and extract numeric data
numeric_data = nominal_wages.drop(columns=['industry']).apply(pd.to_numeric, errors='coerce')
numeric_data = numeric_data.dropna(how='all')

# Verify industry names match data rows
if len(industries) != len(numeric_data):
    raise ValueError("Industry names don't match data rows. Please check the input file structure.")

# Combine industry names with numeric data
combined_data = pd.concat([industries.reset_index(drop=True), numeric_data.reset_index(drop=True)], axis=1)

# Create proper column names
years = range(2014, 2025)
year_headers = []
for year in years:
    year_headers.append(str(year))
    if year != 2014:
        year_headers.append(f"{year} YoY Rate of Change (%)")
year_headers.append("Average Annual Rate of Change")

# Assign column names
combined_data.columns = ['Industry'] + year_headers[:len(combined_data.columns) - 1]

# Reorganize columns
final_data = combined_data[['Industry'] + [str(year) for year in years] + [f"{year} YoY Rate of Change (%)" for year in years] + ['Average Annual Rate of Change']]

# Save the final cleaned data
final_data.to_csv("nominal_wages_hk_cleaned.csv", index=False)

# Print the result to verify
print(final_data)
