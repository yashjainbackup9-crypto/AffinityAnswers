# 🚀 AffinityAnswers Assessment Solutions

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Bash](https://img.shields.io/badge/Shell-Bash-4EAA25?logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Tests](https://img.shields.io/badge/Tests-All%20Passed%20(100%25)-emerald)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)

> Comprehensive, production-grade solutions for the **AffinityAnswers** technical evaluation:
> 1. **MDComputers Product Scraper** (`scrape_mdcomputers.py`) — Autonomous web scraper with pagination, stock detection, discount computation, and multi-format export (CSV/JSON/Table).
> 2. **S&P 500 Year Sorter Shell Script** (`sp500_companies_by_year.sh`) — RFC-compliant CSV parser extracting company names, headquarters locations, and sorting chronologically by founding year.

---

## 📁 Repository Structure

```
AffinityAnswers/
├── scrape_mdcomputers.py         # Task 1: Python Scraper CLI for MDComputers
├── sp500_companies_by_year.sh     # Task 2: Executable shell script for S&P 500
├── tests/
│   ├── test_scraper.py           # Unit & live integration test suite for Task 1
│   └── test_sp500.sh             # Automated validation test suite for Task 2
├── requirements.txt              # Python dependencies (requests, beautifulsoup4)
├── LICENSE                       # MIT License
└── README.md                     # Documentation and execution guide
```

---

## 🛠️ Task 1: MDComputers Product Scraper (`scrape_mdcomputers.py`)

### 📋 Overview
A Python CLI tool to scrape live product listings from [MDComputers.in](https://mdcomputers.in) based on any dynamic search query (e.g. `external harddrive`, `rtx 4070`, `mechanical keyboard`).

### ✨ Key Features
* **Field Extraction:** Product Name, Discounted Price, Regular Price / MRP, Discount Percentage, Stock Availability (`In Stock` / `Out of Stock`), Product URL, and Image URL.
* **Pagination Support:** Seamlessly traverses multi-page search results (`--pages N` or `0` for all pages).
* **Multi-Format Export:** Outputs directly to formatted terminal tables, structured **CSV**, or **JSON**.
* **Defensive Scraping:** User-Agent rotation, session pooling, timeout safety, and rate-limiting delays.

### 🚀 Usage Examples

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Search for default query ("external harddrive")
python3 scrape_mdcomputers.py

# 3. Custom search term across 2 pages and export to CSV
python3 scrape_mdcomputers.py "external harddrive" --pages 2 --output results.csv

# 4. Search graphics cards and output raw JSON
python3 scrape_mdcomputers.py "rtx 4070" --json

# 5. Filter for only in-stock products
python3 scrape_mdcomputers.py "mechanical keyboard" --in-stock-only
```

### 📊 Sample Output Table

```text
========================================================================================================================
#   | PRODUCT NAME                                       | PRICE        | MRP          | DISC   | STATUS      
========================================================================================================================
1   | EK-Loop Connect - External USB Cable (1M)          | ₹550         | ₹1,299       | -58%   | In Stock    
2   | Pioneer 240GB Type-C External SSD                  | ₹4,999       | ₹9,900       | -50%   | In Stock    
3   | Pioneer XS03 External SSD 480GB                    | ₹5,999       | ₹10,500      | -43%   | In Stock    
4   | Seagate Expansion 1TB External Hard Drive          | ₹9,140       | ₹10,000      | -9%    | In Stock    
5   | Western Digital Elements 1TB External Hard Drive   | ₹9,299       | ₹14,000      | -34%   | In Stock    
6   | Western Digital My Passport 1TB External Hard D... | ₹9,700       | ₹12,000      | -19%   | In Stock    
7   | Seagate One Touch 1TB External Hard Drive          | ₹9,760       | ₹10,000      | -2%    | In Stock    
8   | Kingston Dual Portable USB Type A and Type C 51... | ₹10,760      | ₹22,000      | -51%   | In Stock    
9   | Western Digital Elements 2TB Portable Hard Drive   | ₹10,990      | ₹13,000      | -15%   | In Stock    
10  | Western Digital My Passport 2TB External Hard D... | ₹11,500      | ₹15,000      | -23%   | In Stock    
========================================================================================================================
Total Products Found: 20
```

---

## 📈 Task 2: S&P 500 Year Sorter Shell Script (`sp500_companies_by_year.sh`)

### 📋 Overview
A shell script that ingests the S&P 500 constituents CSV dataset and outputs **Company Name**, **Headquarters Location**, and **Founding Year** chronologically sorted from oldest to newest.

* **Target CSV URL:** [`https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv`](https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv)

### ✨ Key Features
* **RFC-Compliant CSV Parsing:** Correctly handles quoted fields containing commas (e.g. `"New York City, New York"`, `"Saint Paul, Minnesota"`).
* **Multi-Format Year Extraction:** Resolves complex historical entries like `2017 (1802)` or `2013 (1888)` to ensure true historical chronological ordering.
* **Flexible CLI Options:** Supports `--table` (default), `--csv`, `--limit N`, `--reverse`, and custom CSV URLs.

### 🚀 Usage Examples

```bash
# 1. Make script executable
chmod +x sp500_companies_by_year.sh

# 2. Run with default URL and view formatted table (Top 15 oldest companies)
./sp500_companies_by_year.sh --limit 15

# 3. Export full sorted list to CSV
./sp500_companies_by_year.sh --csv > sp500_sorted_by_year.csv

# 4. View newest founded companies first
./sp500_companies_by_year.sh --reverse --limit 10

# 5. Pass a custom CSV URL or local file
./sp500_companies_by_year.sh "https://custom-domain.com/constituents.csv"
```

### 📊 Sample Output (Chronological Founding Year)

```text
=========================================================================================================
#    | COMPANY NAME                             | HEADQUARTERS LOCATION               | FOUNDED     
=========================================================================================================
1    | BNY Mellon                               | New York City, New York             | 1784        
2    | State Street Corporation                 | Boston, Massachusetts               | 1792        
3    | DuPont                                   | Wilmington, Delaware                | 2017 (1802) 
4    | Colgate-Palmolive                        | New York City, New York             | 1806        
5    | Hartford (The)                           | Hartford, Connecticut               | 1810        
6    | Bunge Global                             | Chesterfield, Missouri              | 1818        
7    | Consolidated Edison                      | New York City, New York             | 1823        
8    | KeyCorp                                  | Cleveland, Ohio                     | 1825        
9    | Citizens Financial Group                 | Providence, Rhode Island            | 1828        
10   | McKesson Corporation                     | Irving, Texas                       | 1833        
11   | Deere & Company                          | Moline, Illinois                    | 1837        
12   | Procter & Gamble                         | Cincinnati, Ohio                    | 1837        
13   | Berkshire Hathaway                       | Omaha, Nebraska                     | 1839        
14   | Stanley Black & Decker                   | New Britain, Connecticut            | 1843        
15   | PNC Financial Services                   | Pittsburgh, Pennsylvania            | 1845        
=========================================================================================================
Total Companies: 15 | Source: https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv
=========================================================================================================
```

---

## 🧪 Automated Testing

Both solutions include automated test suites:

```bash
# Run Task 1 Scraper Tests (Unit & Live Smoke Tests)
python3 -m unittest tests/test_scraper.py

# Run Task 2 Shell Script Tests (Table, CSV, Year Order Validation)
./tests/test_sp500.sh
```

---

## 📄 License
This repository is licensed under the [MIT License](LICENSE).

Made with ❤️ by [TheWebVale](https://thewebvale.com).
