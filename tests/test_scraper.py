#!/usr/bin/env python3
"""
Automated Unit and Integration Tests for MDComputers Scraper
"""

import unittest
from bs4 import BeautifulSoup
from scrape_mdcomputers import MDComputersScraper, Product


SAMPLE_HTML_CARD = """
<div class="product-grid-item">
    <div class="product-element-top">
        <span class="product-label">-25%</span>
        <div class="product-image-wrapper">
            <img src="https://mdcomputers.in/image/test-hdd.jpg" alt="WD 2TB HDD" />
        </div>
    </div>
    <div class="product-details">
        <h3 class="product-entities-title">
            <a href="https://mdcomputers.in/product/wd-2tb-hdd">Western Digital 2TB External HDD</a>
        </h3>
        <div class="price">
            <span class="price-old">₹10,000</span>
            <span class="price-new">₹7,500</span>
        </div>
        <span class="stock-status">In Stock</span>
    </div>
</div>
"""


class TestMDComputersScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = MDComputersScraper()

    def test_build_search_url(self):
        url_p1 = self.scraper.build_search_url("external harddrive", page=1)
        self.assertIn("search=external+harddrive", url_p1)
        self.assertIn("route=product%2Fsearch", url_p1)

        url_p2 = self.scraper.build_search_url("rtx 4070", page=2)
        self.assertIn("page=2", url_p2)
        self.assertIn("search=rtx+4070", url_p2)

    def test_parse_product_card(self):
        soup = BeautifulSoup(SAMPLE_HTML_CARD, "html.parser")
        card = soup.select_one(".product-grid-item")
        product = self.scraper.parse_product_card(card)

        self.assertIsNotNone(product)
        self.assertEqual(product.title, "Western Digital 2TB External HDD")
        self.assertEqual(product.price, "₹7,500")
        self.assertEqual(product.regular_price, "₹10,000")
        self.assertEqual(product.discount, "-25%")
        self.assertEqual(product.stock_status, "In Stock")
        self.assertEqual(product.product_url, "https://mdcomputers.in/product/wd-2tb-hdd")
        self.assertEqual(product.image_url, "https://mdcomputers.in/image/test-hdd.jpg")

    def test_live_search_query(self):
        """Live smoke test verifying MDComputers search endpoint response."""
        products = self.scraper.search("external harddrive", max_pages=1)
        self.assertGreater(len(products), 0, "Should find at least 1 product for 'external harddrive'")
        first = products[0]
        self.assertTrue(len(first.title) > 0)
        self.assertTrue(first.product_url.startswith("https://mdcomputers.in"))


if __name__ == "__main__":
    unittest.main()
