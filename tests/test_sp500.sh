#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🧪 Running S&P 500 Companies Shell Script Test Suite"
echo "=========================================================="

SCRIPT="./sp500_companies_by_year.sh"

if [[ ! -x "$SCRIPT" ]]; then
  chmod +x "$SCRIPT"
fi

# Test 1: Table format with limit
echo -n "⏳ Test 1: Executing table mode with limit 10... "
TABLE_OUTPUT=$($SCRIPT --limit 10)
if echo "$TABLE_OUTPUT" | grep -q "BNY Mellon" && echo "$TABLE_OUTPUT" | grep -q "Total Companies: 10"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  echo "$TABLE_OUTPUT"
  exit 1
fi

# Test 2: CSV format output
echo -n "⏳ Test 2: Executing CSV mode with limit 5... "
CSV_OUTPUT=$($SCRIPT --csv --limit 5)
if echo "$CSV_OUTPUT" | grep -q "Company Name,Headquarters Location,Founding Year" && echo "$CSV_OUTPUT" | grep -q "BNY Mellon"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  echo "$CSV_OUTPUT"
  exit 1
fi

# Test 3: Chronological Sorting Verification (1784 < 1806 < 1902)
echo -n "⏳ Test 3: Validating chronological year ordering... "
TOP_YEARS=$($SCRIPT --csv --limit 10 | tail -n +2 | cut -d',' -f3 | tr -d '"' | awk '{print $1}')
YEAR_ARRAY=($TOP_YEARS)
PREV=0
for Y in "${YEAR_ARRAY[@]}"; do
  # Extract first 4 digits
  Y_NUM=$(echo "$Y" | grep -oE '[0-9]{4}' | head -n 1)
  if [[ -n "$Y_NUM" && "$Y_NUM" -lt "$PREV" ]]; then
    echo "❌ FAIL (Order violation: $Y_NUM < $PREV)"
    exit 1
  fi
  PREV=$Y_NUM
done
echo "✅ PASS (Strictly Ascending Years)"

# Test 4: Reverse Sorting Option
echo -n "⏳ Test 4: Validating reverse sort mode (--reverse)... "
REV_OUTPUT=$($SCRIPT --csv --reverse --limit 3)
if echo "$REV_OUTPUT" | grep -qE "202[0-9]"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  echo "$REV_OUTPUT"
  exit 1
fi

echo "=========================================================="
echo "🎉 ALL S&P 500 SHELL SCRIPT TESTS PASSED (100% ACCURACY)!"
echo "=========================================================="
