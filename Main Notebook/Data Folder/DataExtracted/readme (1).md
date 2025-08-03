# Real Madrid 2024/25 Player Data Acquisition

This repository contains code and data related to the acquisition of Real Madrid player statistics for the 2024/25 season. Data was scraped from [FBref](https://fbref.com).

## Documentation

- `real_madrid_scrape_24_25.ipynb`: Jupyter Notebook that scrapes match-by-match player stats from FBref.
- `real_madrid_schedule_24_25.csv`: Data set that outlines all of Real Madrid's matches in La Liga and Champions League
- `real_madrid_24_25.csv`: Cleaned dataset combining performance, defensive, and passing stats.
- `README.md`: Project overview and documentation.

## Document Contents
- 776 data entries
- 30 unique players
- 52 matches 


## Features
- Summary Data 
- Opponent and match date are parsed from match URLs.
- Competitions such as La Liga and Champions League are automatically identified. UEFA Super Cup, Supercopa, and Copa del Rey matches were removed
- Columns were arranged for easy analysis with `Date`, `Opponent`, and `Player` first.
- Values for `Date`, `Opponent`, and `Competition` were imputed using the `Match URL` column

## Usage

Open the notebook and run all cells to reproduce the dataset or modify for another team or season.

---

© 2025 Your Name — For academic or personal use only.
