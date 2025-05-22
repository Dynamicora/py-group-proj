# Install required packages (run once)
# pip install pandas openpyxl requests beautifulsoup4 pytrends

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
from datetime import datetime
import numpy as np

# Step 1: Load C&SD Unemployment and Wage Data (XLSX files)
unemployment = pd.read_excel("unemployment.xlsx", engine='openpyxl')
unemployment['Date'] = pd.to_datetime(unemployment['Date'], format='%Y-%m-%d')
unemployment['Unemployment_Rate'] = pd.to_numeric(unemployment['Unemployment_Rate'], errors='coerce')
unemployment = unemployment[(unemployment['Date'].dt.year >= 2019) & (unemployment['Date'].dt.year <= 2024)].dropna()

wages = pd.read_excel("wages.xlsx", engine='openpyxl')
wages['Date'] = pd.to_datetime(wages['Date'], format='%Y-%m-%d')
wages['Median_Wage'] = pd.to_numeric(wages['Median_Wage'], errors='coerce')
wages = wages[(wages['Date'].dt.year >= 2019) & (wages['Date'].dt.year <= 2024) &
              (wages['Industry'].isin(['Finance', 'Retail', 'Technology']))].dropna()

# Step 2: Scrape JobsDB for Job Vacancies
def scrape_jobsdb(sector):
    url = f"https://hk.jobsdb.com/{sector}?"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    job_count = soup.select_one('.job-count').text
    job_count = int(''.join(filter(str.isdigit, job_count)))
    return pd.DataFrame({'Sector': [sector], 'Job_Vacancies': [job_count], 'Date': [datetime.now().date()]})

vacancies = pd.concat([scrape_jobsdb(sector) for sector in ['finance', 'retail', 'technology']])

# Step 3: Google Trends Data
pytrends = TrendReq()
pytrends.build_payload(kw_list=['unemployment Hong Kong'], timeframe='2019-01-01 2024-12-31')
trends = pytrends.interest_over_time()
trends.reset_index(inplace=True)
trends['Date'] = pd.to_datetime(trends['date'])
trends = trends[['Date', 'unemployment Hong Kong']].rename(columns={'unemployment Hong Kong': 'Search_Interest'})
trends = trends[(trends['Date'].dt.year >= 2019) & (trends['Date'].dt.year <= 2024)]

# Step 4: Merge Datasets
unemployment['Quarter'] = unemployment['Date'].dt.to_period('Q').dt.to_timestamp()
unemployment_quarterly = unemployment.groupby('Quarter', as_index=False)['Unemployment_Rate'].mean()

wages['Quarter'] = wages['Date'].dt.to_period('Q').dt.to_timestamp()
wages_quarterly = wages.groupby(['Quarter', 'Industry'], as_index=False)['Median_Wage'].mean()

vacancies['Quarter'] = vacancies['Date'].dt.to_period('Q').dt.to_timestamp()
vacancies_quarterly = vacancies.groupby(['Quarter', 'Sector'], as_index=False)['Job_Vacancies'].mean()

trends['Quarter'] = trends['Date'].dt.to_period('Q').dt.to_timestamp()
trends_quarterly = trends.groupby('Quarter', as_index=False)['Search_Interest'].mean()

# Combine into one dataset
job_market_data = unemployment_quarterly.merge(wages_quarterly, on='Quarter', how='left') \
    .merge(vacancies_quarterly, on='Quarter', how='left') \
    .merge(trends_quarterly, on='Quarter', how='left').dropna()

# Save cleaned data as CSV for further analysis
job_market_data.to_csv("resources/cleaned_datasets/job_market_data_cleaned.csv", index=False)

# Preview
print(job_market_data.head())
