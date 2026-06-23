import requests
from bs4 import BeautifulSoup
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobScraper:
    @staticmethod
    def extract_text_from_url(url: str) -> str:
        """
        Enterprise utility to securely scrape job descriptions from a given URL.
        Includes headers to bypass basic anti-bot protections.
        """
        logging.info(f"Initiating scraping for URL: {url}")
        try:
            # Masking our request to look like a standard enterprise browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML and extract raw text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Target common containers for job descriptions to reduce noise
            main_content = soup.find('main') or soup.find('div', class_=re.compile('job|description|content', re.I)) or soup
            
            # Strip tags and normalize spacing
            extracted_text = main_content.get_text(separator=' ', strip=True)
            clean_text = re.sub(r'\s+', ' ', extracted_text)
            
            logging.info("Successfully scraped and cleaned job description.")
            return clean_text

        except Exception as e:
            logging.error(f"Failed to scrape URL: {e}")
            raise ValueError(f"Could not extract data from the link. Please paste the raw text instead. Error: {str(e)}")