#!/usr/bin/env bash
# ==============================================================================
# S&P 500 Constituents: Company Name, Location, Founding Year (Sorted by Year)
# ==============================================================================
# Given an S&P 500 CSV URL, this script downloads and parses the constituents data,
# extracts Company Name, Headquarters Location, and Founding Year, and outputs
# them chronologically sorted by founding year.
#
# Default CSV URL:
# https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv
#
# Usage:
#   ./sp500_companies_by_year.sh
#   ./sp500_companies_by_year.sh [CSV_URL]
#   ./sp500_companies_by_year.sh --csv > sorted_sp500.csv
#   ./sp500_companies_by_year.sh --limit 20
# ==============================================================================

set -eo pipefail

DEFAULT_URL="https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv"
CSV_URL="$DEFAULT_URL"
OUTPUT_FORMAT="table"
LIMIT=0
REVERSE=0

# Parse CLI Arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --csv)
      OUTPUT_FORMAT="csv"
      shift
      ;;
    --table)
      OUTPUT_FORMAT="table"
      shift
      ;;
    --reverse|-r)
      REVERSE=1
      shift
      ;;
    --limit|-l)
      LIMIT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS] [CSV_URL]"
      echo ""
      echo "Options:"
      echo "  --table       Output as formatted ASCII table (default)"
      echo "  --csv         Output as CSV (Company Name, Location, Founding Year)"
      echo "  -r, --reverse Sort descending (newest founded companies first)"
      echo "  -l, --limit N Output only the first N records"
      echo "  -h, --help    Show this help message"
      echo ""
      echo "Default URL: $DEFAULT_URL"
      exit 0
      ;;
    http*://*)
      CSV_URL="$1"
      shift
      ;;
    *)
      if [[ -f "$1" ]]; then
        CSV_URL="$1"
      else
        echo "[!] Unknown option or invalid argument: $1" >&2
        echo "Run '$0 --help' for usage." >&2
        exit 1
      fi
      shift
      ;;
  esac
done

# Fetch and process CSV
python3 - "$CSV_URL" "$OUTPUT_FORMAT" "$REVERSE" "$LIMIT" << 'EOF'
import sys
import csv
import urllib.request
import re

csv_source = sys.argv[1]
output_format = sys.argv[2]
reverse_sort = sys.argv[3] == "1"
limit = int(sys.argv[4])

# Fetch data from URL or local file
try:
    if csv_source.startswith("http://") or csv_source.startswith("https://"):
        req = urllib.request.Request(
            csv_source,
            headers={"User-Agent": "Mozilla/5.0 (SP500-Parser/1.0)"}
        )
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
        lines = content.splitlines()
    else:
        with open(csv_source, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
except Exception as e:
    sys.stderr.write(f"[Error] Failed to read CSV from '{csv_source}': {e}\n")
    sys.exit(1)

reader = csv.DictReader(lines)
records = []

for row in reader:
    # 1. Company Name (usually 'Security' or 'Company' or 'Name')
    company = (
        row.get("Security")
        or row.get("Company")
        or row.get("Company Name")
        or row.get("Name")
        or ""
    ).strip()

    # 2. Location (usually 'Headquarters Location' or 'Location')
    location = (
        row.get("Headquarters Location")
        or row.get("Location")
        or row.get("HQ Location")
        or ""
    ).strip()

    # 3. Founding Year (usually 'Founded' or 'Year')
    founded_raw = (
        row.get("Founded")
        or row.get("Founded Year")
        or row.get("Year Founded")
        or row.get("Date Added")
        or ""
    ).strip()

    if not company:
        continue

    # Extract 4-digit years for robust sorting (handling formats like '2013 (1888)' or '1902/1998')
    years = re.findall(r"\b(1\d{3}|20\d{2})\b", founded_raw)
    
    # If multiple years mentioned (e.g. historical vs restructuring), pick historical or primary year
    if len(years) > 1 and "(" in founded_raw:
        # e.g., "2013 (1888)" -> historical foundation was 1888
        inside_paren = re.findall(r"\((1\d{3}|20\d{2})\)", founded_raw)
        sort_year = int(inside_paren[0]) if inside_paren else int(years[0])
    elif years:
        sort_year = int(years[0])
    else:
        sort_year = 9999  # Put unknown years at the end

    records.append({
        "company": company,
        "location": location,
        "founded_raw": founded_raw if founded_raw else "N/A",
        "sort_year": sort_year
    })

# Sort chronologically by founding year, then alphabetically by company name
records.sort(key=lambda r: (r["sort_year"], r["company"]), reverse=reverse_sort)

if limit > 0:
    records = records[:limit]

# Output Results
if output_format == "csv":
    writer = csv.writer(sys.stdout)
    writer.writerow(["Company Name", "Headquarters Location", "Founding Year"])
    for r in records:
        writer.writerow([r["company"], r["location"], r["founded_raw"]])
else:
    # Formatted ASCII Table Output
    sep_line = "=" * 105
    header = f"{'#':<4} | {'COMPANY NAME':<40} | {'HEADQUARTERS LOCATION':<35} | {'FOUNDED':<12}"
    print(sep_line)
    print(header)
    print(sep_line)

    for i, r in enumerate(records, 1):
        comp = (r["company"][:37] + "...") if len(r["company"]) > 40 else r["company"]
        loc = (r["location"][:32] + "...") if len(r["location"]) > 35 else r["location"]
        print(f"{i:<4} | {comp:<40} | {loc:<35} | {r['founded_raw']:<12}")

    print(sep_line)
    print(f"Total Companies: {len(records)} | Source: {csv_source}")
    print(sep_line)
EOF
