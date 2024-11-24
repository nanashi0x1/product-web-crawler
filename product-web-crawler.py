import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
from bs4 import BeautifulSoup
import csv
import time
from typing import Dict
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime
from collections import deque
class Config:
    delay = 1
    timeout = 10
    max_tries = 3
    user_agent = 'Product Crawler'
    output_dir = Path('output')
    selectors = {
        'product_name': ['.product-title', '.product-name', 'h1.title'],
        'price': ['.price', '.product-price', '.current-price'],
        'category': ['.breadcrumb', '.category', '.product-category'],
        'sku': ['.sku', '.product-sku', '.product-code'],
        'stock': ['.stock-status', '.availability', '.inventory']
    }
Config.output_dir.mkdir(exist_ok=True)
class WebCrawler:
    def __init__(self, start_url: str, max_depth: int = 3, gui_update_callback=None):
        self.start_url = start_url.strip()
        self.base_url = f"{urlparse(self.start_url).scheme}://{urlparse(self.start_url).netloc}"
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.user_agent})
        self.max_depth = max_depth
        self.queue = deque([(self.start_url, 0)])
        self.is_running = False
        self.gui_update_callback = gui_update_callback
        self.output_file = None
    def extract_product_info(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        product_data = {
            'url': url,
            'product_name': '',
            'price': '',
            'category': '',
            'sku': '',
            'stock': ''
        }
        for field, selectors in Config.selectors.items():
            for selector in selectors:
                if element := soup.select_one(selector):
                    product_data[field] = element.get_text(strip=True)
                    break
        return product_data
    def process_page(self, url: str):
        try:
            response = self.session.get(url, timeout=Config.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            product_data = self.extract_product_info(soup, url)
            new_urls = {urljoin(self.base_url, link['href']) 
                      for link in soup.find_all('a', href=True) 
                      if link['href'].startswith(('/', 'http')) and 
                         self.base_url in urljoin(self.base_url, link['href'])}
            return product_data, new_urls
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None
    def start_crawling(self):
        self.is_running = True
        self.output_file = Config.output_dir / f'products_{datetime.now():%Y%m%d_%H%M%S}.csv'
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'product_name', 'price', 'category', 'sku', 'stock']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            while self.queue and self.is_running:
                url, depth = self.queue.popleft()
                if depth > self.max_depth or url in self.visited:
                    continue
                self.visited.add(url)
                result = self.process_page(url)
                if result:
                    product_data, new_urls = result
                    if any(product_data.values()):
                        writer.writerow(product_data)
                        if self.gui_update_callback:
                            self.gui_update_callback(product_data)
                    self.queue.extend((link, depth + 1) for link in new_urls if link not in self.visited)
                time.sleep(Config.delay)
        if self.is_running:
            if self.gui_update_callback:
                self.gui_update_callback({"url": "Crawl Completed!"})
    def stop_crawling(self):
        self.is_running = False
class ProductCrawlerGUI:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Product Web Crawler")
        self.app.geometry("1000x700")
        self.crawler = None
        self.setup_gui()
    def setup_gui(self):
        input_frame = ttk.Frame(self.app)
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        ttk.Label(input_frame, text="Start URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(input_frame, text="Max Depth:").pack(side=tk.LEFT, padx=5)
        self.depth_entry = ttk.Entry(input_frame, width=5)
        self.depth_entry.pack(side=tk.LEFT)
        self.depth_entry.insert(0, "3")
        button_frame = ttk.Frame(self.app)
        button_frame.pack(pady=5, fill=tk.X)
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_crawling, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.open_button = ttk.Button(button_frame, text="Open Output", command=self.open_output)
        self.open_button.pack(side=tk.LEFT, padx=5)
        columns = ('URL', 'Product Name', 'Price', 'Category', 'SKU', 'Stock')
        self.treeview = ttk.Treeview(self.app, columns=columns, show='headings')
        for col in columns:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=150)
        y_scroll = ttk.Scrollbar(self.app, orient=tk.VERTICAL, command=self.treeview.yview)
        x_scroll = ttk.Scrollbar(self.app, orient=tk.HORIZONTAL, command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.treeview.pack(fill=tk.BOTH, expand=True, padx=10)

    def update_display(self, product_data: Dict[str, str]):
        if product_data['url'] == "Crawl Completed!":
            messagebox.showinfo("Complete", "Crawling completed!")
            self.stop_button.configure(state=tk.DISABLED)
            self.start_button.configure(state=tk.NORMAL)
        else:
            self.treeview.insert('', 'end', values=(
                product_data['url'],
                product_data['product_name'],
                product_data['price'],
                product_data['category'],
                product_data['sku'],
                product_data['stock']
            ))
    def start_crawling(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        try:
            depth = int(self.depth_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid depth number")
            return
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.crawler = WebCrawler(url, depth, self.update_display)
        threading.Thread(target=self.crawler.start_crawling, daemon=True).start()
    def stop_crawling(self):
        if self.crawler:
            self.crawler.stop_crawling()
            self.stop_button.configure(state=tk.DISABLED)
            self.start_button.configure(state=tk.NORMAL)
    def open_output(self):
        if self.crawler and self.crawler.output_file:
            path = self.crawler.output_file.parent
        else:
            path = Config.output_dir
        filedialog.askopenfilename(initialdir=path)
    def run(self):
        self.app.mainloop()
if __name__ == "__main__":
    app = ProductCrawlerGUI()
    app.run()
