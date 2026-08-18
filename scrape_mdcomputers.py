#!/usr/bin/env python3
"""
MDComputers Product Scraper
===========================
Scrapes product details from MDComputers (https://mdcomputers.in) based on a search term.
Extracts title, current price, original price, discount percentage, stock availability,
image URL, and product URL across single or multiple paginated results.

Usage Examples:
    python scrape_mdcomputers.py "external harddrive"
    python scrape_mdcomputers.py "rtx 4070" --pages 2 --output results.csv
    python scrape_mdcomputers.py "mechanical keyboard" --json --in-stock-only
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


@dataclass
class Product:
    title: str
    price: str
    regular_price: str
    discount: str
    stock_status: str
    product_url: str
    image_url: str


class MDComputersScraper:
    BASE_URL = "https://mdcomputers.in"
    SEARCH_ENDPOINT = "https://mdcomputers.in/?route=product/search"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://mdcomputers.in/",
    }

    def __init__(self, timeout: int = 15, delay: float = 0.5):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.timeout = timeout
        self.delay = delay

    def build_search_url(self, search_term: str, page: int = 1) -> str:
        params = {"route": "product/search", "search": search_term}
        if page > 1:
            params["page"] = str(page)
        return f"{self.BASE_URL}/?{urllib.parse.urlencode(params)}"

    def parse_product_card(self, card) -> Optional[Product]:
        """Parses an individual product card element from the search results page."""
        try:
            # 1. Extract Title and Product URL
            title_el = card.select_one(".product-entities-title a, h3.product-entities-title a, h3 a, h4 a, .product-title a")
            if not title_el:
                return None

            title = title_el.get_text(strip=True)
            product_url = title_el.get("href", "").strip()
            if product_url and not product_url.startswith("http"):
                product_url = urllib.parse.urljoin(self.BASE_URL, product_url)

            # Skip dummy or non-product card links
            if not title or title.startswith("-") or "%" in title:
                # Find direct product title link if first matched badge
                alt_title = card.select_one("h3.product-entities-title a")
                if alt_title:
                    title = alt_title.get_text(strip=True)
                    product_url = alt_title.get("href", "").strip()

            # 2. Extract Image URL
            img_el = card.select_one(".product-image-wrapper img, .product-element-top img, img")
            img_url = ""
            if img_el:
                img_url = img_el.get("data-src") or img_el.get("src") or ""
                if img_url and not img_url.startswith("http"):
                    img_url = urllib.parse.urljoin(self.BASE_URL, img_url)

            # 3. Extract Price & Discount Information
            price_container = card.select_one(".price, .price-box, .product-price")
            raw_price_text = price_container.get_text(" ", strip=True) if price_container else ""

            # Extract currency amounts (e.g. ₹9,900 or 9900)
            amounts = re.findall(r"₹\s*[\d,]+|Rs\.?\s*[\d,]+", raw_price_text)

            price_ins = card.select_one("ins, .price-new, .special-price")
            price_del = card.select_one("del, .price-old, .old-price")

            if price_ins and price_del:
                special_price = price_ins.get_text(strip=True)
                regular_price = price_del.get_text(strip=True)
            elif len(amounts) >= 2:
                # Usually in MDComputers format: [Regular Price, Special Price]
                regular_price = amounts[0]
                special_price = amounts[1]
            elif len(amounts) == 1:
                special_price = amounts[0]
                regular_price = amounts[0]
            else:
                special_price = raw_price_text.strip() or "N/A"
                regular_price = special_price

            # 4. Extract Discount Percentage
            discount_badge = card.select_one(".product-label, .badge-discount, .label-sale, .onsale, .discount-badge")
            discount = discount_badge.get_text(strip=True) if discount_badge else "0%"
            if not discount_badge and regular_price and special_price and regular_price != special_price:
                try:
                    p_orig = float(re.sub(r"[^\d.]", "", regular_price))
                    p_disc = float(re.sub(r"[^\d.]", "", special_price))
                    if p_orig > 0:
                        pct = int(round((1 - p_disc / p_orig) * 100))
                        discount = f"-{pct}%"
                except Exception:
                    discount = "N/A"

            # 5. Extract Stock Status
            card_text_lower = card.get_text().lower()
            is_out_of_stock = bool(card.select(".out-of-stock, .badge-out-of-stock, .stock-out")) or "out of stock" in card_text_lower
            stock_status = "Out of Stock" if is_out_of_stock else "In Stock"

            return Product(
                title=title,
                price=special_price,
                regular_price=regular_price,
                discount=discount,
                stock_status=stock_status,
                product_url=product_url,
                image_url=img_url,
            )
        except Exception as e:
            return None

    def scrape_page(self, search_term: str, page: int = 1) -> (List[Product], bool):
        """Scrapes a single page of results. Returns (products, has_next_page)."""
        url = self.build_search_url(search_term, page)
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[Error] Failed to fetch {url}: {e}", file=sys.stderr)
            return [], False

        soup = BeautifulSoup(resp.text, "html.parser")
        product_cards = soup.select(".product-grid-item, .product-item-container, .product-layout")

        products = []
        seen_urls = set()

        for card in product_cards:
            prod = self.parse_product_card(card)
            if prod and prod.product_url not in seen_urls:
                seen_urls.add(prod.product_url)
                products.append(prod)

        # Check for next page
        next_page = page + 1
        has_next = bool(soup.select(f'a[href*="page={next_page}"]'))

        return products, has_next

    def search(self, search_term: str, max_pages: int = 1, in_stock_only: bool = False) -> List[Product]:
        """Scrapes multiple pages of search results up to max_pages."""
        all_products: List[Product] = []
        page = 1

        print(f"[*] Searching MDComputers for: '{search_term}'...", file=sys.stderr)

        while True:
            print(f"[*] Scraping Page {page}...", file=sys.stderr)
            products, has_next = self.scrape_page(search_term, page)
            if not products:
                print(f"[-] No products found on page {page}.", file=sys.stderr)
                break

            for p in products:
                if in_stock_only and p.stock_status != "In Stock":
                    continue
                all_products.append(p)

            if max_pages > 0 and page >= max_pages:
                break
            if not has_next:
                break

            page += 1
            time.sleep(self.delay)

        return all_products


def print_table(products: List[Product]):
    """Prints a formatted ASCII table of scraped products."""
    if not products:
        print("\n[!] No products to display.")
        return

    print("\n" + "=" * 120)
    print(f"{'#':<3} | {'PRODUCT NAME':<50} | {'PRICE':<12} | {'MRP':<12} | {'DISC':<6} | {'STATUS':<12}")
    print("=" * 120)

    for i, p in enumerate(products, 1):
        title = (p.title[:47] + "...") if len(p.title) > 50 else p.title
        print(f"{i:<3} | {title:<50} | {p.price:<12} | {p.regular_price:<12} | {p.discount:<6} | {p.stock_status:<12}")

    print("=" * 120)
    print(f"Total Products Found: {len(products)}\n")


def export_data(products: List[Product], output_path: str):
    """Exports products to CSV or JSON based on file extension."""
    data = [asdict(p) for p in products]

    if output_path.endswith(".json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[+] Successfully exported {len(products)} products to JSON: {output_path}", file=sys.stderr)
    else:
        # Default to CSV
        fieldnames = ["title", "price", "regular_price", "discount", "stock_status", "product_url", "image_url"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"[+] Successfully exported {len(products)} products to CSV: {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape product listings from MDComputers.in based on a search term."
    )
    parser.add_argument(
        "search",
        type=str,
        nargs="?",
        default="external harddrive",
        help="Search query (e.g. 'external harddrive', 'rtx 4060', 'gaming monitor')",
    )
    parser.add_argument(
        "-p", "--pages",
        type=int,
        default=1,
        help="Maximum pages to scrape (default: 1, set 0 to scrape all available pages)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="",
        help="Output filepath (.csv or .json) to save scraped data",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON to stdout",
    )
    parser.add_argument(
        "--in-stock-only",
        action="store_true",
        help="Filter to include only in-stock products",
    )

    args = parser.parse_args()

    scraper = MDComputersScraper()
    products = scraper.search(
        search_term=args.search,
        max_pages=args.pages,
        in_stock_only=args.in_stock_only,
    )

    if args.json:
        print(json.dumps([asdict(p) for p in products], indent=2, ensure_ascii=False))
    else:
        print_table(products)

    if args.output:
        export_data(products, args.output)


if __name__ == "__main__":
    main()
