# product-web-crawler
A Python-based web crawler to extract product details (name, price, category, SKU, stock) from online stores. Features adjustable crawling depth, data saved in CSV, and a Tkinter GUI to control and view the crawl. Uses requests, BeautifulSoup, and csv for scraping and output generation.
# Product Web Crawler

A Python-based web crawler designed to extract product details like name, price, category, SKU, and stock status from websites. It supports crawling websites recursively up to a specified depth and stores the extracted data in a CSV file.

## Features

- Extracts product information: name, price, category, SKU, and stock status.
- Customizable selectors for various product fields.
- Recursively crawls web pages up to a user-defined depth.
- Saves extracted product details to a CSV file.
- User-friendly GUI using Tkinter for ease of use.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/product-web-crawler.git
Navigate into the project directory:

bash
Copy code
cd product-web-crawler
Install the necessary dependencies:

bash
Copy code
pip install -r requirements.txt
Usage
Run the Python script:

bash
Copy code
python crawler_gui.py
In the GUI, input the starting URL and set the maximum depth for crawling.

Click "Start" to begin crawling and "Stop" to halt the process.

The extracted data will be saved in a CSV file in the output directory.

Configuration
Config.py contains the default settings for the crawler, including:
delay: Time delay between requests.
timeout: Timeout for web requests.
selectors: Custom CSS selectors to identify product details.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Contributions
Feel free to fork this repository, submit issues, or create pull requests. Contributions are welcome!

Acknowledgements
BeautifulSoup for web scraping.
Requests for making HTTP requests.
Tkinter for building the GUI.
Contact
For any questions or suggestions, feel free to open an issue on GitHub or contact me at [bahaeddinmselmi1@gmail.com].
