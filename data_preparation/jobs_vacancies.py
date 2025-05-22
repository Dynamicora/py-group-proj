import pandas as pd

# Prompt user to select the CSV file
file_path = input("Please enter the path to the 'Jobs Vacancies HK.csv' file: ")

# Reading the CSV file, skipping unnecessary rows
vacancies_data = pd.read_csv(file_path, skiprows=5)

# Remove empty rows and notes at the bottom
# vacancies_data = vacancies_data[vacancies_data['...1'].notna()]
vacancies_data = vacancies_data.dropna()
# vacancies_data = vacancies_data[~vacancies_data['...1'].str.contains("Note|Source|Release Date", na=False)]

# Rename columns properly
vacancies_data.columns = ["Year", "Month", "Industry_Section", "Managers",
                          "Professionals", "Associate_Professionals",
                          "Clerical_Support_Workers", "Service_Sales_Workers",
                          "Craft_Related_Workers", "Plant_Machine_Operators",
                          "Skilled_Agricultural_Fishery", "Elementary_Occupations", "Total"]

# Clean the data
vacancies_data_clean = vacancies_data.copy()
vacancies_data_clean['Year'] = pd.to_numeric(vacancies_data_clean['Year'], errors='coerce')
vacancies_data_clean['Month'] = vacancies_data_clean['Month'].replace({
    "Mar": "March",
    "Jun": "June",
    "Sep": "September",
    "Dec": "December"
})

vacancies_data_clean['Industry_Section'] = vacancies_data_clean['Industry_Section'].replace({
    "C: Manufacturing": "Manufacturing",
    "B, D & E: Mining and quarrying; and electricity and gas supply, and waste management": "Mining, Quarrying, Electricity, Gas, Waste Management",
    "F: Construction sites (manual workers only)": "Construction Sites (Manual Workers)",
    # Add other industry sections similarly
})

# Convert all numeric columns to numeric (handling "-" as NA)
numeric_columns = vacancies_data_clean.columns[3:13]
vacancies_data_clean[numeric_columns] = vacancies_data_clean[numeric_columns].replace("-", pd.NA)
vacancies_data_clean[numeric_columns] = vacancies_data_clean[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Save cleaned data
vacancies_data_clean.to_csv("resources/cleaned_datasets/jobs_vacancies_hk.csv", index=False)

# Display the head of the cleaned data
print(vacancies_data_clean.head())
